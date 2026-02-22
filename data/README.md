# Data Directory

Place CSV datasets here so the Justice Lens dashboard can load them. Each page expects specific file names; optional files add extra features.

---

## Required Files (by page)

### Police Misconduct Reports

| File | Description |
|------|-------------|
| **`iad_extracted_with_youth_labels.csv`** | Boston Police IAD (Internal Affairs Division) complaints with youth-related labels, 2011–2020. |

**Expected columns (among others):** `received_date_x`, `occurred_date_x`, `incident_type_x`, `allegation_x`, `finding_x`, `disposition_x`, `rank_x`, `label` (youth label).  
If this file is missing, the Police Misconduct page shows a clear message and does not crash.

---

### Boston Youth Arrests

| File | Description |
|------|-------------|
| **`arrests_clean.csv`** | Arrest records with juvenile/adult and district/year info. |

**Expected columns (among others):** `year`, `district_name`, `is_juvenile`. Optional: `school_hours`.  
The app also looks for `pages/arrests_clean.csv` if the file is not in `data/`.

---

### Incident Reports

| File | Description |
|------|-------------|
| **`ir_fall_2025_cleaned.csv`** | Cleaned incident report data for Fall 2025. |

**Expected columns (among others):** `Date`, `Officer Name`, `Badge Number`, `Event District`.  
Optional: **`bpd_complaints_cleaned.csv`** — BPD complaints with `officer_name` and `finding` (e.g. “Sustained”). When present, the app can show complaint counts per officer.

---

## Summary

| File | Used by | Required? |
|------|---------|-----------|
| `iad_extracted_with_youth_labels.csv` | Police Misconduct | Yes |
| `arrests_clean.csv` | Youth Arrests | Yes |
| `ir_fall_2025_cleaned.csv` | Incident Reports | Yes |
| `bpd_complaints_cleaned.csv` | Incident Reports (IAD link) | No |

After adding or updating files, refresh the Streamlit app (or clear cache) to see changes.
