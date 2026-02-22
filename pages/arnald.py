"""
Police Misconduct Reports — Boston IAD data with youth labels.
"""
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page config
st.set_page_config(page_title="Police Misconduct Reports", layout="wide", initial_sidebar_state="expanded")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "iad_extracted_with_youth_labels.csv"

# Palette: editorial / dashboard
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
}
CHART_BG = "#ffffff"
FONT_FAMILY = "'DM Sans', 'Segoe UI', system-ui, sans-serif"
# Dark text for all chart elements (readable on white)
CHART_FONT_COLOR = "#0f172a"
CHART_GRID_COLOR = "#e2e8f0"

# Map messy allegation labels to canonical ones (for display, especially youth)
ALLEGATION_LABEL_MAP = {
    # Truncated / typo
    "of Force": "Use of Force",
    "to Laws": "Conformance to Laws",
    "Unbecoming": "Conduct Unbecoming",
    "Policing Policy": "BIAS-Free Policing Policy",
    "Unreasonable Judgement": "Neg.Duty/Unreasonable Judge",
    "on Duty": "Reporting for Duty",
    "Prisoners": "Treatment",
    "Handcuffs": "Use of Force",
    "Identification": "Self Identification",
    "Examination for Visible Injuries": "Treatment",
    # (N counts) variants
    "Use of Force (2 counts)": "Use of Force",
    "Use of Force (3 counts)": "Use of Force",
    "Neg.Duty/Unreasonable Judge (2 counts)": "Neg.Duty/Unreasonable Judge",
    "Neg.Duty/Unreasonable Judge (3 counts)": "Neg.Duty/Unreasonable Judge",
    "Neglect of Duty/Unreasonable Judgment (2 counts)": "Neg.Duty/Unreasonable Judge",
    "Conduct Unbecoming (2 counts)": "Conduct Unbecoming",
    "Conduct Unbecoming (3 counts)": "Conduct Unbecoming",
    "Respectful Treatment (2 counts)": "Respectful Treatment",
    "Respectful Treatment (3 counts)": "Respectful Treatment",
    "Conformance to Laws (2 counts)": "Conformance to Laws",
    # Officer name prefix (youth data)
    "NGUYEN Conduct Unbecoming": "Conduct Unbecoming",
    "NGUYEN Respectful Treatment": "Respectful Treatment",
    "NGUYEN Canons of Ethics": "Conduct Unbecoming",
    "NGUYEN Neg.Duty/Unreasonable Judge": "Neg.Duty/Unreasonable Judge",
    "Leon BIAS-Free Policing Policy": "BIAS-Free Policing Policy",
    "Leon Use of Force (2 counts)": "Use of Force",
    "Boulger Respectful Treatment": "Respectful Treatment",
    "Mccarthy Respectful Treatment": "Respectful Treatment",
    "Doherty Use of Force": "Use of Force",
    "Kennedy Neg.Duty/Unreasonable Judge": "Neg.Duty/Unreasonable Judge",
    "Jr. Respectful Treatment": "Respectful Treatment",
    "Jr. Neg.Duty/Unreasonable Judge": "Neg.Duty/Unreasonable Judge",
    "III Respectful Treatment": "Respectful Treatment",
    # Other
    "Situations Involving Family & Frien": "Conduct Unbecoming",
    "F.I.O Reports": "Field Interrogation & Observation Report",
    "Manner of Recording Complaints": "Reporting for Duty",
}


def _normalize_allegation(raw):
    """Return canonical allegation label for display; empty/unknown return empty string."""
    if pd.isna(raw) or raw is None:
        return ""
    s = str(raw).strip()
    if s in ("", "nan", "Unknown"):
        return ""
    # Direct mapping
    if s in ALLEGATION_LABEL_MAP:
        return ALLEGATION_LABEL_MAP[s]
    # Strip " (N counts)" and try again
    s_no_counts = re.sub(r"\s*\(\d+\s+counts?\)\s*$", "", s, flags=re.I).strip()
    if s_no_counts and s_no_counts in ALLEGATION_LABEL_MAP:
        return ALLEGATION_LABEL_MAP[s_no_counts]
    # Officer-name prefix: if one word + space + known suffix, use suffix
    for canonical in (
        "Neg.Duty/Unreasonable Judge", "Respectful Treatment", "Use of Force",
        "Conduct Unbecoming", "Conformance to Laws", "BIAS-Free Policing Policy",
        "Self Identification", "Treatment", "Reporting for Duty",
    ):
        if s.endswith(canonical) and len(s) > len(canonical) and s[len(s) - len(canonical) - 1] in (" ", "."):
            return canonical
    return s

def _chart_layout(fig, height=None):
    """Apply readable dark text and white background to a Plotly figure."""
    layout = dict(
        template="plotly_white",
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=FONT_FAMILY, color=CHART_FONT_COLOR, size=12),
        xaxis=dict(tickfont=dict(color=CHART_FONT_COLOR), title_font=dict(color=CHART_FONT_COLOR), gridcolor=CHART_GRID_COLOR),
        yaxis=dict(tickfont=dict(color=CHART_FONT_COLOR), title_font=dict(color=CHART_FONT_COLOR), gridcolor=CHART_GRID_COLOR),
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

# Custom CSS: non-default Streamlit look
def inject_css():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    /* Main area — dark text for readability */
    .stApp { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%); }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; color: #0f172a; }
    .block-container p, .block-container span, .block-container label { color: #0f172a !important; }
    /* Hero header */
    .hero { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        margin: -1rem -1rem 0 -1rem; 
        padding: 2rem 2rem 1.5rem; 
        border-radius: 0 0 20px 20px;
        box-shadow: 0 10px 40px rgba(15,23,42,0.2);
    }
    .hero h1 { 
        color: #f8fafc; 
        font-family: 'DM Sans', sans-serif; 
        font-weight: 700; 
        font-size: 1.85rem; 
        letter-spacing: -0.02em;
        margin: 0;
    }
    .hero p { 
        color: #94a3b8; 
        font-size: 0.95rem; 
        margin: 0.4rem 0 0 0;
    }
    /* Metric cards — force dark text for readability */
    div[data-testid="metric-container"] {
        background: #ffffff;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    div[data-testid="metric-container"] [data-testid="stMetricLabel"],
    div[data-testid="metric-container"] [data-testid="stMetricValue"],
    div[data-testid="metric-container"] label {
        color: #0f172a !important;
    }
    [data-testid="stMetricValue"] { font-family: 'DM Sans', sans-serif; font-weight: 700; color: #0f172a !important; }
    /* Section titles */
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
    /* Chart containers */
    .chart-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] .stMarkdown { color: #94a3b8; }
    [data-testid="stSidebar"] h2 { color: #f8fafc !important; font-size: 0.95rem !important; }
    [data-testid="stSidebar"] label { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] .stSlider label { color: #cbd5e1 !important; }
    /* Footer */
    .footer { 
        text-align: center; 
        color: #64748b; 
        font-size: 0.8rem; 
        margin-top: 2rem; 
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def _parse_year_from_date(series):
    """Extract 4-digit year from date strings (M/D/YYYY) or datetime."""
    def parse(v):
        try:
            s = str(v).strip()
            if s in ("", "nan", "NaT"):
                return None
            # M/D/YYYY
            parts = s.split("/")
            if len(parts) == 3 and parts[-1].isdigit():
                return int(parts[-1])
            # ISO-like YYYY-MM-DD
            if len(s) >= 4 and s[:4].isdigit():
                return int(s[:4])
            if len(s) >= 4 and s[-4:].isdigit():
                return int(s[-4:])
        except Exception:
            pass
        return None
    return series.astype(str).apply(parse)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, low_memory=False)
    # Parse dates (US format M/D/YYYY)
    for col in ["received_date_x", "occurred_date_x"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    # Derive year from received date (use string extraction so we always get year)
    df["year_received"] = _parse_year_from_date(df["received_date_x"].fillna("").astype(str))
    if df["year_received"].isna().all():
        df["year_received"] = df["received_date_x"].dt.year
    df["year_occurred"] = df["occurred_date_x"].dt.year
    # Restrict to 2011-2020 only
    df = df[(df["year_received"] >= 2011) & (df["year_received"] <= 2020)].copy()
    # Clean key categoricals
    for col in ["incident_type_x", "allegation_x", "finding_x", "disposition_x", "rank_x", "label"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["label"] = df["label"].replace({"": "Unknown", "nan": "Unknown"}).fillna("Unknown")
    return df

def main():
    inject_css()
    st.markdown("""
    <div class="hero">
        <h1>Police Misconduct Reports</h1>
        <p>Boston Police Department — Internal Affairs Division (IAD) · Complaints with youth-related labels · 2011–2020</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        st.warning("No data loaded.")
        return

    # ---- Sidebar filters (data is already 2011-2020) ----
    with st.sidebar:
        st.subheader("Filters")
        year_range = st.slider("Year received", 2011, 2020, (2011, 2020), 1)
        youth_filter = st.selectbox("Youth-related", ["All", "Yes", "No"], index=0)
        incident_types = ["All"] + sorted(df["incident_type_x"].dropna().replace("", "Unknown").unique().tolist())
        incident_type = st.selectbox("Incident type", incident_types, index=0)
        allegations = df["allegation_x"].value_counts()
        top_allegations = ["All"] + allegations.head(12).index.tolist()
        allegation_filter = st.selectbox("Allegation type", top_allegations, index=0)
        findings = ["All"] + sorted(df["finding_x"].replace("", "Unknown").dropna().unique().tolist())
        finding_filter = st.selectbox("Finding", findings, index=0)

    # Apply filters
    mask = (
        (df["year_received"] >= year_range[0]) &
        (df["year_received"] <= year_range[1])
    )
    if youth_filter == "Yes":
        mask &= df["label"] == "YES"
    elif youth_filter == "No":
        mask &= df["label"] == "NO"
    if incident_type != "All":
        mask &= df["incident_type_x"] == incident_type
    if allegation_filter != "All":
        mask &= df["allegation_x"] == allegation_filter
    if finding_filter != "All":
        if finding_filter == "Unknown":
            mask &= (df["finding_x"].isna() | (df["finding_x"].astype(str).str.strip() == ""))
        else:
            mask &= df["finding_x"] == finding_filter
    data = df.loc[mask].copy()
    data["allegation_normalized"] = data["allegation_x"].apply(_normalize_allegation)

    # ---- Summary metrics (all by unique IAD cases) ----
    unique_iads = data["ia_no"].nunique()
    youth_iads = data.loc[data["label"] == "YES", "ia_no"].nunique()
    sustained_iads = data.loc[data["finding_x"] == "Sustained", "ia_no"].nunique()
    sustained_pct = (100 * sustained_iads / unique_iads) if unique_iads else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Unique IAD cases", f"{unique_iads:,}", help="Distinct IAD case numbers (what matters)")
    with col2:
        st.metric("Youth-related IADs", f"{youth_iads:,}", help="IAD cases labeled as involving youth")
    with col3:
        st.metric("Sustained IADs", f"{sustained_iads:,}", help="IAD cases with at least one Sustained finding")
    with col4:
        st.metric("Sustained %", f"{sustained_pct:.1f}%", help="Share of unique IAD cases with Sustained finding")
    with col5:
        st.metric("Allegation rows", f"{len(data):,}", help="Total rows (officer/allegation); for reference")

    # ---- Charts (all by unique IAD cases) ----
    st.markdown('<p class="section-title">Complaints over time</p>', unsafe_allow_html=True)
    by_year = data.groupby("year_received", dropna=False).agg(
        unique_iads=("ia_no", "nunique"),
    ).reset_index()
    by_year = by_year[by_year["year_received"].notna()].sort_values("year_received")
    fig_time = px.bar(
        by_year, x="year_received", y="unique_iads",
        labels={"year_received": "Year received", "unique_iads": "Unique IAD cases"},
        color_discrete_sequence=[COLORS["accent_soft"]],
    )
    fig_time.update_layout(margin=dict(t=24, b=40), xaxis=dict(dtick=1), showlegend=False)
    _chart_layout(fig_time)
    st.plotly_chart(fig_time, use_container_width=True)

    st.markdown('<p class="section-title">Allegation types (unique IAD cases)</p>', unsafe_allow_html=True)
    alg_data = data.loc[data["allegation_normalized"] != ""]
    alg = alg_data.groupby("allegation_normalized")["ia_no"].nunique().sort_values(ascending=False).head(12)
    alg_df = alg.reset_index()
    alg_df.columns = ["allegation_type", "unique_iads"]
    fig_alg = px.bar(
        alg_df, x="unique_iads", y="allegation_type", orientation="h",
        labels={"unique_iads": "Unique IAD cases", "allegation_type": "Allegation type"},
        color_discrete_sequence=[COLORS["secondary"]],
    )
    fig_alg.update_layout(margin=dict(t=24, b=40), yaxis=dict(autorange="reversed"), showlegend=False)
    _chart_layout(fig_alg, height=400)
    st.plotly_chart(fig_alg, use_container_width=True)

    st.markdown('<p class="section-title">Finding and disposition (unique IAD cases)</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        finding_iads = data.assign(finding=data["finding_x"].replace("", "Unknown")).groupby("finding")["ia_no"].nunique()
        fig_find = px.pie(
            values=finding_iads.values, names=finding_iads.index,
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig_find.update_layout(margin=dict(t=24, b=24), showlegend=True, legend=dict(orientation="h"))
        _chart_layout(fig_find)
        st.plotly_chart(fig_find, use_container_width=True)
    with c2:
        disp_iads = data.assign(disposition=data["disposition_x"].replace("", "Unknown")).groupby("disposition")["ia_no"].nunique()
        fig_disp = px.pie(
            values=disp_iads.values, names=disp_iads.index,
            color_discrete_sequence=px.colors.sequential.Greens_r,
        )
        fig_disp.update_layout(margin=dict(t=24, b=24), showlegend=True, legend=dict(orientation="h"))
        _chart_layout(fig_disp)
        st.plotly_chart(fig_disp, use_container_width=True)

    st.markdown('<p class="section-title">Youth-related vs other (unique IAD cases by allegation type)</p>', unsafe_allow_html=True)
    youth_data = data[(data["label"] == "YES") & (data["allegation_normalized"] != "") & (data["allegation_normalized"].notna())]
    other_data = data[(data["label"] == "NO") & (data["allegation_normalized"] != "") & (data["allegation_normalized"].notna())]
    youth_alg = youth_data.groupby("allegation_normalized")["ia_no"].nunique().sort_values(ascending=False).head(10)
    other_alg = other_data.groupby("allegation_normalized")["ia_no"].nunique().sort_values(ascending=False).head(10)
    col_a, col_b = st.columns(2)
    with col_a:
        if not youth_alg.empty:
            youth_df = youth_alg.reset_index()
            youth_df.columns = ["allegation", "unique_iads"]
            fig_y = px.bar(
                youth_df, x="unique_iads", y="allegation", orientation="h",
                labels={"unique_iads": "Unique IAD cases", "allegation": "Allegation"}, title="Youth-related",
                color_discrete_sequence=[COLORS["youth"]],
            )
            fig_y.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=36, b=40))
            _chart_layout(fig_y, height=340)
            st.plotly_chart(fig_y, use_container_width=True)
        else:
            st.info("No youth-related IAD cases in current filters.")
    with col_b:
        if not other_alg.empty:
            other_df = other_alg.reset_index()
            other_df.columns = ["allegation", "unique_iads"]
            fig_o = px.bar(
                other_df, x="unique_iads", y="allegation", orientation="h",
                labels={"unique_iads": "Unique IAD cases", "allegation": "Allegation"}, title="Not youth-related",
                color_discrete_sequence=[COLORS["adult"]],
            )
            fig_o.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=36, b=40))
            _chart_layout(fig_o, height=340)
            st.plotly_chart(fig_o, use_container_width=True)

    st.markdown('<p class="section-title">Officer rank (unique IAD cases per rank)</p>', unsafe_allow_html=True)
    rank_iads = data.assign(rank=data["rank_x"].replace("", "Unknown")).groupby("rank")["ia_no"].nunique()
    rank_iads = rank_iads[rank_iads.index != "Unknown"] if "Unknown" in rank_iads.index else rank_iads
    rank_df = rank_iads.reset_index()
    rank_df.columns = ["rank", "unique_iads"]
    fig_rank = px.bar(
        rank_df, x="rank", y="unique_iads",
        labels={"rank": "Rank", "unique_iads": "Unique IAD cases"}, color_discrete_sequence=[COLORS["neutral"]],
    )
    fig_rank.update_layout(margin=dict(t=24, b=60), xaxis_tickangle=-45)
    _chart_layout(fig_rank, height=360)
    st.plotly_chart(fig_rank, use_container_width=True)

    # Missing entries (filtered data)
    missing_allegation = (data["allegation_x"].isna() | (data["allegation_x"].astype(str).str.strip().isin(["", "nan"]))).sum()
    missing_finding = (data["finding_x"].isna() | (data["finding_x"].astype(str).str.strip().isin(["", "nan"]))).sum()
    missing_disposition = (data["disposition_x"].isna() | (data["disposition_x"].astype(str).str.strip().isin(["", "nan"]))).sum()
    missing_rank = (data["rank_x"].isna() | (data["rank_x"].astype(str).str.strip().isin(["", "nan"]))).sum()
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p class="footer">Data: Boston IAD extracted records with youth labels. Use the sidebar to filter by year, incident type, allegation, and finding.</p>'
        f'<p class="footer" style="margin-top: 0.25rem;">Missing entries (current view): {missing_allegation:,} with no allegation type; {missing_finding:,} with no finding; {missing_disposition:,} with no disposition; {missing_rank:,} with no officer rank.</p>',
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
