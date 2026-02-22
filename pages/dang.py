import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Colors: adult #1f77b4, juvenile #d62728
COLOR_ADULT = "#1f77b4"
COLOR_JUVENILE = "#d62728"

DATA_PATH = Path(__file__).parent.parent / "data" / "arrests_clean.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    # Ensure is_juvenile is boolean
    if "is_juvenile" in df.columns:
        df["is_juvenile"] = df["is_juvenile"].map(
            lambda x: x is True or (isinstance(x, str) and x.strip().upper() == "TRUE")
        )
    # Ensure year is numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def main():
    df_raw = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")

    view_mode = st.sidebar.radio(
        "Population",
        options=["All Arrests", "Juvenile Only", "Adult Only"],
        index=0,
    )

    year_min = int(df_raw["year"].min()) if df_raw["year"].notna().any() else 2020
    year_max = int(df_raw["year"].max()) if df_raw["year"].notna().any() else 2025
    year_min = max(2020, year_min)
    year_max = min(2025, year_max)
    year_range = st.sidebar.slider(
        "Year range",
        min_value=2020,
        max_value=2025,
        value=(year_min, year_max),
    )

    district_options = [
        d for d in df_raw["district_name"].dropna().unique().tolist()
        if str(d).strip() != "Unknown"
    ]
    district_options = sorted(district_options)
    selected_districts = st.sidebar.multiselect(
        "District",
        options=district_options,
        default=district_options,
    )

    # Apply filters: year, district (options exclude Unknown), then view mode
    df = df_raw.copy()
    df = df[df["year"].between(year_range[0], year_range[1])]
    df = df[df["district_name"].isin(selected_districts)]

    if view_mode == "Juvenile Only":
        df = df[df["is_juvenile"] == True]
    elif view_mode == "Adult Only":
        df = df[df["is_juvenile"] == False]

    total_count = len(df)
    juvenile_count = int(df["is_juvenile"].sum()) if "is_juvenile" in df.columns else 0
    pct_juvenile = (100.0 * juvenile_count / total_count) if total_count else 0
    most_affected = (
        df[df["is_juvenile"] == True]["district_name"]
        .value_counts()
        .index[0]
        if (df["is_juvenile"] == True).any() and "district_name" in df.columns
        else "—"
    )

    # --- MAIN PAGE ---
    st.title("Boston Youth Arrests Analysis")
    st.caption("Source: Boston Police Index, 2020–2025")
    st.divider()

    # Section 1 — Overview metrics
    st.subheader("Overview")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Arrests", f"{total_count:,}")
    with m2:
        st.metric("Juvenile Arrests", f"{juvenile_count:,}")
    with m3:
        st.metric("% Juvenile", f"{pct_juvenile:.1f}%")
    with m4:
        st.metric("Most Affected District", str(most_affected))
    st.divider()

    # Section 2 — Arrests by District (stacked bar)
    st.subheader("Where: Arrests by District")
    df_dist = df[df["district_name"].notna()].copy()
    df_dist["juvenile_label"] = df_dist["is_juvenile"].map(lambda x: "Juvenile" if x else "Adult")
    dist_counts = (
        df_dist.groupby(["district_name", "juvenile_label"], dropna=False)
        .size()
        .reset_index(name="count")
    )
    if not dist_counts.empty:
        fig_dist = px.bar(
            dist_counts,
            x="count",
            y="district_name",
            color="juvenile_label",
            orientation="h",
            color_discrete_map={"Adult": COLOR_ADULT, "Juvenile": COLOR_JUVENILE},
            title="Arrests by District",
            barmode="stack",
        )
        fig_dist.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No district data for current filters.")
    st.divider()

    # Section 3 — Demographics (3 columns)
    st.subheader("Who: Demographics")
    c1, c2, c3 = st.columns(3)

    with c1:
        race_counts = df.groupby(["race_desc", "is_juvenile"]).size().reset_index(name="count")
        race_counts["juvenile_label"] = race_counts["is_juvenile"].map(lambda x: "Juvenile" if x else "Adult")
        if not race_counts.empty:
            fig_race = px.bar(
                race_counts,
                x="count",
                y="race_desc",
                color="juvenile_label",
                orientation="h",
                color_discrete_map={"Adult": COLOR_ADULT, "Juvenile": COLOR_JUVENILE},
                title="Race breakdown",
            )
            fig_race.update_layout(yaxis={"categoryorder": "total ascending"}, height=300)
            st.plotly_chart(fig_race, use_container_width=True)
        else:
            st.write("No data")

    with c2:
        df_juv = df[(df["is_juvenile"] == True) & (df["age"].between(10, 18))]
        if not df_juv.empty and df_juv["age"].notna().any():
            fig_age = px.histogram(
                df_juv,
                x="age",
                nbins=9,
                title="Age Distribution of Juvenile Arrests",
                color_discrete_sequence=[COLOR_JUVENILE],
            )
            fig_age.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.write("No juvenile age data (10–18)")

    with c3:
        gender_counts = df.groupby("gender_desc", dropna=False).size().reset_index(name="count")
        if not gender_counts.empty:
            fig_gender = px.pie(
                gender_counts,
                values="count",
                names="gender_desc",
                title="Gender breakdown",
            )
            fig_gender.update_layout(height=300)
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.write("No data")
    st.divider()

    # Section 4 — Time patterns
    st.subheader("When: Time Patterns")
    t1, t2 = st.columns(2)

    with t1:
        year_counts = df.groupby(["year", "is_juvenile"]).size().reset_index(name="count")
        year_counts["juvenile_label"] = year_counts["is_juvenile"].map(lambda x: "Juvenile" if x else "Adult")
        if not year_counts.empty:
            fig_year = px.line(
                year_counts,
                x="year",
                y="count",
                color="juvenile_label",
                color_discrete_map={"Adult": COLOR_ADULT, "Juvenile": COLOR_JUVENILE},
                title="Arrest Trend Over Time",
            )
            fig_year.update_layout(height=350)
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.write("No data")

    with t2:
        time_order = ["Morning", "Afternoon", "Evening", "Night"]
        df_time = df[df["time_of_day"].notna()].copy()
        df_time["juvenile_label"] = df_time["is_juvenile"].map(lambda x: "Juvenile" if x else "Adult")
        time_counts = df_time.groupby(["time_of_day", "juvenile_label"]).size().reset_index(name="count")
        time_counts["time_of_day"] = pd.Categorical(time_counts["time_of_day"], categories=time_order, ordered=True)
        time_counts = time_counts.sort_values("time_of_day")
        if not time_counts.empty:
            fig_time = px.bar(
                time_counts,
                x="time_of_day",
                y="count",
                color="juvenile_label",
                color_discrete_map={"Adult": COLOR_ADULT, "Juvenile": COLOR_JUVENILE},
                title="Arrests by Time of Day",
                barmode="group",
            )
            fig_time.update_layout(height=350, xaxis={"categoryorder": "array", "categoryarray": time_order})
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.write("No data")
    st.divider()

    # Section 5 — Charge types
    st.subheader("What: Charge Types")
    s1, s2 = st.columns(2)

    with s1:
        sev_df = df[df["charge_severity"].notna()].copy()
        sev_df["juvenile_label"] = sev_df["is_juvenile"].map(lambda x: "Juvenile" if x else "Adult")
        sev_counts = sev_df.groupby(["charge_severity", "juvenile_label"]).size().reset_index(name="count")
        if not sev_counts.empty:
            fig_sev = px.bar(
                sev_counts,
                x="charge_severity",
                y="count",
                color="juvenile_label",
                barmode="group",
                color_discrete_map={"Adult": COLOR_ADULT, "Juvenile": COLOR_JUVENILE},
                title="Charge Severity (Juvenile vs Adult)",
            )
            fig_sev.update_layout(height=350)
            st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.write("No data")

    with s2:
        top_charges = df["charge_desc"].value_counts().head(10).reset_index()
        top_charges.columns = ["charge_desc", "count"]
        if not top_charges.empty:
            fig_charge = px.bar(
                top_charges,
                x="count",
                y="charge_desc",
                orientation="h",
                title="Top 10 Charges",
                color_discrete_sequence=[COLOR_ADULT],
            )
            fig_charge.update_layout(yaxis={"categoryorder": "total ascending"}, height=350)
            st.plotly_chart(fig_charge, use_container_width=True)
        else:
            st.write("No data")
    st.divider()

    # Section 6 — School hours
    st.subheader("School Hours")
    df_juv_only = df[df["is_juvenile"] == True]
    juv_total = len(df_juv_only)
    if juv_total == 0 or "school_hours" not in df_juv_only.columns:
        juv_school = 0
    else:
        sh = df_juv_only["school_hours"]
        if sh.dtype == bool:
            juv_school = int(sh.sum())
        else:
            juv_school = (sh.astype(str).str.strip().str.upper() == "TRUE").sum()
    pct_school = (100.0 * juv_school / juv_total) if juv_total else 0
    st.metric(
        "Juvenile arrests during school hours (Mon–Fri 8am–3pm)",
        f"{pct_school:.1f}%",
    )

    df_juv_dist = df_juv_only[df_juv_only["district_name"].notna() & (df_juv_only["district_name"].astype(str).str.strip() != "Unknown")]
    if not df_juv_dist.empty and "school_hours" in df_juv_dist.columns:
        sh = df_juv_dist["school_hours"]
        is_school = sh.astype(str).str.strip().str.upper() == "TRUE" if sh.dtype != bool else sh
        df_juv_dist = df_juv_dist.copy()
        df_juv_dist["school_hours_bool"] = is_school
        rate_by_dist = (
            df_juv_dist.groupby("district_name")["school_hours_bool"]
            .agg(["sum", "count"])
            .assign(rate=lambda x: 100.0 * x["sum"] / x["count"])
            .sort_values("rate", ascending=False)
            .reset_index()
        )
        fig_school = px.bar(
            rate_by_dist,
            x="district_name",
            y="rate",
            title="School Hours Arrest Rate by District (Juvenile Only)",
            labels={"rate": "% during school hours", "district_name": "District"},
        )
        fig_school.update_layout(xaxis_tickangle=-45, height=350)
        st.plotly_chart(fig_school, use_container_width=True)
    st.caption("School hours defined as Monday–Friday, 8am–3pm.")
    st.divider()

    st.caption(
        "Note: 9.4% of arrests have no district recorded and are excluded from district-level charts. "
        "Missing district data has increased from 263 records in 2020 to 2,637 in 2024."
    )


if __name__ == "__main__":
    main()
