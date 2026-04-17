from typing import List, Dict, Any

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="EduShield AI Ultra Pro Dashboard", layout="wide")

REQUIRED_COLUMNS = [
    "Student_ID",
    "Student_Name",
    "Class",
    "Section",
    "Physics_Marks",
    "Chemistry_Marks",
    "Math_Marks",
    "Attendance_Percentage",
    "Homework_Completion_Percentage",
    "Parent_Email",
    "Teacher_Email",
    "Phone_Number",
]


# -----------------------------
# Theme + CSS
# -----------------------------
def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0b1020 0%, #111827 35%, #f8fafc 35%, #f8fafc 100%);
        }
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        .hero-wrap {
            background: linear-gradient(135deg, #111827 0%, #1d4ed8 55%, #0ea5e9 100%);
            color: white;
            padding: 28px 30px;
            border-radius: 24px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
            border: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 18px;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
            line-height: 1.2;
        }
        .hero-sub {
            color: rgba(255,255,255,0.88);
            font-size: 1rem;
            margin-bottom: 0;
        }
        .glass-card {
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 22px;
            padding: 18px;
            box-shadow: 0 8px 26px rgba(15, 23, 42, 0.08);
        }
        .metric-card {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e5e7eb;
            border-radius: 22px;
            padding: 18px 16px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            min-height: 122px;
        }
        .metric-label {
            color: #64748b;
            font-size: 0.92rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .metric-value {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
        }
        .metric-foot {
            color: #475569;
            font-size: 0.85rem;
            margin-top: 8px;
        }
        .alert-card {
            padding: 16px 18px;
            border-radius: 18px;
            margin-bottom: 12px;
            box-shadow: 0 10px 24px rgba(15,23,42,0.08);
            border-left: 8px solid #ef4444;
            background: linear-gradient(180deg, #fff1f2 0%, #ffffff 100%);
        }
        .section-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0.25rem 0 0.75rem 0;
        }
        .soft-box {
            background: white;
            border-radius: 18px;
            padding: 14px 16px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# -----------------------------
# Helpers
# -----------------------------
def validate_columns(df: pd.DataFrame) -> List[str]:
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def load_demo_data() -> pd.DataFrame:
    rows = [
        [1, "Aman", "11", "A", 52, 61, 48, 72, 65, "parent1@example.com", "teacher1@example.com", "9000000001"],
        [2, "Bhavna", "11", "A", 81, 77, 85, 91, 88, "parent2@example.com", "teacher1@example.com", "9000000002"],
        [3, "Charu", "12", "B", 43, 58, 46, 69, 55, "parent3@example.com", "teacher2@example.com", "9000000003"],
        [4, "Dev", "12", "B", 66, 64, 62, 79, 74, "parent4@example.com", "teacher2@example.com", "9000000004"],
        [5, "Eshan", "10", "C", 35, 42, 39, 61, 50, "parent5@example.com", "teacher3@example.com", "9000000005"],
        [6, "Farhan", "10", "C", 76, 74, 72, 82, 81, "parent6@example.com", "teacher3@example.com", "9000000006"],
        [7, "Gauri", "12", "A", 58, 49, 55, 71, 63, "parent7@example.com", "teacher4@example.com", "9000000007"],
        [8, "Harsh", "11", "B", 89, 84, 91, 94, 92, "parent8@example.com", "teacher4@example.com", "9000000008"],
    ]
    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def to_number(val: Any, fallback: float = 0.0) -> float:
    try:
        if pd.isna(val) or val == "":
            return fallback
        return float(val)
    except Exception:
        return fallback


def risk_badge_html(category: str) -> str:
    category = str(category or "Unknown")
    color_map = {
        "High Risk": ("#ef4444", "#fff1f2"),
        "Medium Risk": ("#f59e0b", "#fff7ed"),
        "Low Risk": ("#10b981", "#ecfdf5"),
        "Unknown": ("#6b7280", "#f3f4f6"),
    }
    fg, bg = color_map.get(category, color_map["Unknown"])
    return (
        f"<span style='display:inline-block;padding:0.38rem 0.78rem;border-radius:999px;"
        f"font-weight:800;color:{fg};background:{bg};border:1px solid {fg};'>{category}</span>"
    )


def priority_badge_html(priority: str) -> str:
    priority = str(priority or "Unknown")
    color_map = {
        "Immediate Action": ("#b91c1c", "#fef2f2"),
        "Monitor Closely": ("#b45309", "#fffbeb"),
        "Stable": ("#047857", "#ecfdf5"),
        "Unknown": ("#6b7280", "#f3f4f6"),
    }
    fg, bg = color_map.get(priority, color_map["Unknown"])
    return (
        f"<span style='display:inline-block;padding:0.38rem 0.78rem;border-radius:999px;"
        f"font-weight:800;color:{fg};background:{bg};border:1px solid {fg};'>{priority}</span>"
    )


def gauge_html(value: float, title: str, color: str = "#2563eb") -> str:
    pct = max(0.0, min(100.0, float(value or 0)))
    return f"""
    <div class="soft-box">
      <div style="font-size:14px;color:#64748b;margin-bottom:8px;font-weight:700;">{title}</div>
      <div style="height:16px;background:#e5e7eb;border-radius:999px;overflow:hidden;">
        <div style="width:{pct}%;height:16px;background:{color};border-radius:999px;"></div>
      </div>
      <div style="margin-top:8px;font-size:24px;font-weight:800;color:#0f172a;">{pct:.1f}%</div>
    </div>
    """


def metric_card_html(label: str, value: Any, foot: str = "") -> str:
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-foot">{foot}</div>
    </div>
    """


def hero_html() -> str:
    return """
    <div class="hero-wrap">
      <div class="hero-title">EduShield AI — ULTRA PRO Dashboard</div>
      <p class="hero-sub">Explainable risk intelligence for teachers, intervention planning, parent communication, and executive-level monitoring.</p>
    </div>
    """


def score_style(val: Any) -> str:
    try:
        val = float(val)
        if val >= 40:
            return "background-color: #ef4444; color: white; font-weight: 800"
        if val >= 25:
            return "background-color: #f59e0b; color: white; font-weight: 800"
        return "background-color: #10b981; color: white; font-weight: 800"
    except Exception:
        return ""


def category_style(val: Any) -> str:
    val = str(val)
    if val == "High Risk":
        return "background-color: #fff1f2; color: #b91c1c; font-weight: 800"
    if val == "Medium Risk":
        return "background-color: #fff7ed; color: #b45309; font-weight: 800"
    if val == "Low Risk":
        return "background-color: #ecfdf5; color: #047857; font-weight: 800"
    return ""


def ensure_premium_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    numeric_cols = [
        "Physics_Marks",
        "Chemistry_Marks",
        "Math_Marks",
        "Attendance_Percentage",
        "Homework_Completion_Percentage",
        "Average_Marks",
        "Risk_Score",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Average_Marks" not in df.columns:
        subject_cols = [c for c in ["Physics_Marks", "Chemistry_Marks", "Math_Marks"] if c in df.columns]
        if subject_cols:
            df["Average_Marks"] = df[subject_cols].mean(axis=1).round(2)
        else:
            df["Average_Marks"] = 0.0

    if "Risk_Category" not in df.columns and "Risk_Score" in df.columns:
        def derive_category(score: float) -> str:
            if pd.isna(score):
                return "Unknown"
            if score >= 40:
                return "High Risk"
            if score >= 25:
                return "Medium Risk"
            return "Low Risk"
        df["Risk_Category"] = df["Risk_Score"].apply(derive_category)

    if "Intervention_Priority" not in df.columns:
        def derive_priority(score: float) -> str:
            if pd.isna(score):
                return "Unknown"
            if score >= 40:
                return "Immediate Action"
            if score >= 25:
                return "Monitor Closely"
            return "Stable"
        score_series = df["Risk_Score"] if "Risk_Score" in df.columns else pd.Series([None] * len(df))
        df["Intervention_Priority"] = score_series.apply(derive_priority)

    if "Why_Flagged" not in df.columns:
        def build_reason(row: pd.Series) -> str:
            reasons = []
            avg = row.get("Average_Marks")
            att = row.get("Attendance_Percentage")
            hw = row.get("Homework_Completion_Percentage")
            weak = row.get("Weak_Subject")

            if pd.notna(avg) and avg < 60:
                reasons.append(f"Low average marks ({avg:.1f})")
            if pd.notna(att) and att < 75:
                reasons.append(f"Low attendance ({att:.1f}%)")
            if pd.notna(hw) and hw < 70:
                reasons.append(f"Low homework completion ({hw:.1f}%)")
            if isinstance(weak, str) and weak.strip():
                reasons.append(f"Weakest subject: {weak}")
            return "; ".join(reasons) if reasons else "Stable performance pattern"
        df["Why_Flagged"] = df.apply(build_reason, axis=1)

    if "Risk_Color" not in df.columns:
        color_map = {"High Risk": "#ef4444", "Medium Risk": "#f59e0b", "Low Risk": "#10b981"}
        df["Risk_Color"] = df["Risk_Category"].map(color_map).fillna("#6b7280")

    if "Parent_Message_Draft" not in df.columns:
        def build_parent_msg(row: pd.Series) -> str:
            name = row.get("Student_Name", "Student")
            risk = row.get("Risk_Category", "concern")
            weak = row.get("Weak_Subject", "key subjects")
            reason = row.get("Why_Flagged", "recent academic signals")
            return (
                f"Dear Parent, {name} has been flagged under {risk}. "
                f"Key concern: {reason}. Please support focused revision in {weak} and coordinate with the teacher this week."
            )
        df["Parent_Message_Draft"] = df.apply(build_parent_msg, axis=1)

    if "Suggestion" not in df.columns:
        df["Suggestion"] = "Review weak topics, improve attendance consistency, and follow the teacher intervention plan."

    return df


def build_summary_from_processed(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {
            "total_students": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "average_risk_score": 0.0,
            "most_common_weak_subject": "N/A",
        }
    weak_subject = "N/A"
    if "Weak_Subject" in df.columns and not df["Weak_Subject"].dropna().empty:
        weak_subject = str(df["Weak_Subject"].mode().iloc[0])

    homework_attention_percentage = 0.0
    if "Homework_Completion_Percentage" in df.columns:
        homework_attention_percentage = round(float((df["Homework_Completion_Percentage"] < 70).mean() * 100), 2)

    high_risk_count = int((df["Risk_Category"] == "High Risk").sum()) if "Risk_Category" in df.columns else 0

    return {
        "total_students": int(len(df)),
        "high_risk_count": high_risk_count,
        "medium_risk_count": int((df["Risk_Category"] == "Medium Risk").sum()) if "Risk_Category" in df.columns else 0,
        "low_risk_count": int((df["Risk_Category"] == "Low Risk").sum()) if "Risk_Category" in df.columns else 0,
        "average_risk_score": round(float(df["Risk_Score"].mean()), 2) if "Risk_Score" in df.columns else 0.0,
        "most_common_weak_subject": weak_subject,
        "high_risk_percentage": round((high_risk_count / len(df)) * 100, 2) if len(df) else 0,
        "homework_attention_percentage": homework_attention_percentage,
    }


def build_intervention_report(processed_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Student_ID",
        "Student_Name",
        "Class",
        "Section",
        "Risk_Score",
        "Risk_Category",
        "Intervention_Priority",
        "Weak_Subject",
        "Why_Flagged",
        "Suggestion",
        "Teacher_Email",
        "Parent_Email",
        "Parent_Message_Draft",
    ]
    available = [c for c in cols if c in processed_df.columns]
    if "Risk_Score" in processed_df.columns:
        return processed_df[available].sort_values("Risk_Score", ascending=False)
    return processed_df[available]


def render_alert_cards(df: pd.DataFrame) -> None:
    if df.empty:
        st.success("No high-risk students found.")
        return
    for _, row in df.iterrows():
        st.markdown(
            f"""
            <div class="alert-card">
                <div style="font-size:1.08rem;font-weight:800;color:#991b1b;">🚨 {row.get('Student_Name', 'Student')}</div>
                <div style="margin-top:6px;color:#334155;line-height:1.6;">
                    <b>Class:</b> {row.get('Class', '')}-{row.get('Section', '')}&nbsp;&nbsp;|&nbsp;&nbsp;
                    <b>Risk Score:</b> {row.get('Risk_Score', 'N/A')}&nbsp;&nbsp;|&nbsp;&nbsp;
                    <b>Weak Subject:</b> {row.get('Weak_Subject', 'N/A')}<br>
                    <b>Priority:</b> {row.get('Intervention_Priority', 'N/A')}<br>
                    <b>Why Flagged:</b> {row.get('Why_Flagged', 'N/A')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def styled_dataframe(df: pd.DataFrame, risk_subset: List[str], cat_subset: List[str]):
    styler = df.style
    for col in risk_subset:
        if col in df.columns:
            styler = styler.map(score_style, subset=[col])
    for col in cat_subset:
        if col in df.columns:
            styler = styler.map(category_style, subset=[col])
    return styler


# -----------------------------
# Layout
# -----------------------------
st.markdown(hero_html(), unsafe_allow_html=True)

with st.sidebar:
    st.header("Workflow Connection")
    webhook_url = st.text_input(
        "n8n Production Webhook URL",
        placeholder="https://your-n8n-domain/webhook/student-dashboard-api",
        help="Use the Production URL from an active n8n workflow.",
    )
    timeout_seconds = st.number_input("Request timeout (seconds)", min_value=30, max_value=300, value=120, step=10)
    st.markdown("---")
    st.caption("Use demo data for a quick premium walkthrough.")

st.markdown("<div class='section-title'>1) Upload student CSV or use demo data</div>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
with col2:
    use_demo = st.button("Use Demo Data")

df_input = None
if uploaded_file is not None:
    df_input = pd.read_csv(uploaded_file)
elif use_demo:
    df_input = load_demo_data()

if df_input is None:
    st.info("Upload a CSV or click 'Use Demo Data' to begin.")
    with st.expander("Required CSV columns"):
        st.write(REQUIRED_COLUMNS)
    st.stop()

st.dataframe(df_input, use_container_width=True)

missing_columns = validate_columns(df_input)
if missing_columns:
    st.error("Missing required columns: " + ", ".join(missing_columns))
    st.stop()

csv_bytes = df_input.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download current data as CSV",
    data=csv_bytes,
    file_name="student_input_data.csv",
    mime="text/csv",
)

if "result" not in st.session_state:
    st.session_state["result"] = None

run_clicked = st.button("Run ULTRA PRO Workflow", type="primary")

if run_clicked:
    if not webhook_url.strip():
        st.error("Please paste your n8n Production Webhook URL in the sidebar.")
    else:
        payload = {"students": df_input.to_dict(orient="records")}
        try:
            with st.spinner("Calling n8n webhook and loading premium analytics..."):
                response = requests.post(webhook_url.strip(), json=payload, timeout=timeout_seconds)

            if response.status_code != 200:
                st.error("n8n did not return success.")
                st.code(response.text)
            else:
                st.session_state["result"] = response.json()
        except requests.exceptions.RequestException as exc:
            st.error(f"Network or webhook error: {exc}")
        except ValueError:
            st.error("n8n response was not valid JSON.")
            st.code(response.text if 'response' in locals() else "No response body available.")

result = st.session_state.get("result")
if not result:
    st.warning("No processed workflow output yet. Run the workflow to see analytics.")
    with st.expander("Sample payload Streamlit sends to n8n"):
        st.code(
            '{\n  "students": [\n    {\n      "Student_ID": 1,\n      "Student_Name": "Aman",\n      "Class": "11",\n      "Section": "A",\n      "Physics_Marks": 52,\n      "Chemistry_Marks": 61,\n      "Math_Marks": 48,\n      "Attendance_Percentage": 72,\n      "Homework_Completion_Percentage": 65,\n      "Parent_Email": "parent1@example.com",\n      "Teacher_Email": "teacher1@example.com",\n      "Phone_Number": "9000000001"\n    }\n  ]\n}',
            language="json",
        )
    st.stop()

summary = result.get("summary", {})
processed = result.get("all_students_processed", [])
alerts = result.get("teacher_alert_list", [])
weekly_trend = result.get("weekly_trend", {})

processed_df = ensure_premium_columns(pd.DataFrame(processed))
alerts_df = pd.DataFrame(alerts)

if processed_df.empty:
    st.error("The workflow returned no processed student records.")
    st.stop()

if not summary:
    summary = build_summary_from_processed(processed_df)

# KPI cards
st.markdown("<div class='section-title'>2) Executive KPI Overview</div>", unsafe_allow_html=True)
metric_cols = st.columns(6)
with metric_cols[0]:
    st.markdown(metric_card_html("Total Students", summary.get("total_students", len(processed_df)), "Active students in current dataset"), unsafe_allow_html=True)
with metric_cols[1]:
    st.markdown(metric_card_html("High Risk", summary.get("high_risk_count", 0), "Immediate intervention bucket"), unsafe_allow_html=True)
with metric_cols[2]:
    st.markdown(metric_card_html("Medium Risk", summary.get("medium_risk_count", 0), "Watchlist requiring monitoring"), unsafe_allow_html=True)
with metric_cols[3]:
    st.markdown(metric_card_html("Low Risk", summary.get("low_risk_count", 0), "Stable performers"), unsafe_allow_html=True)
with metric_cols[4]:
    st.markdown(metric_card_html("Avg Risk", summary.get("average_risk_score", 0.0), "Overall cohort risk intensity"), unsafe_allow_html=True)
with metric_cols[5]:
    st.markdown(metric_card_html("Top Weak Subject", summary.get("most_common_weak_subject", "N/A"), "Most common gap area"), unsafe_allow_html=True)

g1, g2, g3 = st.columns(3)
with g1:
    st.markdown(gauge_html(summary.get("high_risk_percentage", 0), "High Risk Share", "#ef4444"), unsafe_allow_html=True)
with g2:
    st.markdown(gauge_html(summary.get("average_risk_score", 0), "Average Risk Score", "#2563eb"), unsafe_allow_html=True)
with g3:
    st.markdown(gauge_html(summary.get("homework_attention_percentage", 0), "Homework Attention Need", "#f59e0b"), unsafe_allow_html=True)

# Filters and search
st.markdown("<div class='section-title'>3) Smart Filters</div>", unsafe_allow_html=True)
fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 1.2])
classes = ["All"] + sorted(processed_df["Class"].astype(str).dropna().unique().tolist()) if "Class" in processed_df.columns else ["All"]
sections = ["All"] + sorted(processed_df["Section"].astype(str).dropna().unique().tolist()) if "Section" in processed_df.columns else ["All"]
risk_levels = ["All", "High Risk", "Medium Risk", "Low Risk"]
selected_class = fc1.selectbox("Class", classes)
selected_section = fc2.selectbox("Section", sections)
selected_risk = fc3.selectbox("Risk Category", risk_levels)
search_name = fc4.text_input("Search Student", placeholder="Type student name")

filtered_df = processed_df.copy()
if selected_class != "All" and "Class" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Class"].astype(str) == selected_class]
if selected_section != "All" and "Section" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Section"].astype(str) == selected_section]
if selected_risk != "All" and "Risk_Category" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Risk_Category"] == selected_risk]
if search_name.strip() and "Student_Name" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Student_Name"].astype(str).str.contains(search_name.strip(), case=False, na=False)]

if filtered_df.empty:
    st.warning("No students match the selected filters.")
    st.stop()

left, right = st.columns([1.2, 1])
with left:
    st.markdown("<div class='section-title'>4) Top 5 Highest-Risk Students</div>", unsafe_allow_html=True)
    top5 = filtered_df.sort_values("Risk_Score", ascending=False).head(5).copy() if "Risk_Score" in filtered_df.columns else filtered_df.head(5).copy()
    display_top5 = top5[[
        c for c in [
            "Student_Name", "Class", "Section", "Risk_Score", "Risk_Category",
            "Weak_Subject", "Intervention_Priority", "Why_Flagged"
        ] if c in top5.columns
    ]]
    st.dataframe(
        styled_dataframe(display_top5, ["Risk_Score"], ["Risk_Category"]),
        use_container_width=True,
    )

with right:
    st.markdown("<div class='section-title'>5) Critical Alert Cards</div>", unsafe_allow_html=True)
    high_risk_students = filtered_df[filtered_df["Risk_Category"] == "High Risk"] if "Risk_Category" in filtered_df.columns else pd.DataFrame()
    render_alert_cards(high_risk_students.head(5))

# Charts
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='section-title'>6) Risk Score Distribution</div>", unsafe_allow_html=True)
    if {"Student_Name", "Risk_Score", "Risk_Category"}.issubset(filtered_df.columns):
        risk_chart = alt.Chart(filtered_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Student_Name:N", sort="-y", title="Student"),
            y=alt.Y("Risk_Score:Q", title="Risk Score"),
            color=alt.Color(
                "Risk_Category:N",
                scale=alt.Scale(domain=["High Risk", "Medium Risk", "Low Risk"], range=["#ef4444", "#f59e0b", "#10b981"]),
                legend=None,
            ),
            tooltip=["Student_Name", "Risk_Score", "Risk_Category", "Weak_Subject"],
        ).properties(height=380)
        st.altair_chart(risk_chart, use_container_width=True)

with c2:
    st.markdown("<div class='section-title'>7) Weak Subject Distribution</div>", unsafe_allow_html=True)
    if "Weak_Subject" in filtered_df.columns:
        weak_counts = filtered_df["Weak_Subject"].value_counts().reset_index()
        weak_counts.columns = ["Weak_Subject", "Count"]
        weak_chart = alt.Chart(weak_counts).mark_arc(innerRadius=70).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Weak_Subject", type="nominal"),
            tooltip=["Weak_Subject", "Count"],
        ).properties(height=380)
        st.altair_chart(weak_chart, use_container_width=True)

# Processed table
st.markdown("<div class='section-title'>8) Processed Student Results</div>", unsafe_allow_html=True)
show_df = filtered_df.copy()
preferred_cols = [
    "Student_ID", "Student_Name", "Class", "Section", "Average_Marks", "Risk_Score",
    "Risk_Category", "Weak_Subject", "Intervention_Priority", "Why_Flagged", "Suggestion", "Parent_Message_Draft"
]
available_preferred = [c for c in preferred_cols if c in show_df.columns]
st.dataframe(
    styled_dataframe(show_df[available_preferred], ["Risk_Score", "Average_Marks"], ["Risk_Category"]),
    use_container_width=True,
)

# Alerts + report
st.markdown("<div class='section-title'>9) Teacher Alert List</div>", unsafe_allow_html=True)
if alerts_df.empty:
    st.success("No high-risk students found.")
else:
    alert_show = alerts_df.copy()
    cols = [c for c in ["Student_Name", "Class", "Section", "Risk_Score", "Risk_Category", "Weak_Subject", "Intervention_Priority", "Why_Flagged", "Teacher_Email"] if c in alert_show.columns]
    st.dataframe(styled_dataframe(alert_show[cols], ["Risk_Score"], ["Risk_Category"]), use_container_width=True)

st.markdown("<div class='section-title'>10) Downloadable Teacher Intervention Report</div>", unsafe_allow_html=True)
report_df = build_intervention_report(filtered_df)
report_csv = report_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Teacher Intervention Report (CSV)",
    data=report_csv,
    file_name="teacher_intervention_report.csv",
    mime="text/csv",
)

# Parent message generator
p1, p2 = st.columns([1, 1.2])
with p1:
    st.markdown("<div class='section-title'>11) Parent Message Draft Generator</div>", unsafe_allow_html=True)
    student_options = filtered_df["Student_Name"].astype(str).tolist() if "Student_Name" in filtered_df.columns else []
    if student_options:
        selected_student = st.selectbox("Select student", student_options)
        student_row = filtered_df[filtered_df["Student_Name"].astype(str) == selected_student].iloc[0]
        msg_text = student_row.get("Parent_Message_Draft", "No draft available.")
        st.text_area("Parent communication draft", value=msg_text, height=170)
    else:
        st.info("No student names available for parent message drafting.")

with p2:
    st.markdown("<div class='section-title'>12) Trend Comparison</div>", unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    tc1.metric(
        "Current Avg Risk",
        summary.get("average_risk_score", 0.0),
        delta=round(summary.get("average_risk_score", 0.0) - weekly_trend.get("previous_week_average_risk", summary.get("average_risk_score", 0.0)), 2),
    )
    tc2.metric(
        "Current High Risk",
        summary.get("high_risk_count", 0),
        delta=summary.get("high_risk_count", 0) - weekly_trend.get("previous_week_high_risk_count", summary.get("high_risk_count", 0)),
    )
    tc3.metric(
        "Improvement Status",
        weekly_trend.get("improvement_status", "Baseline loaded"),
    )

    if result.get("email_subject") or result.get("email_body"):
        st.markdown("<div class='section-title'>13) Dummy Alert Preview</div>", unsafe_allow_html=True)
        st.text(result.get("email_subject", ""))
        st.code(result.get("email_body", ""), language="text")

with st.expander("Required CSV columns"):
    st.write(REQUIRED_COLUMNS)
