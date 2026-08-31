import html
from app.models.specs.architecture import ArchitectureSpec
from app.renderers.base import BaseRenderer, RenderedOutput

class ArchitectureRenderer(BaseRenderer):
    def render(self, spec: ArchitectureSpec) -> RenderedOutput:
        layer_count = max(1, len(spec.layers))
        layer_width = 760
        layer_height = 85
        gap = 25
        canvas_width = 820
        canvas_height = max(460, 80 + layer_count * (layer_height + gap) + 40)

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_width} {canvas_height}" width="100%" height="100%" style="background:#FFFFFF; font-family: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
            '<defs>',
            '  <marker id="arch-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB" />',
            '  </marker>',
            '  <filter id="a-shadow" x="-5%" y="-5%" width="115%" height="115%" filterUnits="userSpaceOnUse">',
            '    <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#0F172A" flood-opacity="0.06" />',
            '  </filter>',
            '</defs>'
        ]

        svg_parts.append(f'<text x="30" y="36" font-size="18" font-weight="700" fill="#0F172A">{html.escape(spec.title)}</text>')

        # Layout Layers and Components
        layer_y_map = {}
        cur_y = 65
        for layer in spec.layers:
            layer_y_map[layer.id] = cur_y
            # Layer Container
            svg_parts.append(f'<rect x="30" y="{cur_y}" width="{layer_width}" height="{layer_height}" rx="10" fill="#F8FAFC" stroke="{layer.color}" stroke-width="1.5" stroke-dasharray="6,4" />')
            svg_parts.append(f'<text x="45" y="{cur_y + 22}" font-size="12" font-weight="700" fill="{layer.color}">{html.escape(layer.name)}</text>')
            if layer.description:
                svg_parts.append(f'<text x="45" y="{cur_y + 36}" font-size="10" font-weight="500" fill="#64748B">{html.escape(layer.description)}</text>')

            # Components in this layer
            comps = [c for c in spec.components if c.layer_id == layer.id]
            if comps:
                comp_w = min(240, int((layer_width - 240) / len(comps)))
                comp_x = 220
                for c in comps:
                    svg_parts.append(f'<rect x="{comp_x}" y="{cur_y + 12}" width="{comp_w}" height="{layer_height - 24}" rx="6" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" filter="url(#a-shadow)" />')
                    svg_parts.append(f'<text x="{comp_x + comp_w/2}" y="{cur_y + 32}" font-size="12" font-weight="700" fill="#1E293B" text-anchor="middle">{html.escape(c.name)}</text>')
                    if c.technology:
                        svg_parts.append(f'<text x="{comp_x + comp_w/2}" y="{cur_y + 48}" font-size="10" font-weight="600" fill="{layer.color}" text-anchor="middle">{html.escape(c.technology)}</text>')
                    comp_x += comp_w + 16

            cur_y += layer_height + gap

        # Draw Directed Pipeline Flow Arrow on Right
        arrow_x = canvas_width - 45
        svg_parts.append(f'<line x1="{arrow_x}" y1="80" x2="{arrow_x}" y2="{cur_y - gap - 10}" stroke="#2563EB" stroke-width="3" marker-end="url(#arch-arrow)" />')
        svg_parts.append(f'<text x="{arrow_x + 10}" y="{(80 + cur_y - gap)/2}" font-size="11" font-weight="700" fill="#2563EB" transform="rotate(90, {arrow_x + 10}, {(80 + cur_y - gap)/2})" text-anchor="middle">PIPELINE FLOW</text>')

        svg_parts.append('</svg>')
        raw_svg = "\n".join(svg_parts)

        principles_html = ""
        if spec.key_principles:
            lis = "".join([f'<li style="margin-bottom:4px;">{html.escape(p)}</li>' for p in spec.key_principles])
            principles_html = f'''
            <div style="margin-top:16px; padding:12px 16px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px;">
                <div style="font-size:13px; font-weight:700; color:#166534; margin-bottom:6px;">System Architectural Principles:</div>
                <ul style="margin:0; padding-left:20px; font-size:13px; color:#14532d;">{lis}</ul>
            </div>
            '''

        raw_html = f'''<div class="visual-card arch-wrapper" style="background:#fff; border-radius:12px; padding:20px; box-shadow:0 4px 16px rgba(0,0,0,0.06); max-width:860px; margin:auto;">
    <h3 style="margin-top:0; color:#0f172a; font-size:18px;">{html.escape(spec.title)}</h3>
    <p style="color:#475569; font-size:14px; line-height:1.5;">{html.escape(spec.explanation)}</p>
    <div style="margin-top:16px; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;">
        {raw_svg}
    </div>
    {principles_html}
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
            format="svg",
            raw_svg=raw_svg,
            raw_html=raw_html,
            full_html_page=full_page
        )
