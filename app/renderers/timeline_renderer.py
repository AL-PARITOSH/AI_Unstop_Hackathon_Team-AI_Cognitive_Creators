import html
from app.models.specs.timeline import TimelineSpec
from app.renderers.base import BaseRenderer, RenderedOutput

class TimelineRenderer(BaseRenderer):
    def render(self, spec: TimelineSpec) -> RenderedOutput:
        event_count = len(spec.events)
        event_height = 95
        gap = 25
        canvas_width = 820
        canvas_height = max(500, 80 + event_count * (event_height + gap))
        cx = 120  # Left date line offset

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_width} {canvas_height}" width="100%" height="100%" style="background:#FFFFFF; font-family: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
            '<defs>',
            '  <filter id="t-shadow" x="-5%" y="-5%" width="115%" height="115%" filterUnits="userSpaceOnUse">',
            '    <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#0F172A" flood-opacity="0.06" />',
            '  </filter>',
            '</defs>'
        ]

        svg_parts.append(f'<text x="30" y="36" font-size="18" font-weight="700" fill="#0F172A">{html.escape(spec.title)}</text>')

        # Vertical axis line
        axis_start_y = 65
        axis_end_y = canvas_height - 40
        svg_parts.append(f'<line x1="{cx}" y1="{axis_start_y}" x2="{cx}" y2="{axis_end_y}" stroke="#CBD5E1" stroke-width="3" stroke-linecap="round" />')

        cur_y = 80
        for i, ev in enumerate(spec.events):
            dot_color = "#2563EB" if ev.importance == "high" else "#64748B"
            dot_radius = 8 if ev.importance == "high" else 6
            badge_bg = "#DBEAFE" if ev.importance == "high" else "#F1F5F9"
            badge_color = "#1E40AF" if ev.importance == "high" else "#475569"

            # Milestone marker node on axis
            svg_parts.append(f'<circle cx="{cx}" cy="{cur_y + 25}" r="{dot_radius + 4}" fill="#FFFFFF" stroke="{dot_color}" stroke-width="3" />')
            svg_parts.append(f'<circle cx="{cx}" cy="{cur_y + 25}" r="{dot_radius}" fill="{dot_color}" />')

            # Date on left
            svg_parts.append(f'<text x="{cx - 16}" y="{cur_y + 28}" font-size="12" font-weight="700" fill="#1E293B" text-anchor="end">{html.escape(ev.date_or_period)}</text>')

            # Card on right
            card_x = cx + 24
            card_w = canvas_width - card_x - 30
            card_h = event_height

            svg_parts.append(f'<rect x="{card_x}" y="{cur_y}" width="{card_w}" height="{card_h}" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" filter="url(#t-shadow)" />')

            # Category chip
            if ev.category:
                svg_parts.append(f'<rect x="{card_x + 14}" y="{cur_y + 12}" width="95" height="18" rx="4" fill="{badge_bg}" />')
                svg_parts.append(f'<text x="{card_x + 61}" y="{cur_y + 25}" font-size="10" font-weight="700" fill="{badge_color}" text-anchor="middle">{html.escape(ev.category)}</text>')

            # Title
            title_offset_x = card_x + 120 if ev.category else card_x + 14
            svg_parts.append(f'<text x="{title_offset_x}" y="{cur_y + 26}" font-size="14" font-weight="700" fill="#0F172A">{html.escape(ev.title)}</text>')

            # Description
            svg_parts.append(f'<text x="{card_x + 14}" y="{cur_y + 52}" font-size="12" font-weight="500" fill="#475569" width="{card_w - 28}">{html.escape(ev.description[:110] + ("..." if len(ev.description) > 110 else ""))}</text>')

            # Tags
            if ev.tags:
                tag_x = card_x + 14
                for tag in ev.tags[:3]:
                    tw = len(tag) * 7 + 12
                    svg_parts.append(f'<rect x="{tag_x}" y="{cur_y + 68}" width="{tw}" height="16" rx="3" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>')
                    svg_parts.append(f'<text x="{tag_x + tw/2}" y="{cur_y + 80}" font-size="10" font-weight="500" fill="#64748B" text-anchor="middle">#{html.escape(tag)}</text>')
                    tag_x += tw + 8

            cur_y += event_height + gap

        svg_parts.append('</svg>')
        raw_svg = "\n".join(svg_parts)

        raw_html = f'''<div class="visual-card timeline-wrapper" style="background:#fff; border-radius:12px; padding:20px; box-shadow:0 4px 16px rgba(0,0,0,0.06); max-width:860px; margin:auto;">
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
