import re
from typing import Dict, List, Tuple
from app.selector.taxonomy import TAXONOMY_KEYWORDS, SECONDARY_VISUAL_MAP, SUPPORTED_VISUAL_TYPES

class RuleEngine:
    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.lower().strip())

    @staticmethod
    def match_exact_concept(concept: str) -> Tuple[str, List[str], float, str]:
        c = RuleEngine.normalize(concept)
        
        # 1. Newton's Laws
        if "newton" in c and ("second" in c or "2nd" in c or "law" in c):
            return "formula", ["diagram"], 0.98, "Newton's Second Law is a fundamental mathematical law (F = m · a) best represented with algebraic formulas and vector diagrams."

        # 2. Ohm's Law
        if "ohm" in c and "law" in c:
            return "formula", ["diagram"], 0.98, "Ohm's Law expresses the direct mathematical relation V = I · R alongside circuit schematics."

        # 3. Photosynthesis
        if "photosynthesis" in c:
            return "diagram", ["flowchart"], 0.97, "Photosynthesis involves cellular structures (chloroplast, thylakoid) best illustrated via anatomical biological diagrams and reaction flows."

        # 4. Binary Search
        if "binary search" in c:
            return "flowchart", ["code_execution"], 0.97, "Binary Search is a divide-and-conquer algorithm with decision branches (low, mid, high) best shown via flowcharts."

        # 5. Python for loop / Loops
        if ("for loop" in c or "python loop" in c or "loop" in c) and ("python" in c or "code" in c or "for" in c):
            return "code_execution", ["flowchart"], 0.97, "Python for loop is an imperative programming construct best explained through code syntax and step-by-step state traces."

        # 6. Machine Learning Pipeline
        if "machine learning" in c or "ml pipeline" in c or ("pipeline" in c and "data" in c):
            return "architecture", ["flowchart"], 0.96, "Machine Learning pipelines represent multi-tier system components (Ingestion, Prep, Train, Registry, Serving) best depicted as architectural block diagrams."

        # 7. French Revolution / Timeline
        if "french revolution" in c or ("revolution" in c and "timeline" in c) or ("history" in c and "timeline" in c):
            return "timeline", ["flowchart"], 0.97, "Historical revolutions follow chronological event milestones best visualized as interactive timelines."

        # 8. y = x^2 / Function graphs
        if "y = x" in c or "y=x" in c or "x^2" in c or "x²" in c or "parabola" in c or "quadratic function" in c:
            return "graph", ["formula"], 0.98, "Mathematical functions like y = x² represent coordinate curves and geometric properties best plotted on Cartesian graphs."

        return None

    @staticmethod
    def score_visual_types(topic: str, concept: str, context: str) -> Dict[str, float]:
        combined = f"{RuleEngine.normalize(topic)} {RuleEngine.normalize(concept)} {RuleEngine.normalize(context)}"
        scores: Dict[str, float] = {vt: 0.0 for vt in SUPPORTED_VISUAL_TYPES}

        for vtype, keywords in TAXONOMY_KEYWORDS.items():
            for kw in keywords:
                if kw in combined:
                    weight = 0.35 if kw in RuleEngine.normalize(concept) else 0.15
                    if len(kw.split()) > 1:
                        weight += 0.2  # Bonus for multi-word exact match
                    scores[vtype] += weight

        # Special syntactic boosters
        if re.search(r'\b[a-zA-Z]\s*=\s*[a-zA-Z0-9]', combined):
            scores["formula"] += 0.3
            scores["graph"] += 0.2

        if re.search(r'\b(def|for|while|class|import|return)\b', combined):
            scores["code_execution"] += 0.4

        if re.search(r'\b(1[789]\d\d|20\d\d|century|bce|ce|ad)\b', combined):
            scores["timeline"] += 0.4

        return scores
