import html
import plotly.graph_objects as go
from app.models.specs.graph import GraphSpec
from app.renderers.base import BaseRenderer, RenderedOutput

class GraphRenderer(BaseRenderer):
    def render(self, spec: GraphSpec) -> RenderedOutput:
        fig = go.Figure()

        for s in spec.series:
            mode = s.mode
            line_kwargs = {}
            if s.line_color:
                line_kwargs["color"] = s.line_color
            if s.line_width:
                line_kwargs["width"] = s.line_width
            if s.line_dash:
                line_kwargs["dash"] = s.line_dash

            if mode == "bar":
                fig.add_trace(go.Bar(
                    x=s.x_values,
                    y=s.y_values,
                    name=s.name,
                    marker=dict(color=s.line_color or "#2563EB")
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=s.x_values,
                    y=s.y_values,
                    mode=mode,
                    name=s.name,
                    line=line_kwargs,
                    marker=dict(size=8)
                ))

        for ann in spec.annotations:
            fig.add_annotation(
                x=ann.x,
                y=ann.y,
                text=ann.text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=ann.point_color,
                ax=0,
                ay=-35,
                bgcolor="#FFFFFF",
                bordercolor=ann.point_color,
                borderwidth=1.5,
                borderpad=4,
                font=dict(size=12, color="#0F172A", family="sans-serif")
            )

        layout_dict = dict(
            title=dict(text=spec.title, font=dict(size=16, color="#0F172A", family="sans-serif")),
            xaxis=dict(
                title=spec.x_label,
                showgrid=spec.show_grid,
                gridcolor="#E2E8F0",
                zeroline=True,
                zerolinecolor="#94A3B8",
                zerolinewidth=2
            ),
            yaxis=dict(
                title=spec.y_label,
                showgrid=spec.show_grid,
                gridcolor="#E2E8F0",
                zeroline=True,
                zerolinecolor="#94A3B8",
                zerolinewidth=2
            ),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=50, r=50, t=60, b=50),
            hovermode="closest",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        if spec.x_range:
            layout_dict["xaxis"]["range"] = spec.x_range
        if spec.y_range:
            layout_dict["yaxis"]["range"] = spec.y_range

        if spec.plotly_layout_override:
            layout_dict.update(spec.plotly_layout_override)

        fig.update_layout(**layout_dict)

        plotly_json = fig.to_dict()
        plot_html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        raw_html = f'''<div class="visual-card graph-wrapper" style="background:#fff; border-radius:12px; padding:20px; box-shadow:0 4px 16px rgba(0,0,0,0.06); max-width:860px; margin:auto;">
    <h3 style="margin-top:0; color:#0f172a; font-size:18px;">{html.escape(spec.title)}</h3>
    <p style="color:#475569; font-size:14px; line-height:1.5;">{html.escape(spec.explanation)}</p>
    <div style="margin-top:16px; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;">
        {plot_html}
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
            format="plotly",
            plotly_dict=plotly_json,
            raw_html=raw_html,
            full_html_page=full_page
        )
