import html
from app.models.specs.diagram import DiagramSpec
from app.renderers.base import BaseRenderer, RenderedOutput

class DiagramRenderer(BaseRenderer):
    def render(self, spec: DiagramSpec) -> RenderedOutput:
        w = spec.canvas_width
        h = spec.canvas_height

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" style="background:#FFFFFF; font-family: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
            '<defs>',
            '  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#3B82F6" />',
            '  </marker>',
            '  <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#10B981" />',
            '  </marker>',
            '  <marker id="arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#F59E0B" />',
            '  </marker>',
            '  <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%" filterUnits="userSpaceOnUse">',
            '    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0F172A" flood-opacity="0.08" />',
            '  </filter>',
            '</defs>'
        ]

        svg_parts.append(f'<text x="24" y="36" font-size="17" font-weight="700" fill="#0F172A">{html.escape(spec.title)}</text>')

        elem_map = {e.id: e for e in spec.elements}

        for conn in spec.connections:
            s = elem_map.get(conn.source_id)
            t = elem_map.get(conn.target_id)
            if s and t:
                sx = s.x + s.width / 2
                sy = s.y + s.height / 2
                tx = t.x + t.width / 2
                ty = t.y + t.height / 2

                if abs(tx - sx) > abs(ty - sy):
                    if tx > sx:
                        sx = s.x + s.width
                        tx = t.x
                    else:
                        sx = s.x
                        tx = t.x + t.width
                else:
                    if ty > sy:
                        sy = s.y + s.height
                        ty = t.y
                    else:
                        sy = s.y
                        ty = t.y + t.height

                marker_id = "arrow"
                if "10B981" in conn.color or "green" in conn.color.lower():
                    marker_id = "arrow-green"
                elif "F59E0B" in conn.color or "orange" in conn.color.lower():
                    marker_id = "arrow-orange"

                dash = ' stroke-dasharray="6,4"' if conn.arrow_type == "dashed" else ""
                svg_parts.append(f'<path d="M {sx} {sy} Q {(sx+tx)/2} {(sy+ty)/2 - 10} {tx} {ty}" fill="none" stroke="{conn.color}" stroke-width="2.5"{dash} marker-end="url(#{marker_id})" />')

                if conn.label:
                    mx = (sx + tx) / 2
                    my = (sy + ty) / 2 - 12
                    svg_parts.append(f'<rect x="{mx - 40}" y="{my - 9}" width="80" height="18" rx="4" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1" />')
                    svg_parts.append(f'<text x="{mx}" y="{my + 4}" font-size="11" font-weight="600" fill="{conn.color}" text-anchor="middle">{html.escape(conn.label)}</text>')

        for el in spec.elements:
            rx = 24 if el.shape == "pill" else 10
            if el.shape == "circle":
                cx = el.x + el.width / 2
                cy = el.y + el.height / 2
                r = el.width / 2
                svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{el.bg_color}" stroke="{el.border_color}" stroke-width="2" filter="url(#shadow)"/>')
            else:
                svg_parts.append(f'<rect x="{el.x}" y="{el.y}" width="{el.width}" height="{el.height}" rx="{rx}" fill="{el.bg_color}" stroke="{el.border_color}" stroke-width="2" filter="url(#shadow)"/>')

            tx = el.x + el.width / 2
            ty = el.y + el.height / 2 - (6 if el.subtext else 0)
            svg_parts.append(f'<text x="{tx}" y="{ty + 5}" font-size="13" font-weight="700" fill="{el.color}" text-anchor="middle">{html.escape(el.label)}</text>')
            if el.subtext:
                svg_parts.append(f'<text x="{tx}" y="{ty + 20}" font-size="11" font-weight="500" fill="#475569" text-anchor="middle">{html.escape(el.subtext)}</text>')

        for ann in spec.annotations:
            svg_parts.append(f'<g transform="translate({ann.x}, {ann.y})">')
            svg_parts.append(f'  <rect x="0" y="0" width="380" height="42" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.5"/>')
            svg_parts.append(f'  <text x="12" y="16" font-size="11" font-weight="700" fill="{ann.color}">{html.escape(ann.title)}</text>')
            svg_parts.append(f'  <text x="12" y="32" font-size="11" font-weight="500" fill="#334155">{html.escape(ann.text)}</text>')
            svg_parts.append('</g>')

        svg_parts.append('</svg>')
        raw_svg = "\n".join(svg_parts)

        raw_html = f'''<div class="visual-card diagram-wrapper" style="background:#fff; border-radius:12px; padding:20px; box-shadow:0 4px 16px rgba(0,0,0,0.06); max-width:860px; margin:auto;">
    <h3 style="margin-top:0; color:#0f172a; font-size:18px;">{html.escape(spec.title)}</h3>
    <p style="color:#475569; font-size:14px; line-height:1.5;">{html.escape(spec.explanation)}</p>
    <div style="margin-top:16px; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;">
        {raw_svg}
    </div>
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
