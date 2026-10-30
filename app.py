from pdb import run

import streamlit as st
import pandas as pd 
from mfa_auth import show_login 

st.set_page_config(
    page_title="PhishGuard AI",
    page_icon="🛡️",
    layout="wide"
)
if not show_login():
    st.stop()
st.markdown("""
<style>
.stApp {
    background-color: #f3f6fb;
}
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #12345a;
}
[data-testid="stSidebar"] {
    background-color: #10243a;
}
[data-testid="stSidebar"] * {
    color: white;
}
div.stButton > button {
    background-color: #087f8c;
    color: white;
    border-radius: 9px;
    border: none;
    min-height: 44px;
}
div.stButton > button:hover {
    background-color: #066570;
    color: white;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ PhishGuard AI")
    st.caption("Cybersecurity Research Project")
    page = st.radio(
        "NAVIGATION",
        ["Home", "Email Scanner", "Job Checker", "Research Dashboard"]
    )
    st.divider()
    st.caption("MCA Research Project")

if page == "Home":
    st.title("Cybersecurity Protection Center")
    st.write(
        "Analyze suspicious messages, identify potential job-scam "
        "warning signs, and explore cybersecurity awareness."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Detection Tools", "2")
    c2.metric("Research Survey", "Available")
    c3.metric("Analysis", "Text-based")

    st.info(
        "Start with Email Scanner or Job Checker in the sidebar."
    )

elif page in ["Email Scanner", "Job Checker"]:
    is_job = page == "Job Checker"

    st.title(
        "💼 Job Vacancy Risk Checker"
        if is_job else "📧 Email & Message Scanner"
    )

    st.write(
        "Paste the text below to check for potential warning signs."
    )

    message = st.text_area(
        "Message to analyze",
        height=220,
        placeholder="Paste an email, message, or job advertisement..."
    )

    if st.button("🔍 Analyze Now", use_container_width=True):
        if not message.strip():
            st.warning("Please enter a message first.")
        else:
            import re

            text = message.lower()
            warnings = []

            checks = [
                (
                    r"\b(password|otp|one-time password)\b",
                    "Mentions passwords or OTPs. Never share these with others.",
                    30
                ),
                (
                    r"\b(verify your account|confirm your password)\b",
                    "Requests account verification. Check through the official website.",
                    25
                ),
                (
                    r"\b(registration fee|pay now|deposit money|processing fee)\b",
                    "Payment-related wording detected. Verify the request independently.",
                    25
                ),
                (
                    r"\b(urgent|immediately|act now|limited time)\b",
                    "Urgent or pressuring language detected.",
                    15
                ),
                (
                    r"https?://|www\.",
                    "A web address is present. Inspect its domain before opening it.",
                    15
                ),
            ]

            for pattern, warning, points in checks:
                if re.search(pattern, text):
                    warnings.append({
                        "message": warning,
                        "points": points
                    })

            if is_job and re.search(
                r"\b(guaranteed job|no interview|earn money easily)\b",
                text
            ):
                warnings.append({
                    "message": (
                        "Unusual job claims detected. Verify the employer "
                        "independently."
                    ),
                    "points": 25
                })

            # Cap the total at 100
            risk_score = min(
                100,
                sum(item["points"] for item in warnings)
            )

            st.divider()
            st.subheader("Analysis Report")

            if risk_score >= 50:
                risk_level = "High"
                st.error(f"⚠️ {risk_level} estimated risk")
            elif risk_score >= 25:
                risk_level = "Medium"
                st.warning(f"⚠️ {risk_level} estimated risk")
            else:
                risk_level = "Low"
                st.success(f"ℹ️ {risk_level} estimated risk")

            st.metric("Warning Score", f"{risk_score}/100")
            st.progress(risk_score / 100)

            if warnings:
                st.subheader("Warning Signs Detected")

                for item in warnings:
                    st.write(
                        f"⚠️ {item['message']} "
                        f"(weight: {item['points']} points)"
                    )

                st.write(
                    "*Recommended action:* Do not pay or share sensitive "
                    "information until you have verified the message "
                    "through an independent, trusted source."
                )
            else:
                st.info(
                    "No warning signs were detected by these basic rules."
                )
                st.write(
                    "This does not prove the message is genuine or safe. "
                    "Scams can use wording that these rules do not detect."
                )

            st.caption(
                "Prototype only: this score is based on simple keyword rules, "
                "not a trained AI model or a validated probability of fraud. "
                "It may produce false positives and false negatives."
            )

elif page == "Research Dashboard":
    import pandas as pd
    import plotly.express as px
    from pathlib import Path

    st.title("📊 Cybersecurity Awareness Research")
    st.write(
        "Explore the responses collected through your Google Forms "
        "cybersecurity awareness survey."
    )

    csv_path = Path("Untitled form (Responses) - Form Responses 1.csv")

    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            df.columns = df.columns.astype(str).str.strip()

            # Exclude completely empty survey rows
            df = df.dropna(how="all")
            total_responses = len(df)

            st.subheader("Survey Overview")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Survey Responses", total_responses)

            with col2:
                st.metric("Survey Questions", max(len(df.columns) - 1, 0))

            st.divider()
            # Phishing-awareness statistics from actual survey answers
            st.subheader("🔎 Key Phishing Awareness Findings")

            def find_question(keyword):
                for col in df.columns:
                    if keyword.lower() in col.lower():
                        return col
                return None

            def calculate_yes_percentage(keyword):
                col = find_question(keyword)

                if col is None:
                    return None

                answers = df[col].dropna().astype(str).str.strip()
                answers = answers[answers != ""]

                if answers.empty:
                    return None

                yes_count = answers.str.match(
                    r"(?i)^yes\b"
                ).sum()

                percentage = round(
                    (yes_count / len(answers)) * 100, 1
                )

                return {
                    "yes": int(yes_count),
                    "total": len(answers),
                    "percentage": percentage
                }

            findings = [
                (
                    "Heard of phishing attacks",
                    "Have you heard of phishing attacks before?"
                ),
                (
                    "Received cybersecurity training",
                    "Have you ever received formal training"
                ),
                (
                    "Believe awareness education helps",
                    "Do you think cybersecurity awareness education"
                ),
                (
                    "Use two-factor authentication",
                    "Do you use two-factor authentication"
                ),
            ]

            metric_cols = st.columns(2)

            for index, (label, keyword) in enumerate(findings):
                result = calculate_yes_percentage(keyword)

                with metric_cols[index % 2]:
                    if result is not None:
                        st.metric(
                            label,
                            f"{result['percentage']}%",
                            f"{result['yes']} of {result['total']} responses"
                        )
                    else:
                        st.info(f"Question not found: {label}")

            st.caption(
                "Percentages are calculated from non-empty answers. "
                "They describe your survey respondents, not the whole population."
            )

            st.divider()
            st.subheader("Explore Your Survey Results")
            # Automatically generated research findings
            st.subheader("📝 Key Research Findings")

            for label, keyword in findings:
                result = calculate_yes_percentage(keyword)

                if result is not None:
                    pct = result["percentage"]

                    if pct >= 70:
                        interpretation = "A high proportion of respondents answered Yes."
                    elif pct >= 40:
                        interpretation = "Responses were mixed; awareness or practice may need improvement."
                    else:
                        interpretation = "A low proportion answered Yes; this may indicate an area for improvement."

                    st.write(
                        f"*{label}:* {interpretation} "
                        f"({result['yes']} out of {result['total']} respondents, "
                        f"{pct}%)."
                    )

            st.caption(
                "These are descriptive findings from this survey only. "
                "They do not establish cause and effect or represent everyone."
            )

            st.divider()

            # Select a survey question, excluding the timestamp
            question_columns = [
                c for c in df.columns
                if c.lower() != "timestamp"
            ]

            if question_columns and total_responses > 0:
                question = st.selectbox(
                    "Choose a survey question",
                    question_columns
                )

                answers = (
                    df[question]
                    .dropna()
                    .astype(str)
                    .str.strip()
                )
                answers = answers[answers != ""]

                if not answers.empty:
                    counts = (
                        answers.value_counts()
                        .rename_axis("Answer")
                        .reset_index(name="Responses")
                    )
                    counts["Percentage"] = (
                        counts["Responses"] / len(answers) * 100
                    ).round(1)

                    st.write("*Response breakdown*")
                    st.dataframe(counts, use_container_width=True)

                    fig = px.bar(
                        counts,
                        x="Answer",
                        y="Responses",
                        title="Survey Responses by Answer",
                        text="Responses"
                    )
                    fig.update_layout(
                        xaxis_title="Answer",
                        yaxis_title="Number of responses"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.caption(
                        f"{len(answers)} non-empty answers were recorded "
                        f"for this question."
                    )
                else:
                    st.info("No answers have been recorded for this question yet.")
            else:
                st.info("Your survey file does not contain any responses yet.")

            st.divider()
            st.caption(
                "Research note: Results describe the survey respondents only. "
                "They may not represent the views of everyone. "
                "No responses have been invented."
            )

        except Exception as e:
            st.error("Unable to read the survey data.")
            st.write("Check that the CSV file is valid and try again.")
            st.caption(f"Technical detail: {e}")

    else:
        st.error("Survey CSV file not found.")
        st.write(
            "Keep your downloaded CSV file in the same folder as app.py "
            "and check that its filename matches the filename in the code."
        )