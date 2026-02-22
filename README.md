# Justice Lens

**Justice Lens** is a civic data dashboard for exploring Boston-area criminal justice and police accountability data. It visualizes Internal Affairs (IAD) complaints, youth arrests, and incident reports in one place with filters and interactive charts.

Built for [Civic Hacks](https://civichacks.org/) to make public data easier to explore and understand.

---

## Features

- **Police Misconduct Reports** — Boston Police Department IAD complaints (2011–2020) with youth-related labels. Filter by year, incident type, and allegation; view trends and breakdowns.
- **Boston Youth Arrests** — Arrest data with juvenile vs. adult breakdowns, district and year filters, and school-hours analysis.
- **Incident Reports** — Fall 2025 incident data with optional linkage to BPD complaint history by officer.
- **Data** — Placeholder page for additional datasets or uploads.

All pages share a consistent layout and styling (sidebar navigation, filters, and responsive charts).

---

## Tech Stack

- **Python 3.12+**
- **Streamlit** — Web app framework
- **Pandas** — Data loading and manipulation
- **Plotly** — Interactive charts

---

## Quick Start

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd civichacks_justice_lens
```

### 2. Set up the environment

**Option A — Virtual environment (recommended)**

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Option B — uv**

```bash
uv sync
```

### 3. Run the app

**Using the run script (uses `.venv` automatically):**

```bash
./run_app.sh
```

**Or manually with Streamlit:**

```bash
# If using venv:
source .venv/bin/activate
streamlit run app.py
```

Then open **http://localhost:8501** (or the URL Streamlit prints) in your browser.

---

## Data

Place CSV files in the **`data/`** folder. See **[data/README.md](data/README.md)** for required and optional datasets per page.

| Page                 | Required file(s)                    | Optional |
|----------------------|-------------------------------------|----------|
| Police Misconduct    | `iad_extracted_with_youth_labels.csv` | —        |
| Youth Arrests        | `arrests_clean.csv`                 | —        |
| Incident Reports     | `ir_fall_2025_cleaned.csv`          | `bpd_complaints_cleaned.csv` |

If a required file is missing, the corresponding page will show a clear message instead of crashing.

---

## Project Structure

```
civichacks_justice_lens/
├── app.py              # Entry point (redirects to first page)
├── run_app.sh          # Run Streamlit with project venv
├── shared_styles.py    # Shared CSS and chart defaults
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project metadata (uv/pip)
├── data/               # CSV datasets (see data/README.md)
├── pages/              # Streamlit multi-page app
│   ├── police_misconduct.py
│   ├── youth_arrests.py
│   ├── incident_reports.py
│   └── edward.py       # Data placeholder page
└── docs/               # Additional documentation
    └── DOCUMENTATION.md
```

---

## Documentation

- **[data/README.md](data/README.md)** — Data files and expected columns
- **[docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)** — Detailed docs: pages, data sources, and development notes

---

## License

See repository license. Data used in this project may have its own terms (e.g., City of Boston open data).
