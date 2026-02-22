"""
Dashboard for cleaned IR Fall 2025 incident data.
Uses shared Justice Lens styling (arnald-based). Connected to IAD complaints data when available (by officer name).
"""
import os
import streamlit as st
import pandas as pd
from shared_styles import inject_css, hero_html, sidebar_page_links

st.set_page_config(
    page_title="Justice Lens — IR Dashboard",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# Load data (cached) — incident CSV is in pages/; add Officer = Name # Badge
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, "..", "data")
    path = os.path.join(data_dir, "ir_fall_2025_cleaned.csv")
    df = pd.read_csv(path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if "Officer Name" in df.columns and "Badge Number" in df.columns:
        df["Officer"] = (
            df["Officer Name"].astype(str).str.strip()
            + " #"
            + df["Badge Number"].astype(str).str.strip()
        )
    return df


@st.cache_data
def load_iad_lookups():
    """Load cleaned BPD complaints; return (total_complaints_per_officer, sustained_complaints_per_officer) by normalized name."""
    base = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, "..", "data")
    cleaned_path = os.path.join(data_dir, "bpd_complaints_cleaned.csv")
    if not os.path.exists(cleaned_path):
        return None, None
    cp = pd.read_csv(cleaned_path)
    if "officer_name" not in cp.columns or cp["officer_name"].empty:
        return None, None

    def norm(s):
        return " ".join(str(s).lower().strip().split())

    cp = cp.dropna(subset=["officer_name"])
    cp["key"] = cp["officer_name"].astype(str).apply(norm)
    total = cp["key"].value_counts().to_dict()
    sustained = {}
    if "finding" in cp.columns:
        sustained = cp[cp["finding"] == "Sustained"]["key"].value_counts().to_dict()
    return total, sustained


def normalize_name(s):
    """Same normalization as IAD lookup for matching."""
    return " ".join(str(s).lower().strip().split())


df_raw = load_data()
df = df_raw.copy()
iad_lookup, iad_sustained_lookup = load_iad_lookups()

# Sidebar
with st.sidebar:
    sidebar_page_links()
    st.markdown("### ◉ Justice Lens")
    st.caption("Incident reports · Fall 2025")
    st.divider()
    st.markdown("**Filters**")
    st.caption("Narrow the dataset")

if "Event District" in df.columns:
    districts = ["All"] + sorted([x for x in df["Event District"].dropna().astype(str).unique() if x and x != "nan"])
    sel_district = st.sidebar.selectbox("Event District", districts)
    if sel_district != "All":
        df = df[df["Event District"].astype(str) == sel_district]

if "Weapon/Force Involved" in df.columns:
    weapons = ["All"] + sorted([x for x in df["Weapon/Force Involved"].dropna().astype(str).unique() if x and x != "nan"])
    sel_weapon = st.sidebar.selectbox("Weapon/Force Involved", weapons)
    if sel_weapon != "All":
        df = df[df["Weapon/Force Involved"].astype(str) == sel_weapon]

st.sidebar.divider()
st.sidebar.caption(f"Showing **{len(df):,}** of {len(df_raw):,} records")

# Hero
st.markdown(
    hero_html("Incident Reports", "Cleaned IR Fall 2025 · Explore by date, district, and force type"),
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# Metrics (shared styling via st.metric)
n_incidents = len(df)
n_officers = df["Officer Name"].nunique() if "Officer Name" in df.columns else 0
n_districts = df["Event District"].nunique() if "Event District" in df.columns else 0
with_weapon = (df["Weapon/Force Involved"].notna() & (df["Weapon/Force Involved"].astype(str).str.len() > 0)).sum() if "Weapon/Force Involved" in df.columns else 0
total_charges = int(df["Total Charges"].sum()) if "Total Charges" in df.columns else 0
# Officers with ≥1 IAD complaint and with ≥1 sustained (when complaints data is loaded)
officers_with_complaints = 0
officers_with_sustained = 0
if iad_lookup and "Officer Name" in df.columns:
    unique_names = df["Officer Name"].astype(str).str.strip().unique()
    for n in unique_names:
        if not n or n.lower() == "nan":
            continue
        k = normalize_name(n)
        if iad_lookup.get(k, 0) >= 1:
            officers_with_complaints += 1
        if iad_sustained_lookup and iad_sustained_lookup.get(k, 0) >= 1:
            officers_with_sustained += 1

metrics = [
    ("Total incidents", f"{n_incidents:,}"),
    ("Unique officers", f"{n_officers:,}"),
    ("Districts", f"{n_districts}"),
    ("Weapon/force", f"{with_weapon:,}"),
    ("Total charges", f"{total_charges:,}"),
]
if iad_lookup:
    metrics.append(("Officers w/ IAD complaint", f"{officers_with_complaints}"))
if iad_sustained_lookup:
    metrics.append(("Officers w/ sustained", f"{officers_with_sustained}"))
m_cols = st.columns(len(metrics))
for col, (label, value) in zip(m_cols, metrics):
    with col:
        st.metric(label, value)

if iad_lookup and n_officers:
    pct = 100 * officers_with_complaints / n_officers
    st.caption(f"**IAD data (2011–2024):** {officers_with_complaints} officers in this dataset have at least one complaint on record ({pct:.0f}% of unique officers). Sustained = complaint was upheld by Internal Affairs.")

# Charts
st.markdown('<p class="section-title">Trends & distribution</p>', unsafe_allow_html=True)
st.markdown("**Incidents by district**")
if "Event District" in df.columns:
    dist_counts = df["Event District"].value_counts().sort_index()
    st.bar_chart(dist_counts)
else:
    st.info("No district data.")

# Weapon/force — exclude empty, none, (none), nan
if "Weapon/Force Involved" in df.columns:
    st.markdown('<p class="section-title">Weapon / force involved</p>', unsafe_allow_html=True)
    wcol = df["Weapon/Force Involved"].astype(str).str.strip()
    skip = {"", "none", "(none)", "nan"}
    weapon_counts = wcol[~wcol.str.lower().isin(skip)].value_counts()
    if len(weapon_counts) > 0:
        w1, w2 = st.columns(2)
        with w1:
            st.bar_chart(weapon_counts.head(15))
        with w2:
            st.dataframe(
                weapon_counts.head(15).reset_index().rename(columns={"index": "Type", "Weapon/Force Involved": "Count"}),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.caption("No weapon/force types to display after filtering.")

# Officers with IAD history — same matching logic, show only badge number
if iad_lookup and "Officer" in df.columns:
    st.markdown('<p class="section-title">Officers with IAD history</p>', unsafe_allow_html=True)
    st.caption("Officers in this incident data who have at least one IAD complaint on record (2011–2024).")
    officer_incidents = df["Officer"].value_counts()
    rows = []
    for officer_display, inc_count in officer_incidents.items():
        name_part = officer_display.split(" #")[0].strip() if " #" in officer_display else officer_display
        badge_part = officer_display.split(" #", 1)[1].strip() if " #" in officer_display else ""
        key = normalize_name(name_part)
        iad_count = iad_lookup.get(key, 0)
        if iad_count < 1:
            continue
        sustained = (iad_sustained_lookup or {}).get(key, 0)
        rows.append({
            "Badge": f"#{badge_part}" if badge_part else "",
            "Incidents": inc_count,
            "IAD complaints": iad_count,
            "Sustained": sustained,
        })
    if rows:
        iad_df = pd.DataFrame(rows).sort_values("IAD complaints", ascending=False).head(20)
        st.dataframe(iad_df, use_container_width=True, hide_index=True)
        pct = 100 * len(rows) / officer_incidents.shape[0] if officer_incidents.shape[0] else 0
        st.caption(f"**{len(rows)}** of **{officer_incidents.shape[0]}** unique officers in this data have at least one IAD complaint on record ({pct:.0f}%).")
    else:
        st.caption("No officers in the current filter have IAD complaints on record.")

# Map — density heatmap style with pydeck
if "Offense Latitude" in df.columns and "Offense Longitude" in df.columns:
    st.markdown('<p class="section-title">Incident locations (density)</p>', unsafe_allow_html=True)
    map_df = df[["Offense Latitude", "Offense Longitude"]].dropna()
    map_df = map_df[(map_df["Offense Latitude"] != 0) | (map_df["Offense Longitude"] != 0)]
    if len(map_df) > 0:
        try:
            import pydeck as pdk
            layer = pdk.Layer(
                "HeatmapLayer",
                data=map_df.rename(columns={"Offense Latitude": "lat", "Offense Longitude": "lon"}),
                get_position="[lon, lat]",
                get_weight=1,
                radius_pixels=60,
                intensity=1,
                threshold=0.5,
            )
            view = pdk.ViewState(latitude=map_df["Offense Latitude"].mean(), longitude=map_df["Offense Longitude"].mean(), zoom=10, pitch=0)
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, map_style="light", tooltip=False))
        except Exception:
            map_df = map_df.rename(columns={"Offense Latitude": "lat", "Offense Longitude": "lon"})
            st.map(map_df, use_container_width=True)
    else:
        st.caption("No valid coordinates to display.")

