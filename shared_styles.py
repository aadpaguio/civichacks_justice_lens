"""
Shared styling for Justice Lens dashboards.
Based on arnald.py with chart/card elements from deep.py.
"""
import streamlit as st

# Palette: editorial / dashboard (arnald-based)
COLORS = {
    "primary": "#0f172a",
    "secondary": "#1e293b",
    "accent": "#0ea5e9",
    "accent_soft": "#38bdf8",
    "youth": "#dc2626",
    "adult": "#059669",
    "neutral": "#64748b",
    "card_bg": "#f8fafc",
    "border": "#e2e8f0",
    # Dang page semantic aliases (juvenile / all arrests)
    "juvenile": "#e85d4a",
    "juvenile_muted": "#e85d4a",
    "all_arrests": "#4a9eff",
    "adult_muted": "#7eb8ff",
}

# Chart defaults (readable on white)
CHART_BG = "#ffffff"
FONT_FAMILY = "'DM Sans', 'Segoe UI', system-ui, sans-serif"
CHART_FONT_COLOR = "#0f172a"
CHART_GRID_COLOR = "#e2e8f0"

# Shared CSS: arnald base + deep's chart-card padding/shadow and dataframe styling
_SHARED_CSS_BODY = r"""
.stApp { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%); }
.main .block-container, .block-container { padding-top: 3.5rem; padding-bottom: 3rem; max-width: 1400px; color: #0f172a; }
[data-testid="stHeader"] { padding-top: 0.5rem; padding-bottom: 0.5rem; }
.block-container p, .block-container span, .block-container label { color: #0f172a !important; }
.block-container .hero, .block-container .hero p, .block-container .hero h1, .block-container .hero span { color: #f8fafc !important; }
.block-container .hero p { color: #94a3b8 !important; }
.hero, .hero *, .hero h1, .hero p, [data-testid="stMarkdown"] .hero, [data-testid="stMarkdown"] .hero * {
    color: #f8fafc !important;
}
.hero p, [data-testid="stMarkdown"] .hero p { color: #94a3b8 !important; }
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    margin: -1rem -1rem 0 -1rem;
    padding: 2rem 2rem 1.5rem;
    border-radius: 0 0 20px 20px;
    box-shadow: 0 10px 40px rgba(15,23,42,0.2);
}
.hero h1, [data-testid="stMarkdown"] .hero h1 {
    color: #f8fafc !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 1.85rem;
    letter-spacing: -0.02em;
    margin: 0;
}
.hero .accent-bar {
    width: 48px;
    height: 3px;
    background: linear-gradient(90deg, #0ea5e9, #38bdf8);
    border-radius: 2px;
    margin-top: 0.75rem;
}
div[data-testid="metric-container"] {
    background: #ffffff;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"],
div[data-testid="metric-container"] [data-testid="stMetricValue"],
div[data-testid="metric-container"] label { color: #0f172a !important; }
[data-testid="stMetricValue"] { font-family: 'DM Sans', sans-serif; font-weight: 700; color: #0f172a !important; }
.section-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    color: #0f172a;
    letter-spacing: -0.01em;
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #0ea5e9;
    display: inline-block;
}
.chart-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0;
    margin-bottom: 1rem;
}
div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06);
}
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #f8fafc !important; font-size: 0.95rem !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stSlider label, [data-testid="stSidebar"] [data-testid="stWidgetLabel"] { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; }
[data-testid="stSidebar"] a { color: #e2e8f0 !important; }
[data-testid="stSidebar"] a:hover { color: #f8fafc !important; }
[data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stMultiSelect label, [data-testid="stSidebar"] .stSlider label { color: #cbd5e1 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stAlert, [data-testid="stSidebar"] [data-testid="stAlert"] { color: #cbd5e1 !important; }
.footer { text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 2rem; padding: 1rem; }
"""


def inject_css():
    """Inject shared CSS into the Streamlit app (no visible output)."""
    inner = (
        '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">'
        "<style>" + _SHARED_CSS_BODY.replace("\n", " ").strip() + "</style>"
    )
    # Hidden wrapper so the block takes no space; styles still apply to the whole page
    html = '<div style="display:none; height:0; overflow:hidden;">' + inner + "</div>"
    try:
        st.html(html)
    except AttributeError:
        # Streamlit < 1.28: no st.html, fall back to markdown
        st.markdown(html, unsafe_allow_html=True)


def chart_layout(fig, height=None):
    """Apply readable dark text and white background to a Plotly figure."""
    layout = dict(
        template="plotly_white",
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_FAMILY, color=CHART_FONT_COLOR, size=12),
        title_font=dict(family=FONT_FAMILY, color=CHART_FONT_COLOR, size=14),
        xaxis=dict(
            tickfont=dict(color=CHART_FONT_COLOR),
            title_font=dict(color=CHART_FONT_COLOR),
            gridcolor=CHART_GRID_COLOR,
        ),
        yaxis=dict(
            tickfont=dict(color=CHART_FONT_COLOR),
            title_font=dict(color=CHART_FONT_COLOR),
            gridcolor=CHART_GRID_COLOR,
        ),
        legend=dict(font=dict(color=CHART_FONT_COLOR)),
    )
    if height:
        layout["height"] = height
    fig.update_layout(**layout)
    try:
        fig.update_annotations(font_color=CHART_FONT_COLOR)
    except Exception:
        pass
    return fig


def hero_html(title: str, tagline: str = "", with_accent_bar: bool = True):
    """Return HTML for the hero block. Light title/tagline via inline styles so they stay readable."""
    accent = '<div class="accent-bar"></div>' if with_accent_bar else ""
    tag = f'<p style="color:#94a3b8!important;font-size:0.95rem;margin:0.4rem 0 0 0;">{tagline}</p>' if tagline else ""
    return (
        f'<div class="hero" style="color:#f8fafc!important;">'
        f'<h1 style="color:#f8fafc!important;font-family:\'DM Sans\',sans-serif;font-weight:700;font-size:1.85rem;letter-spacing:-0.02em;margin:0;">{title}</h1>'
        f'{tag}{accent}</div>'
    )


def sidebar_page_links():
    """Render sidebar navigation with Title Case page names (call from each page)."""
    st.sidebar.markdown("### Pages")
    st.sidebar.page_link("pages/police_misconduct.py", label="Police Misconduct")
    st.sidebar.page_link("pages/youth_arrests.py", label="Youth Arrests")
    st.sidebar.page_link("pages/incident_reports.py", label="Incident Reports")
    st.sidebar.divider()
