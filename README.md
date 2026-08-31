# AI-Teacher Visual Explanation Engine

A standalone, deterministic, and modular Visual Explanation Engine built with Python and FastAPI for the AI Teacher hackathon.

The engine analyzes educational topics and concepts, automatically selects the optimal visual representation type, generates structured visual specifications, and renders crisp vector and interactive outputs (SVG, KaTeX/LaTeX, Plotly, Pygments syntax highlighting, and responsive HTML).

---

## ? Quick Start for Teammates (Fresh Clone)

### 1. Clone & Enter Directory
```bash
git clone <repo-url>
cd AI-Teacher-Visual-Engine
```

### 2. (Optional) Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Automated Verification & Benchmarks
```bash
# Run pytest test suite (21 unit & integration tests)
pytest -v

# Run all 8 curriculum benchmark examples
python examples/run_examples.py
```

### 5. Start the FastAPI Server
```bash
python run.py
```
- **Live API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Healthcheck**: `http://127.0.0.1:8000/health`

---

## ?? What Files Are in This Repository?

Every file in this repository is completely self-contained, clean, and safe to share with your hackathon team:

```
AI-Teacher-Visual-Engine/
??? app/
?   ??? config.py                   # Central settings, URLs, static directory paths
?   ??? main.py                     # FastAPI application setup, CORS, static mounts
?   ??? models/
?   ?   ??? request.py              # VisualRequest (topic, concept, level, language, context, etc.)
?   ?   ??? response.py             # VisualResponse, VisualItem, SelectorMetadata
?   ?   ??? specs/                  # Strongly-typed schemas for all 7 visual types
?   ??? selector/
?   ?   ??? base.py                 # Abstract BaseVisualSelector interface & SelectorResult
?   ?   ??? taxonomy.py             # Domain keywords & multi-visual mappings
?   ?   ??? rules.py                # Deterministic pattern matching & scoring engine
?   ?   ??? rule_selector.py        # RuleBasedVisualSelector with confidence & safe fallback
?   ?   ??? llm_selector.py         # Pluggable LLM interface extension point
?   ??? generators/
?   ?   ??? base.py                 # Abstract BaseSpecGenerator interface
?   ?   ??? knowledge_base.py       # High-fidelity curriculum specs for standard topics
?   ?   ??? dynamic_builder.py      # Algorithmic generator for arbitrary concepts
?   ?   ??? registry.py             # Central spec generator dispatcher
?   ??? renderers/
?   ?   ??? base.py                 # Abstract BaseRenderer & RenderedOutput
?   ?   ??? diagram_renderer.py     # Pure vector SVG/HTML labelled diagram renderer
?   ?   ??? flowchart_renderer.py   # SVG Flowchart & decision tree renderer (with side-margin routing)
?   ?   ??? formula_renderer.py     # KaTeX / MathJax compatible LaTeX card renderer
?   ?   ??? graph_renderer.py       # Plotly interactive coordinate graph renderer
?   ?   ??? timeline_renderer.py    # SVG Chronological milestone timeline renderer
?   ?   ??? code_renderer.py        # Pygments code highlighting + execution trace stepper
?   ?   ??? architecture_renderer.py# SVG Multi-tier system architecture renderer
?   ?   ??? registry.py             # Central renderer registry
?   ??? services/
?   ?   ??? storage_service.py      # Saves .html/.svg artifacts & generates embed URLs
?   ?   ??? engine_service.py       # Orchestrates selector -> generator -> renderer pipeline
?   ??? api/v1/
?       ??? routes.py               # POST /generate-visual, POST /select-type, GET /visual-types, GET /examples
?       ??? render_views.py         # GET /visuals/{visual_id} standalone iframe viewer
??? examples/                       # 8 Benchmark JSON payloads & test runner (run_examples.py)
??? static/                         # Generated standalone HTML/SVG visual artifacts
??? tests/                          # Automated Pytest suite (21 passing tests)
??? pytest.ini                      # Pytest configuration
??? conftest.py                     # Test path bootstrap
??? requirements.txt                # Lightweight, pinned dependencies
??? run.py                          # Server launch script
??? README.md                       # Complete documentation & backend integration guide
```

---

## ?? Supported Visual Modalities

| Visual Type | Description | Render Format |
|---|---|---|
| `formula` | LaTeX equations, KaTeX math cards, variable legends with SI units, derivation steps | KaTeX / MathJax HTML |
| `diagram` | Vector anatomical, physical, circuit, and structural diagrams with callouts and badges | Clean Responsive SVG / HTML |
| `flowchart` | Algorithmic decision trees, conditions, branch labels, and iteration loops | Clean Responsive SVG / HTML |
| `graph` | Plotly interactive function curves, coordinate grids, and annotated extreme points | Plotly JSON + Interactive HTML |
| `timeline` | Chronological event pipeline with milestone nodes, dates, tags, and category chips | Clean Responsive SVG / HTML |
| `code_execution` | Pygments syntax-highlighted code + line-by-line variable memory trace table | Pygments HTML + State Table |
| `architecture` | Multi-tier system architectures, ML pipelines, and directed data communication flows | Clean Responsive SVG / HTML |

---

## ?? API Reference & Integration

### `POST /generate-visual`
The primary endpoint to call from another backend (chatbot, orchestrator, or frontend).

#### Request Body
```json
{
  "topic": "Physics",
  "concept": "Ohm's Law",
  "level": "intermediate",
  "language": "English",
  "lesson_context": "Explain the relationship between voltage, current, and resistance.",
  "include_secondary": true,
  "visual_type_override": null
}
```

#### Response Body
```json
{
  "visual_type": "formula",
  "title": "Ohm's Law (V = I ? R)",
  "explanation": "Current is directly proportional to voltage and inversely proportional to resistance.",
  "selector_metadata": {
    "confidence": 0.98,
    "reason": "Ohm's Law expresses the direct mathematical relation V = I ? R alongside circuit schematics.",
    "suggested_visual_types": ["formula", "diagram", "flowchart", "graph", "timeline", "code_execution", "architecture"]
  },
  "visual_data": {
    "format": "katex",
    "latex": "V = I \cdot R",
    "rendered_html": "<div class="visual-card formula-card">...</div>",
    "spec": { ... }
  },
  "visual_url": "http://127.0.0.1:8000/visuals/vis_ohm_s_law_formula_0b333f.html",
  "secondary_visuals": [
    {
      "visual_type": "diagram",
      "title": "Ohm's Law DC Circuit & Triangle",
      "explanation": "Schematic of a simple closed DC circuit with voltage source, current loop, and resistor.",
      "visual_data": { "format": "svg", "raw_svg": "<svg>...</svg>", "rendered_html": "..." },
      "visual_url": "http://127.0.0.1:8000/visuals/vis_ohm_s_law_diagram_6e89cf.html"
    }
  ]
}
```

---

### Backend Integration Examples

#### Node.js (Axios)
```javascript
const axios = require('axios');

async function getVisual(topic, concept, context) {
  const res = await axios.post('http://127.0.0.1:8000/generate-visual', {
    topic,
    concept,
    lesson_context: context,
    include_secondary: true
  });
  return {
    primaryUrl: res.data.visual_url,
    secondaryUrls: res.data.secondary_visuals.map(s => s.visual_url),
    explanation: res.data.explanation
  };
}
```

#### Python (Requests / HTTPX)
```python
import requests

def get_visual(topic: str, concept: str) -> dict:
    resp = requests.post(
        "http://127.0.0.1:8000/generate-visual",
        json={"topic": topic, "concept": concept, "include_secondary": True}
    )
    return resp.json()
```

#### Frontend Iframe Embed
```html
<iframe
  src="http://127.0.0.1:8000/visuals/vis_photosynthesis_diagram_6dc6b8.html"
  width="100%"
  height="520px"
  frameborder="0"
  style="border-radius: 12px; border: 1px solid #e2e8f0;">
</iframe>
```
