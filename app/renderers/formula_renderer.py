import html
from app.models.specs.formula import FormulaSpec
from app.renderers.base import BaseRenderer, RenderedOutput

class FormulaRenderer(BaseRenderer):
    def render(self, spec: FormulaSpec) -> RenderedOutput:
        disp_latex = spec.display_latex or spec.latex

        # Variable cards HTML
        vars_html_list = []
        for v in spec.variables:
            unit_badge = f'<span style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:600; margin-left:6px;">{html.escape(v.unit)}</span>' if v.unit else ''
            desc = f'<div style="font-size:12px; color:#64748b; margin-top:2px;">{html.escape(v.description)}</div>' if v.description else ''
            vars_html_list.append(f'''
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px;">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <span style="font-family:serif; font-size:16px; font-weight:700; color:#1e293b;">{html.escape(v.symbol)}</span>
                    <span style="font-size:13px; font-weight:600; color:#334155;">{html.escape(v.name)} {unit_badge}</span>
                </div>
                {desc}
            </div>
            ''')
        vars_section = "".join(vars_html_list)

        # Steps HTML
        steps_html_list = []
        for s in spec.derivation_steps:
            steps_html_list.append(f'''
            <div style="margin-bottom:12px; padding:10px 14px; background:#fdfdfd; border-left:3px solid #3b82f6; border-radius:0 6px 6px 0;">
                <div style="font-size:13px; font-weight:700; color:#1e293b;">{html.escape(s.title)}</div>
                <div style="font-family:serif; font-size:15px; color:#2563eb; margin:4px 0;">$${html.escape(s.latex_expression)}$$</div>
                <div style="font-size:12px; color:#64748b;">{html.escape(s.explanation)}</div>
            </div>
            ''')
        steps_section = "".join(steps_html_list) if steps_html_list else ""

        example_section = ""
        if spec.example_calculation:
            example_section = f'''
            <div style="margin-top:16px; padding:12px 16px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px;">
                <div style="font-size:13px; font-weight:700; color:#166534; margin-bottom:4px;">Practical Worked Example:</div>
                <div style="font-size:13px; color:#15803d; white-space:pre-wrap; font-family:monospace;">{html.escape(spec.example_calculation)}</div>
            </div>
            '''

        raw_html = f'''<div class="visual-card formula-card" style="background:#fff; border-radius:12px; padding:24px; box-shadow:0 4px 16px rgba(0,0,0,0.06); max-width:820px; margin:auto; font-family:system-ui, -apple-system, sans-serif;">
    <h3 style="margin-top:0; color:#0f172a; font-size:20px; border-bottom:1px solid #f1f5f9; padding-bottom:10px;">{html.escape(spec.title)}</h3>
    <p style="color:#475569; font-size:14px; line-height:1.6;">{html.escape(spec.explanation)}</p>
    
    <div style="background:linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%); border:1px solid #bfdbfe; border-radius:10px; padding:20px; text-align:center; margin:20px 0;">
        <div style="font-size:24px; color:#1e40af; font-weight:bold;">
            $${html.escape(disp_latex)}$$
        </div>
    </div>

    <h4 style="color:#334155; font-size:14px; text-transform:uppercase; letter-spacing:0.5px; margin-top:20px;">Variable Breakdown & Units</h4>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:10px; margin-top:10px;">
        {vars_section}
    </div>

    {f'<h4 style="color:#334155; font-size:14px; text-transform:uppercase; letter-spacing:0.5px; margin-top:24px;">Derivation & Step-by-Step Logic</h4>' if steps_section else ''}
    {steps_section}

    {example_section}
</div>'''

        full_page = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(spec.title)}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; padding: 24px; margin: 0; }}
    </style>
</head>
<body>
    {raw_html}
</body>
</html>'''

        return RenderedOutput(
            format="katex",
            latex_str=spec.latex,
            raw_html=raw_html,
            full_html_page=full_page
        )
