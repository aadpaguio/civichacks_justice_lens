"""
Police Misconduct Reports — Boston IAD data with youth labels.
"""
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from shared_styles import inject_css, chart_layout, COLORS, sidebar_page_links

# Page config
st.set_page_config(page_title="Police Misconduct Reports", layout="wide", initial_sidebar_state="expanded")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "iad_extracted_with_youth_labels.csv"

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
        <p>Boston Police Department — Internal Affairs Division (IAD) · Complaints with youth-related labels · 2011–2020. NOTE: Data from 2019 is missing</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        st.warning("No data loaded.")
        return

    # ---- Sidebar filters (data is already 2011-2020) ----
    with st.sidebar:
        sidebar_page_links()
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
    fig_time.update_layout(title=dict(text=""), margin=dict(t=24, b=40), xaxis=dict(dtick=1), showlegend=False)
    chart_layout(fig_time)
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
    fig_alg.update_layout(title=dict(text=""), margin=dict(t=24, b=40), yaxis=dict(autorange="reversed"), showlegend=False)
    chart_layout(fig_alg, height=400)
    st.plotly_chart(fig_alg, use_container_width=True)

    st.markdown('<p class="section-title">Finding and disposition (unique IAD cases)</p>', unsafe_allow_html=True)
    st.caption("Two outcome fields: **Finding** = investigative result (e.g. Sustained, Exonerated); **Disposition** = formal administrative outcome. Each pie shows how many unique IAD cases have that value (a case can appear in more than one slice if it has multiple officers/outcomes).")
    c1, c2 = st.columns(2)
    with c1:
        finding_iads = data.assign(finding=data["finding_x"].replace("", "Unknown")).groupby("finding")["ia_no"].nunique()
        fig_find = px.pie(
            values=finding_iads.values, names=finding_iads.index,
            color_discrete_sequence=px.colors.sequential.Blues_r,
            title="By finding (investigative result)",
        )
        fig_find.update_layout(margin=dict(t=48, b=24), showlegend=True, legend=dict(orientation="h"))
        chart_layout(fig_find)
        st.plotly_chart(fig_find, use_container_width=True)
    with c2:
        disp_iads = data.assign(disposition=data["disposition_x"].replace("", "Unknown")).groupby("disposition")["ia_no"].nunique()
        fig_disp = px.pie(
            values=disp_iads.values, names=disp_iads.index,
            color_discrete_sequence=px.colors.sequential.Greens_r,
            title="By disposition (administrative outcome)",
        )
        fig_disp.update_layout(margin=dict(t=48, b=24), showlegend=True, legend=dict(orientation="h"))
        chart_layout(fig_disp)
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
            fig_y.update_layout(
                yaxis=dict(autorange="reversed", automargin=True),
                margin=dict(t=36, b=56, l=220),
                xaxis_title_standoff=12,
            )
            chart_layout(fig_y, height=340)
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
            fig_o.update_layout(
                yaxis=dict(autorange="reversed", automargin=True),
                margin=dict(t=36, b=56, l=220),
                xaxis_title_standoff=12,
            )
            chart_layout(fig_o, height=340)
            st.plotly_chart(fig_o, use_container_width=True)

    st.markdown('<p class="section-title">Officer rank (unique IAD cases per rank)</p>', unsafe_allow_html=True)
    rank_iads = data.assign(rank=data["rank_x"].replace("", "Unknown")).groupby("rank")["ia_no"].nunique()
    # Drop Unknown, NaN, and "nan" so they don't show as categories
    rank_df = rank_iads.reset_index()
    rank_df.columns = ["rank", "unique_iads"]
    rank_df = rank_df[
        rank_df["rank"].notna()
        & (rank_df["rank"].astype(str).str.strip().str.lower() != "nan")
        & (rank_df["rank"].astype(str).str.strip() != "")
        & (rank_df["rank"] != "Unknown")
    ]
    rank_df = rank_df.sort_values("unique_iads", ascending=False)
    fig_rank = px.bar(
        rank_df, x="rank", y="unique_iads",
        labels={"rank": "Rank", "unique_iads": "Unique IAD cases"},
        color_discrete_sequence=[COLORS["neutral"]],
    )
    fig_rank.update_layout(title=dict(text=""), margin=dict(t=24, b=60), xaxis_tickangle=-45)
    chart_layout(fig_rank, height=360)
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
