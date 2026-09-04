"""
Subject-Aware Visual Renderer supporting Kroki Mermaid, Pollinations AI, and Matplotlib Fallbacks.
"""

import os
import io
import urllib.parse
import hashlib
import requests
import logging
from typing import Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from src.config import MEDIA_CACHE_DIR

logger = logging.getLogger(__name__)

def render_visual(visual_type: str, visual_spec: str, title: str = "Concept Visual") -> str:
    """
    Render visual based on visual_type and return output image file path.
    Supported types: diagram, illustration, formula, code, timeline, graph, concept_map, comparison_table
    """
    hash_key = hashlib.sha256(f"{visual_type}_{visual_spec}_{title}".encode("utf-8")).hexdigest()[:16]
    output_filename = f"visual_{visual_type}_{hash_key}.png"
    output_path = os.path.join(MEDIA_CACHE_DIR, output_filename)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return output_path

    v_type = visual_type.lower()
    
    try:
        if v_type == "diagram":
            return render_mermaid_diagram(visual_spec, output_path, title)
        elif v_type == "illustration":
            return render_pollinations_illustration(visual_spec, output_path, title)
        elif v_type == "formula":
            return render_matplotlib_formula(visual_spec, output_path, title)
        elif v_type == "code":
            return render_code_card(visual_spec, output_path, title)
        elif v_type == "graph":
            return render_graph(visual_spec, output_path, title)
        else:
            return render_concept_map_card(visual_spec, output_path, title)
    except Exception as e:
        logger.error(f"Visual rendering error for type '{visual_type}': {e}. Generating local card fallback.")
        return render_card_fallback(title, visual_spec, output_path)


def render_mermaid_diagram(mermaid_spec: str, output_path: str, title: str) -> str:
    """Render Mermaid diagram via Kroki endpoint with local Matplotlib fallback."""
    try:
        # Sanitize spec
        spec = mermaid_spec.strip()
        if not (spec.startswith("graph") or spec.startswith("flowchart") or spec.startswith("sequenceDiagram") or spec.startswith("classDiagram")):
            spec = f"flowchart TD\n{spec}"

        url = "https://kroki.io/mermaid/png"
        response = requests.post(url, json={"diagram_source": spec}, timeout=6)
        if response.status_code == 200 and len(response.content) > 100:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
    except Exception as e:
        logger.warning(f"Kroki Mermaid rendering failed: {e}")

    return render_card_fallback(title, mermaid_spec, output_path)


def render_pollinations_illustration(prompt: str, output_path: str, title: str) -> str:
    """Render image illustration via Pollinations AI with local fallback."""
    try:
        encoded_prompt = urllib.parse.quote(f"Educational illustration of {prompt}, high quality, clean diagram style")
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"
        response = requests.get(url, timeout=8)
        if response.status_code == 200 and len(response.content) > 500:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
    except Exception as e:
        logger.warning(f"Pollinations AI rendering failed: {e}")

    return render_card_fallback(title, prompt, output_path)


def render_matplotlib_formula(formula_spec: str, output_path: str, title: str) -> str:
    """Render mathematical formula card using Matplotlib LaTeX."""
    fig, ax = plt.subplots(figsize=(8, 4), facecolor='#1E293B')
    ax.set_facecolor('#1E293B')
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.85, title, color='#F8FAFC', fontsize=18, fontweight='bold', ha='center', va='center')
    
    # Formula text or raw math
    clean_formula = formula_spec.strip().replace("\n", "  ")
    if not clean_formula.startswith("$"):
        clean_formula = f"${clean_formula}$"

    try:
        ax.text(0.5, 0.45, clean_formula, color='#38BDF8', fontsize=24, ha='center', va='center')
    except Exception:
        # Fallback to plain text if LaTeX fails
        ax.text(0.5, 0.45, formula_spec, color='#38BDF8', fontsize=18, ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


def render_code_card(code_spec: str, output_path: str, title: str) -> str:
    """Render syntax code snippet card using Matplotlib."""
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0F172A')
    ax.set_facecolor('#1E293B')
    ax.axis('off')

    ax.text(0.05, 0.90, f"// Code: {title}", color='#A855F7', fontsize=14, fontweight='bold', family='monospace')
    ax.text(0.05, 0.45, code_spec, color='#F1F5F9', fontsize=12, family='monospace', va='center', bbox=dict(boxstyle="round,pad=0.5", fc="#1E293B", ec="#3B82F6", lw=1.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


def render_graph(graph_spec: str, output_path: str, title: str) -> str:
    """Render coordinate or bar plot using Matplotlib."""
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0F172A')
    ax.set_facecolor('#1E293B')

    ax.set_title(title, color='#F8FAFC', fontsize=16, fontweight='bold', pad=12)
    ax.tick_params(colors='#94A3B8')
    for spine in ax.spines.values():
        spine.set_color('#334155')

    # Example standard plot for physics/math if V=I*R
    import numpy as np
    x = np.linspace(0, 10, 50)
    y1 = 2 * x # R=2 Ohm (V = 2I)
    y2 = 4 * x # R=4 Ohm (V = 4I)

    ax.plot(x, y1, color='#38BDF8', linewidth=2.5, label='Resistance R = 2 Ω')
    ax.plot(x, y2, color='#F43F5E', linewidth=2.5, label='Resistance R = 4 Ω')
    ax.set_xlabel('Current I (Amperes)', color='#CBD5E1')
    ax.set_ylabel('Voltage V (Volts)', color='#CBD5E1')
    ax.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC')
    ax.grid(True, linestyle='--', alpha=0.3, color='#475569')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


def render_concept_map_card(spec: str, output_path: str, title: str) -> str:
    """Render structured concept map / bullet list card."""
    return render_card_fallback(title, spec, output_path)


def render_card_fallback(title: str, text: str, output_path: str) -> str:
    """Local Pillow/Matplotlib visual card generator."""
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0F172A')
    ax.set_facecolor('#1E293B')
    ax.axis('off')

    # Header title
    ax.text(0.5, 0.85, title, color='#38BDF8', fontsize=18, fontweight='bold', ha='center', va='center')
    
    # Body text wrapped
    wrapped_text = "\n".join([text[i:i+55] for i in range(0, len(text), 55)])
    if len(wrapped_text) > 300:
        wrapped_text = wrapped_text[:300] + "..."

    ax.text(0.5, 0.45, wrapped_text, color='#F8FAFC', fontsize=13, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.8", fc="#1E293B", ec="#6366F1", lw=1.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path
