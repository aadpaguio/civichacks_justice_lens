"""
Dashboard for cleaned IR Fall 2025 incident data.
Professional, distinctive design.
"""
import os
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Justice Lens — IR Dashboard",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom theme: dark slate + amber accent — stands out, feels serious and civic
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Override Streamlit defaults */
.stApp { background: linear-gradient(180deg, #0c1222 0%, #111827 50%, #0f172a 100%); }
.main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }
h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* Hide default Streamlit branding for cleaner look */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Hero header */
.hero {
    font-family: 'Plus Jakarta Sans', sans-serif;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(245, 158, 11, 0.25);
}
.hero h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.02em;
    margin: 0;
}
.hero .tagline {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-top: 0.35rem;
    font-weight: 500;
}
.hero .accent-bar {
    width: 48px;
    height: 3px;
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
    border-radius: 2px;
    margin-top: 0.75rem;
}

/* Metric cards — custom cards with accent */
.metric-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-left: 3px solid #f59e0b;
    border-radius: 10px;
    padding: 1.25rem 1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.metric-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 0.25rem;
}
.metric-card .value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.02em;
}

/* Section headers */
.section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #cbd5e1;
    margin: 1.75rem 0 0.75rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.15);
}
.chart-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.15);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #0c1222 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.1);
}
[data-testid="stSidebar"] .stMarkdown { color: #94a3b8; }
[data-testid="stSidebar"] h2 { color: #e2e8f0 !important; font-size: 0.9rem !important; }
[data-testid="stSidebar"] .stCaption { color: #64748b !important; }

/* Dataframe styling */
div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.12);
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.15);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Load data (cached)
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "ir_fall_2025_cleaned.csv")
    df = pd.read_csv(path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df_raw = load_data()
df = df_raw.copy()

# Sidebar
with st.sidebar:
    st.markdown("### ◉ Justice Lens")
    st.caption("Incident reports · Fall 2025")
    st.divider()
    st.markdown("**Filters**")
    st.caption("Narrow the dataset")

if "Date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Date"]):
    df = df.dropna(subset=["Date"])
    min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        df = df[(df["Date"].dt.date >= date_range[0]) & (df["Date"].dt.date <= date_range[1])]
    elif hasattr(date_range, "year"):
        df = df[df["Date"].dt.date == date_range]
else:
    st.sidebar.info("Date column missing or not parsed.")

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
    '<div class="hero">'
    '<h1>Incident Reports</h1>'
    '<p class="tagline">Cleaned IR Fall 2025 · Explore by date, district, and force type</p>'
    '<div class="accent-bar"></div>'
    '</div>',
    unsafe_allow_html=True,
)

# Metric cards (custom HTML for full control)
n_incidents = len(df)
n_officers = df["Officer Name"].nunique() if "Officer Name" in df.columns else 0
n_districts = df["Event District"].nunique() if "Event District" in df.columns else 0
with_weapon = (df["Weapon/Force Involved"].notna() & (df["Weapon/Force Involved"].astype(str).str.len() > 0)).sum() if "Weapon/Force Involved" in df.columns else 0
total_charges = int(df["Total Charges"].sum()) if "Total Charges" in df.columns else 0

m1, m2, m3, m4, m5 = st.columns(5)
for col, (label, value) in zip(
    [m1, m2, m3, m4, m5],
    [
        ("Total incidents", f"{n_incidents:,}"),
        ("Unique officers", f"{n_officers:,}"),
        ("Districts", f"{n_districts}"),
        ("Weapon/force", f"{with_weapon:,}"),
        ("Total charges", f"{total_charges:,}"),
    ],
):
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# Charts
st.markdown('<p class="section-title">Trends & distribution</p>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown("**Incidents by date**")
    if "Date" in df.columns and len(df) > 0:
        daily = df.set_index("Date").resample("D").size().reset_index(name="Incidents")
        st.line_chart(daily.set_index("Date"))
    else:
        st.info("No date data to plot.")

with c2:
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

# Heatmap: District × Hour (or Day of week)
st.markdown('<p class="section-title">Heatmap — incidents by district & time</p>', unsafe_allow_html=True)
heat_df = df.copy()
if "Date" in heat_df.columns and "Event District" in heat_df.columns:
    heat_df["Date"] = pd.to_datetime(heat_df["Date"], errors="coerce")
    heat_df = heat_df.dropna(subset=["Date", "Event District"])
    heat_df["hour"] = heat_df["Date"].dt.hour
    heat_df["district"] = heat_df["Event District"].astype(str)
    heat_df = heat_df[~heat_df["district"].isin(["", "nan"])]
    agg = heat_df.groupby(["district", "hour"]).size().reset_index(name="incidents")
    if len(agg) > 0:
        district_order = agg.groupby("district")["incidents"].sum().sort_values(ascending=False).index.tolist()
        heat = (
            alt.Chart(agg)
            .mark_rect()
            .encode(
                x=alt.X("hour:O", title="Hour of day", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("district:N", title="District", sort=district_order),
                color=alt.Color("incidents:Q", title="Incidents", scale=alt.Scale(scheme="oranges")),
                tooltip=["district", "hour", "incidents"],
            )
            .properties(height=400)
            .configure_axis(labelColor="#94a3b8", titleColor="#cbd5e1")
            .configure_legend(labelColor="#94a3b8", titleColor="#cbd5e1")
        )
        st.altair_chart(heat, use_container_width=True)
    else:
        st.caption("No data for heatmap.")
else:
    st.caption("Date and District required for heatmap.")

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
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, map_style="dark", tooltip=False))
        except Exception:
            map_df = map_df.rename(columns={"Offense Latitude": "lat", "Offense Longitude": "lon"})
            st.map(map_df, use_container_width=True)
    else:
        st.caption("No valid coordinates to display.")

# Data table
st.markdown('<p class="section-title">Records</p>', unsafe_allow_html=True)
display_cols = [c for c in ["Date", "Time", "Officer Name", "Event District", "Event Street Address", "Weapon/Force Involved", "Suspect Count", "Total Charges", "Charge I"] if c in df.columns]
table_df = df[display_cols] if display_cols else df
st.dataframe(table_df.head(1000), use_container_width=True, hide_index=True)
st.caption(f"First 1,000 of {len(df):,} rows. Use the sidebar to filter.")
