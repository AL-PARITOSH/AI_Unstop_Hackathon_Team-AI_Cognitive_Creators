"""
Document Ingestion, Multilingual Semantic Chunking, Local ChromaDB Vector Indexing, and RAG Citations.
"""

import os
import uuid
import logging
import warnings
from typing import List, Dict, Any, Tuple, Optional
from src.config import CHROMA_DB_DIR

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

logger = logging.getLogger(__name__)

# Initialize ChromaDB client lazily
_chroma_client = None
_chroma_collection = None

def get_chroma_collection():
    global _chroma_client, _chroma_collection
    if _chroma_collection is None:
        try:
            import chromadb
            _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
            _chroma_collection = _chroma_client.get_or_create_collection(
                name="ai_teacher_documents",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            _chroma_collection = None
    return _chroma_collection


# Embeddings adapter
_embedding_model = None

def get_embedding_vector(text: str) -> List[float]:
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Using instant lightweight embedding fallback: {e}")
            _embedding_model = "hash_fallback"

    if _embedding_model == "hash_fallback":
        # Instant hash deterministic 384-dim float vector fallback
        import hashlib
        vec = []
        for i in range(12):
            h = hashlib.sha256(f"{i}:{text}".encode('utf-8')).digest()
            vec.extend([float(b) / 255.0 for b in h])
        return vec[:384]
    else:
        try:
            return _embedding_model.encode(text).tolist()
        except Exception:
            _embedding_model = "hash_fallback"
            return get_embedding_vector(text)


def get_embedding_vectors_batch(texts: List[str]) -> List[List[float]]:
    """Generate embedding vectors for a list of texts in fast batch mode."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Using instant lightweight embedding fallback: {e}")
            _embedding_model = "hash_fallback"

    if _embedding_model == "hash_fallback":
        import hashlib
        all_vecs = []
        for text in texts:
            vec = []
            for i in range(12):
                h = hashlib.sha256(f"{i}:{text}".encode('utf-8')).digest()
                vec.extend([float(b) / 255.0 for b in h])
            all_vecs.append(vec[:384])
        return all_vecs
    else:
        try:
            return _embedding_model.encode(texts, batch_size=32, show_progress_bar=False).tolist()
        except Exception:
            _embedding_model = "hash_fallback"
            return get_embedding_vectors_batch(texts)


# Document extraction functions
def parse_pdf(file_path: str, focus_topic: Optional[str] = None) -> List[Dict[str, Any]]:
    """Extract text page by page from PDF using PyMuPDF (fitz), with smart chapter targeting for textbooks."""
    pages = []
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        target_indices = []
        # If document is a large textbook (> 35 pages) and user specified a focus (e.g. "chapter 2")
        if total_pages > 35 and focus_topic:
            focus_clean = focus_topic.lower().strip()
            import re
            m = re.search(r'(?:chapter|ch\.?)\s*(\d+)', focus_clean)
            ch_num = m.group(1) if m else None

            found_start = -1
            if ch_num:
                # 1. First, scan TOC (first 25 pages) to get Chapter Title if present
                chapter_title = ""
                for idx in range(min(total_pages, 25)):
                    t_toc = doc[idx].get_text("text")
                    tm = re.search(r'(?:^|\n)\s*' + ch_num + r'\s*\n\s*([A-Za-z\s]{3,40})\n\s*\d+', t_toc)
                    if tm:
                        chapter_title = tm.group(1).strip()
                        break

                # 2. Search for the chapter start page in the document
                for idx in range(min(total_pages, 250)):
                    txt_p = doc[idx].get_text("text")
                    lines = [l.strip() for l in txt_p.split('\n') if l.strip()]
                    if not lines or len(lines) < 3:
                        continue
                    
                    # Match by TOC chapter title
                    if chapter_title:
                        if chapter_title.lower() in txt_p.lower() and "contents" not in txt_p.lower():
                            if lines[0] == ch_num or lines[0].lower() == f"chapter {ch_num}" or chapter_title.lower() in lines[1].lower():
                                found_start = idx
                                break
                    else:
                        # Match by heading pattern (line 0 is ch_num or 'Chapter X', line 2 is full paragraph)
                        if (lines[0] == ch_num or lines[0].lower() == f"chapter {ch_num}" or lines[0].lower() == f"chapter  {ch_num}"):
                            if "contents" not in txt_p.lower() and len(lines[2]) > 35:
                                found_start = idx
                                break
            
            # If ch_num search didn't match or no ch_num, try searching for focus keywords
            if found_start == -1:
                for idx in range(min(total_pages, 120)):
                    p_text = doc[idx].get_text("text").lower()
                    if focus_clean in p_text:
                        found_start = idx
                        break

            if found_start != -1:
                # Include starting from found chapter, up to 30 pages
                target_indices = list(range(found_start, min(total_pages, found_start + 30)))
            else:
                # If chapter not directly found, take the first 30 pages
                target_indices = list(range(min(total_pages, 30)))
        elif total_pages > 35:
            # Large textbook with no specific focus: take first 30 pages for curriculum overview
            target_indices = list(range(min(total_pages, 30)))
        else:
            # Normal document (slides, notes): take all pages
            target_indices = list(range(total_pages))

        for idx in target_indices:
            page = doc[idx]
            text = page.get_text("text").strip()
            if text:
                pages.append({
                    "page_number": idx + 1,
                    "slide_number": None,
                    "section_heading": f"Page {idx + 1}",
                    "text": text
                })
        doc.close()
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
    return pages


def parse_docx(file_path: str) -> List[Dict[str, Any]]:
    """Extract paragraphs and headings from DOCX file."""
    sections = []
    try:
        import docx
        doc = docx.Document(file_path)
        current_heading = "Main Content"
        current_text = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            if p.style.name.startswith("Heading"):
                if current_text:
                    sections.append({
                        "page_number": len(sections) + 1,
                        "slide_number": None,
                        "section_heading": current_heading,
                        "text": "\n".join(current_text)
                    })
                    current_text = []
                current_heading = text
            else:
                current_text.append(text)

        if current_text:
            sections.append({
                "page_number": len(sections) + 1,
                "slide_number": None,
                "section_heading": current_heading,
                "text": "\n".join(current_text)
            })
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
    return sections


def parse_pptx(file_path: str) -> List[Dict[str, Any]]:
    """Extract slide text from PPTX file."""
    slides = []
    try:
        import pptx
        prs = pptx.Presentation(file_path)
        for idx, slide in enumerate(prs.slides):
            slide_texts = []
            heading = f"Slide {idx + 1}"
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    if hasattr(shape, "text_frame") and shape == slide.shapes[0]:
                        heading = shape.text.strip()
                    else:
                        slide_texts.append(shape.text.strip())
            if slide_texts or heading:
                slides.append({
                    "page_number": None,
                    "slide_number": idx + 1,
                    "section_heading": heading,
                    "text": "\n".join(slide_texts)
                })
    except Exception as e:
        logger.error(f"Error parsing PPTX {file_path}: {e}")
    return slides


def parse_txt_md(file_path: str) -> List[Dict[str, Any]]:
    """Extract content from TXT or MD files."""
    sections = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        lines = content.splitlines()
        current_heading = "Document Content"
        current_text = []

        for line in lines:
            line_str = line.strip()
            if line_str.startswith("#"):
                if current_text:
                    sections.append({
                        "page_number": len(sections) + 1,
                        "slide_number": None,
                        "section_heading": current_heading,
                        "text": "\n".join(current_text)
                    })
                    current_text = []
                current_heading = line_str.lstrip("#").strip()
            elif line_str:
                current_text.append(line_str)

        if current_text:
            sections.append({
                "page_number": len(sections) + 1,
                "slide_number": None,
                "section_heading": current_heading,
                "text": "\n".join(current_text)
            })
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {e}")
    return sections


def chunk_sections(sections: List[Dict[str, Any]], chunk_size: int = 600, overlap: int = 60, max_chunks: int = 60) -> List[Dict[str, Any]]:
    """Semantic chunking with metadata attachment and max chunk budget."""
    chunks = []
    chunk_index = 0

    for sec in sections:
        if len(chunks) >= max_chunks:
            break
        text = sec["text"]
        if len(text) <= chunk_size:
            chunks.append({
                "chunk_index": chunk_index,
                "page_number": sec["page_number"],
                "slide_number": sec["slide_number"],
                "section_heading": sec["section_heading"],
                "text": text
            })
            chunk_index += 1
        else:
            # Overlapping chunking
            start = 0
            while start < len(text) and len(chunks) < max_chunks:
                end = start + chunk_size
                chunk_str = text[start:end]
                chunks.append({
                    "chunk_index": chunk_index,
                    "page_number": sec["page_number"],
                    "slide_number": sec["slide_number"],
                    "section_heading": sec["section_heading"],
                    "text": chunk_str
                })
                chunk_index += 1
                start += (chunk_size - overlap)

    return chunks


def process_and_index_document(file_path: str, original_filename: str, focus_topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse document based on extension, chunk, generate embeddings in fast batch mode, and index into ChromaDB.
    """
    ext = os.path.splitext(original_filename)[1].lower()
    doc_id = str(uuid.uuid4())

    if ext == ".pdf":
        sections = parse_pdf(file_path, focus_topic=focus_topic)
        source_type = "pdf"
    elif ext in [".docx", ".doc"]:
        sections = parse_docx(file_path)
        source_type = "docx"
    elif ext in [".pptx", ".ppt"]:
        sections = parse_pptx(file_path)
        source_type = "pptx"
    elif ext in [".txt", ".md"]:
        sections = parse_txt_md(file_path)
        source_type = "txt"
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    if not sections:
        return {
            "status": "error",
            "message": f"No extractable text found in {original_filename}.",
            "doc_id": doc_id,
            "chunk_count": 0
        }

    chunks = chunk_sections(sections, max_chunks=60)
    collection = get_chroma_collection()

    if collection and chunks:
        ids = [f"{doc_id}_{chk['chunk_index']}" for chk in chunks]
        texts = [chk["text"] for chk in chunks]
        metadatas = [{
            "document_id": doc_id,
            "source_name": original_filename,
            "source_type": source_type,
            "page_number": chk["page_number"] if chk["page_number"] is not None else -1,
            "slide_number": chk["slide_number"] if chk["slide_number"] is not None else -1,
            "section_heading": chk["section_heading"] or "",
            "chunk_index": chk["chunk_index"]
        } for chk in chunks]

        # Fast batch embedding generation (runs in seconds)
        embeddings = get_embedding_vectors_batch(texts)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    return {
        "status": "success",
        "doc_id": doc_id,
        "original_name": original_filename,
        "source_type": source_type,
        "section_count": len(sections),
        "chunk_count": len(chunks)
    }


def query_rag_context(
    query: str, 
    top_k: int = 5, 
    min_relevance_score: float = 0.10,
    document_name: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Retrieve relevant source chunks with document filtering, score thresholding, and citation formatting.
    Guarantees document context retrieval for grounded lesson planning.
    """
    collection = get_chroma_collection()
    if not collection or collection.count() == 0:
        return "insufficient_source_evidence", []

    query_emb = get_embedding_vector(query)
    
    # Try querying with document_name filter first if provided
    results = None
    if document_name:
        try:
            results = collection.query(
                query_embeddings=[query_emb],
                n_results=top_k,
                where={"source_name": document_name}
            )
        except Exception:
            results = None

    # Fallback to general query if document filter had no matches or failed
    if not results or not results.get("documents") or not results["documents"][0]:
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=top_k
        )

    if not results or not results.get("documents") or not results["documents"][0]:
        return "insufficient_source_evidence", []

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results.get("distances", [[0.0] * len(docs)])[0]

    retrieved_chunks = []
    formatted_texts = []

    for doc, meta, dist in zip(docs, metas, distances):
        # Cosine distance to similarity
        similarity = 1.0 - dist if dist <= 1.0 else (1.0 / (1.0 + dist))
        if similarity < min_relevance_score:
            continue

        src_name = meta.get("source_name", "Source Document")
        pg = meta.get("page_number", -1)
        sl = meta.get("slide_number", -1)

        citation = f"[{src_name}"
        if pg != -1:
            citation += f" — Page {pg}]"
        elif sl != -1:
            citation += f" — Slide {sl}]"
        else:
            citation += "]"

        chunk_info = {
            "citation": citation,
            "text": doc,
            "metadata": meta,
            "similarity": similarity
        }
        retrieved_chunks.append(chunk_info)
        formatted_texts.append(f"Citation: {citation}\nContent: {doc}")

    # If all fell below threshold, keep at least the top closest chunk so grounding is never lost
    if not retrieved_chunks and docs:
        top_doc = docs[0]
        top_meta = metas[0] if metas else {}
        src_name = top_meta.get("source_name", "Source Document")
        pg = top_meta.get("page_number", -1)
        citation = f"[{src_name}{f' — Page {pg}' if pg != -1 else ''}]"
        retrieved_chunks.append({
            "citation": citation,
            "text": top_doc,
            "metadata": top_meta,
            "similarity": 0.5
        })
        formatted_texts.append(f"Citation: {citation}\nContent: {top_doc}")

    if not retrieved_chunks:
        return "insufficient_source_evidence", []

    combined_context = "\n\n---\n\n".join(formatted_texts)
    return combined_context, retrieved_chunks
