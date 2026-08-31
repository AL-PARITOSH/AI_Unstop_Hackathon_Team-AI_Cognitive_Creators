import html
import json
from pygments import highlight
from pygments.lexers import get_lexer_by_name, PythonLexer
from pygments.formatters import HtmlFormatter
from app.models.specs.code_execution import CodeExecutionSpec
from app.renderers.base import BaseRenderer, RenderedOutput

class CodeRenderer(BaseRenderer):
    def render(self, spec: CodeExecutionSpec) -> RenderedOutput:
        try:
            lexer = get_lexer_by_name(spec.language.lower(), stripall=True)
        except Exception:
            lexer = PythonLexer()

        formatter = HtmlFormatter(
            linenos=True,
            cssclass="highlight-pygments",
            style="default",
            hl_lines=spec.highlighted_lines
        )
        pygments_css = formatter.get_style_defs('.highlight-pygments')
        highlighted_code = highlight(spec.code, lexer, formatter)

        # Build Trace Table
        trace_rows = []
        for step in spec.execution_trace:
            vars_json = json.dumps(step.variables_state) if step.variables_state else "{}"
            stdout_str = f'<code style="color:#059669; font-weight:600;">{html.escape(step.output_printed)}</code>' if step.output_printed else '<span style="color:#94a3b8;">-</span>'
            trace_rows.append(f'''
            <tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding:8px 12px; font-weight:700; color:#2563eb;">Step {step.step_number}</td>
                <td style="padding:8px 12px; font-family:monospace; color:#475569;">Line {step.line_number}</td>
                <td style="padding:8px 12px; font-family:monospace; font-size:12px; color:#0f172a; background:#f8fafc;">{html.escape(step.code_line)}</td>
                <td style="padding:8px 12px; font-size:12px; color:#334155;">{html.escape(step.explanation)}</td>
                <td style="padding:8px 12px; font-family:monospace; font-size:11px; color:#7c3aed;">{html.escape(vars_json)}</td>
                <td style="padding:8px 12px; font-size:12px;">{stdout_str}</td>
            </tr>
            ''')
        trace_tbody = "".join(trace_rows)

        takeaways_html = ""
        if spec.key_takeaways:
            lis = "".join([f'<li style="margin-bottom:4px;">{html.escape(t)}</li>' for t in spec.key_takeaways])
            takeaways_html = f'''
            <div style="margin-top:16px; padding:12px 16px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px;">
                <div style="font-size:13px; font-weight:700; color:#1e40af; margin-bottom:6px;">Key Pedagogical Takeaways:</div>
                <ul style="margin:0; padding-left:20px; font-size:13px; color:#1e3a8a;">{lis}</ul>
            </div>
            '''

        raw_html = f'''<div class="visual-card code-wrapper" style="background:#fff; border-radius:12px; padding:24px; box-shadow:0 4px 16px rgba(0,0,0,0.06); max-width:880px; margin:auto; font-family:system-ui, -apple-system, sans-serif;">
    <style>{pygments_css}
    .highlight-pygments {{ border-radius:8px; overflow:hidden; border:1px solid #e2e8f0; font-size:13px; }}
    .highlight-pygments pre {{ margin:0; padding:12px; line-height:1.5; }}
    .highlight-pygments .linenodiv pre {{ color:#94a3b8; background:#f8fafc; padding-right:10px; border-right:1px solid #e2e8f0; }}
    </style>
    <h3 style="margin-top:0; color:#0f172a; font-size:18px;">{html.escape(spec.title)}</h3>
    <p style="color:#475569; font-size:14px; line-height:1.5;">{html.escape(spec.explanation)}</p>
    
    <div style="margin:16px 0;">
        <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#64748b; margin-bottom:6px;">Source Code ({html.escape(spec.language)}):</div>
        {highlighted_code}
    </div>

    {f'<div style="font-size:12px; font-weight:700; text-transform:uppercase; color:#64748b; margin-top:20px; margin-bottom:8px;">Execution State & Variable Trace:</div>' if trace_tbody else ''}
    <div style="overflow-x:auto; border:1px solid #e2e8f0; border-radius:8px;">
        <table style="width:100%; border-collapse:collapse; text-align:left; font-size:13px;">
            <thead>
                <tr style="background:#f8fafc; border-bottom:2px solid #e2e8f0; color:#475569; font-size:11px; text-transform:uppercase;">
                    <th style="padding:10px 12px;">Step</th>
                    <th style="padding:10px 12px;">Line</th>
                    <th style="padding:10px 12px;">Executing Statement</th>
                    <th style="padding:10px 12px;">Action & Explanation</th>
                    <th style="padding:10px 12px;">Variables In Scope</th>
                    <th style="padding:10px 12px;">Stdout</th>
                </tr>
            </thead>
            <tbody>
                {trace_tbody}
            </tbody>
        </table>
    </div>

    {takeaways_html}
</div>'''

        full_page = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(spec.title)}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; padding: 24px; margin: 0; }}
    </style>
</head>
<body>
    {raw_html}
</body>
</html>'''

        return RenderedOutput(
            format="html",
            raw_html=raw_html,
            full_html_page=full_page
        )
