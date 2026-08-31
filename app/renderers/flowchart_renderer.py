import html
from app.models.specs.flowchart import FlowchartSpec
from app.renderers.base import BaseRenderer, RenderedOutput

class FlowchartRenderer(BaseRenderer):
    def render(self, spec: FlowchartSpec) -> RenderedOutput:
        node_count = len(spec.nodes)
        node_height = 65
        node_width = 300
        gap = 45
        canvas_width = 820
        canvas_height = max(450, 80 + node_count * (node_height + gap))
        cx = canvas_width / 2

        node_index_map = {n.id: i for i, n in enumerate(spec.nodes)}
        node_positions = {}
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_width} {canvas_height}" width="100%" height="100%" style="background:#FFFFFF; font-family: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
            '<defs>',
            '  <marker id="flow-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#3B82F6" />',
            '  </marker>',
            '  <marker id="flow-arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#10B981" />',
            '  </marker>',
            '  <marker id="flow-arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#EF4444" />',
            '  </marker>',
            '  <filter id="f-shadow" x="-5%" y="-5%" width="115%" height="115%" filterUnits="userSpaceOnUse">',
            '    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0F172A" flood-opacity="0.07" />',
            '  </filter>',
            '</defs>'
        ]

        svg_parts.append(f'<text x="30" y="36" font-size="18" font-weight="700" fill="#0F172A">{html.escape(spec.title)}</text>')

        cur_y = 70
        for node in spec.nodes:
            node_positions[node.id] = (cx, cur_y, cur_y + node_height)
            cur_y += node_height + gap

        # Draw Edges
        for edge in spec.edges:
            s_pos = node_positions.get(edge.source_id)
            t_pos = node_positions.get(edge.target_id)
            s_idx = node_index_map.get(edge.source_id, 0)
            t_idx = node_index_map.get(edge.target_id, 0)

            if s_pos and t_pos:
                sx, sy_top, sy_bottom = s_pos
                tx, ty_top, ty_bottom = t_pos

                marker = "flow-arrow"
                stroke_color = "#3B82F6"
                if edge.condition == "Yes" or (edge.label and "yes" in edge.label.lower()):
                    marker = "flow-arrow-green"
                    stroke_color = "#10B981"
                elif edge.condition == "No" or (edge.label and "no" in edge.label.lower()):
                    marker = "flow-arrow-red"
                    stroke_color = "#EF4444"

                # 1. Loop back (target is above source)
                if t_idx < s_idx:
                    loop_offset = node_width / 2 + 55
                    sy_mid = (sy_top + sy_bottom) / 2
                    ty_mid = (ty_top + ty_bottom) / 2
                    svg_parts.append(f'<path d="M {sx + node_width/2} {sy_mid} H {sx + loop_offset} V {ty_mid} H {tx + node_width/2 + 5}" fill="none" stroke="{stroke_color}" stroke-width="2.5" stroke-dasharray="5,4" marker-end="url(#{marker})" />')
                    if edge.label:
                        svg_parts.append(f'<text x="{sx + loop_offset + 10}" y="{(sy_mid + ty_mid)/2}" font-size="11" font-weight="600" fill="{stroke_color}">{html.escape(edge.label)}</text>')

                # 2. Leap forward (target is NOT the immediate next node: route around left side)
                elif t_idx > s_idx + 1:
                    side_offset = node_width / 2 + 50
                    sy_mid = (sy_top + sy_bottom) / 2
                    ty_mid = (ty_top + ty_bottom) / 2
                    svg_parts.append(f'<path d="M {sx - node_width/2} {sy_mid} H {sx - side_offset} V {ty_mid} H {tx - node_width/2 - 5}" fill="none" stroke="{stroke_color}" stroke-width="2.5" marker-end="url(#{marker})" />')
                    if edge.label or edge.condition:
                        txt = edge.label or edge.condition
                        svg_parts.append(f'<rect x="{sx - side_offset - 45}" y="{(sy_mid + ty_mid)/2 - 10}" width="65" height="18" rx="4" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1" />')
                        svg_parts.append(f'<text x="{sx - side_offset - 12}" y="{(sy_mid + ty_mid)/2 + 3}" font-size="11" font-weight="700" fill="{stroke_color}" text-anchor="middle">{html.escape(txt)}</text>')

                # 3. Direct next node (straight down)
                else:
                    svg_parts.append(f'<path d="M {sx} {sy_bottom} V {ty_top}" fill="none" stroke="{stroke_color}" stroke-width="2.5" marker-end="url(#{marker})" />')
                    if edge.label or edge.condition:
                        txt = edge.label or edge.condition
                        svg_parts.append(f'<rect x="{sx + 8}" y="{(sy_bottom + ty_top)/2 - 10}" width="70" height="18" rx="4" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1" />')
                        svg_parts.append(f'<text x="{sx + 43}" y="{(sy_bottom + ty_top)/2 + 3}" font-size="11" font-weight="700" fill="{stroke_color}" text-anchor="middle">{html.escape(txt)}</text>')

        # Draw Nodes
        for node in spec.nodes:
            _, ny_top, _ = node_positions[node.id]
            nx = cx - node_width / 2
            ny = ny_top

            if node.node_type == "start" or node.node_type == "end":
                bg = "#EFF6FF" if node.node_type == "start" else "#FEF2F2"
                border = "#3B82F6" if node.node_type == "start" else "#EF4444"
                text_col = "#1E40AF" if node.node_type == "start" else "#B91C1C"
                svg_parts.append(f'<rect x="{nx}" y="{ny}" width="{node_width}" height="{node_height}" rx="{node_height/2}" fill="{bg}" stroke="{border}" stroke-width="2" filter="url(#f-shadow)" />')
            elif node.node_type == "decision":
                bg = "#FEF3C7"
                border = "#F59E0B"
                text_col = "#92400E"
                pts = f"{cx},{ny} {nx + node_width},{ny + node_height/2} {cx},{ny + node_height} {nx},{ny + node_height/2}"
                svg_parts.append(f'<polygon points="{pts}" fill="{bg}" stroke="{border}" stroke-width="2" filter="url(#f-shadow)" />')
            else:
                bg = "#F8FAFC"
                border = "#64748B"
                text_col = "#0F172A"
                svg_parts.append(f'<rect x="{nx}" y="{ny}" width="{node_width}" height="{node_height}" rx="10" fill="{bg}" stroke="{border}" stroke-width="2" filter="url(#f-shadow)" />')

            # Text
            text_y = ny + (node_height / 2) - (6 if node.detail else 0)
            svg_parts.append(f'<text x="{cx}" y="{text_y + 4}" font-size="13" font-weight="700" fill="{text_col}" text-anchor="middle">{html.escape(node.label)}</text>')
            if node.detail:
                svg_parts.append(f'<text x="{cx}" y="{text_y + 20}" font-size="11" font-weight="500" fill="#64748B" text-anchor="middle">{html.escape(node.detail)}</text>')

        svg_parts.append('</svg>')
        raw_svg = "\n".join(svg_parts)

        raw_html = f'''<div class="visual-card flowchart-wrapper" style="background:#fff; border-radius:12px; padding:20px; box-shadow:0 4px 16px rgba(0,0,0,0.06); max-width:860px; margin:auto;">
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
