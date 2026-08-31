from typing import Dict, List, Set

# Visual types supported by the engine
SUPPORTED_VISUAL_TYPES = [
    "formula",
    "diagram",
    "flowchart",
    "graph",
    "timeline",
    "code_execution",
    "architecture"
]

# Domain and keyword taxonomy mappings
TAXONOMY_KEYWORDS: Dict[str, List[str]] = {
    "formula": [
        "law", "equation", "formula", "theorem", "relativity", "calculus",
        "derivative", "integral", "newton", "ohm", "coulomb", "einstein",
        "pythagorean", "kinematics", "gravitation", "thermodynamics", "algebraic",
        "equilibrium", "conservation", "momentum", "f = ma", "v = ir", "e = mc^2",
        "kepler", "maxwell", "bernoulli", "quadratic equation", "force", "voltage",
        "resistance", "current", "velocity", "acceleration"
    ],
    "graph": [
        "plot", "graph", "curve", "parabola", "function", "y =", "f(x)",
        "coordinates", "cartesian", "slope", "intercept", "quadratic", "linear",
        "exponential", "sine", "cosine", "logarithmic", "distribution", "polynomial",
        "scatter", "trend", "histogram", "growth", "decay", "y = x^2", "x^2", "x²"
    ],
    "code_execution": [
        "loop", "for loop", "while loop", "code", "syntax", "execution", "trace",
        "iteration", "python", "javascript", "variable", "recursion", "array indexing",
        "function call", "list comprehension", "pointer", "stack frame", "memory state",
        "debugging", "conditional execution", "string manipulation"
    ],
    "flowchart": [
        "binary search", "algorithm", "flowchart", "decision tree", "decision", "step-by-step",
        "process flow", "branching", "if-else", "search logic", "sorting algorithm",
        "breadth-first", "depth-first", "control flow", "procedure", "condition",
        "workflow", "finite state"
    ],
    "architecture": [
        "pipeline", "architecture", "machine learning pipeline", "ml pipeline",
        "system design", "microservices", "infrastructure", "client-server",
        "data pipeline", "etl", "model training", "serving", "ingestion", "database",
        "component", "cloud architecture", "layers", "api gateway"
    ],
    "timeline": [
        "timeline", "history", "revolution", "french revolution", "world war",
        "chronology", "century", "era", "dynasty", "historical event", "chronological",
        "evolution of", "milestones", "treaty", "renaissance", "period", "ages"
    ],
    "diagram": [
        "diagram", "photosynthesis", "cell", "anatomy", "biological", "chloroplast",
        "plant", "animal", "organism", "solar system", "ecosystem", "respiration",
        "water cycle", "parts of", "structure of", "schematic", "cross-section",
        "internal structure", "food web"
    ]
}

# Standard multi-visual associations
SECONDARY_VISUAL_MAP: Dict[str, List[str]] = {
    "ohm's law": ["diagram"],
    "ohms law": ["diagram"],
    "newton's second law": ["diagram"],
    "newton's law": ["diagram"],
    "photosynthesis": ["flowchart"],
    "binary search": ["code_execution"],
    "python for loop": ["flowchart"],
    "python loop": ["flowchart"],
    "machine learning pipeline": ["flowchart"],
    "ml pipeline": ["flowchart"],
    "french revolution": ["flowchart"],
    "french revolution timeline": ["flowchart"],
    "y = x^2": ["formula"],
    "y = x²": ["formula"],
    "quadratic": ["formula"]
}
