# ============================================================
# 💡 CHURN INTELLIGENCE DASHBOARD v2
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 🎨 PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Churn Intelligence Dashboard",
    page_icon="💡",
    layout="wide"
)

# Custom orange theme
st.markdown("""
    <style>
        .main {
            background-color: #fffaf5;
        }
        h1, h2, h3 {
            color: #f97316;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #f97316;
            color: white;
        }
        .metric-card {
            background: white;
            border-left: 5px solid #f97316;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 📂 LOAD DATA
# ============================================================
st.title("💳 Customer Churn Intelligence Dashboard")
st.markdown("Gain insights into **why customers leave**, **who is most at risk**, and **what behaviors drive attrition**.")

uploaded_file = st.file_uploader("📂 Upload your dataset (CSV)", type=["csv"])
if not uploaded_file:
    st.info("Upload a dataset to start analyzing churn patterns.")
    st.stop()

df = pd.read_csv(uploaded_file)
df.columns = df.columns.str.lower()

if "attritionflag" not in df.columns:
    st.error("❌ Missing column: `attritionflag`.")
    st.stop()

# ============================================================
# 🧹 FILTER PANEL
# ============================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=100)
    st.header("🎛️ Filters")

    if "cardtype" in df.columns:
        card_filter = st.multiselect("Card Type", df["cardtype"].unique(), df["cardtype"].unique())
        df = df[df["cardtype"].isin(card_filter)]

    if "gender" in df.columns:
        gender_filter = st.multiselect("Gender", df["gender"].unique(), df["gender"].unique())
        df = df[df["gender"].isin(gender_filter)]

    if "persona" in df.columns:
        persona_filter = st.multiselect("Persona", df["persona"].unique(), df["persona"].unique())
        df = df[df["persona"].isin(persona_filter)]

    if "educationtier" in df.columns:
        edu_filter = st.multiselect("Education Tier", df["educationtier"].unique(), df["educationtier"].unique())
        df = df[df["educationtier"].isin(edu_filter)]

    if "demographiccluster" in df.columns:
        cluster_filter = st.multiselect("Demographic Cluster", df["demographiccluster"].unique(), df["demographiccluster"].unique())
        df = df[df["demographiccluster"].isin(cluster_filter)]

# ============================================================
# 📊 KEY METRICS
# ============================================================
total_customers = len(df)
attrition_rate = df["attritionflag"].mean() * 100
avg_credit_limit = df["creditlimit"].mean() if "creditlimit" in df.columns else 0
avg_util = df["utilizationrate"].mean() * 100 if "utilizationrate" in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total Customers", f"{total_customers:,}", "Active Base")
col2.metric("⚠️ Attrition Rate", f"{attrition_rate:.2f}%", "Overall")
col3.metric("💳 Avg Credit Limit", f"${avg_credit_limit:,.0f}", "Per Customer")
col4.metric("📊 Avg Utilization", f"{avg_util:.1f}%", "Portfolio Avg")

st.markdown("---")

# ============================================================
# 🔍 1️⃣ DEMOGRAPHIC CHURN INSIGHT
# ============================================================
st.header("1️⃣ Customer Insight: Demographics Linked to Churn")

cols = st.columns(3)

if "gender" in df.columns:
    churn_gender = df.groupby("gender")["attritionflag"].mean().reset_index()
    fig = px.bar(churn_gender, x="gender", y="attritionflag",
                 color="gender", color_discrete_sequence=px.colors.sequential.Oranges)
    fig.update_yaxes(title="Churn Rate", tickformat=".0%")
    cols[0].plotly_chart(fig, use_container_width=True)

if "educationtier" in df.columns:
    churn_edu = df.groupby("educationtier")["attritionflag"].mean().reset_index()
    fig = px.bar(churn_edu, x="educationtier", y="attritionflag",
                 color="educationtier", color_discrete_sequence=px.colors.sequential.Oranges)
    fig.update_yaxes(title="Churn Rate", tickformat=".0%")
    cols[1].plotly_chart(fig, use_container_width=True)

if "demographiccluster" in df.columns:
    churn_cluster = df.groupby("demographiccluster")["attritionflag"].mean().reset_index()
    fig = px.bar(churn_cluster, x="demographiccluster", y="attritionflag",
                 color="demographiccluster", color_discrete_sequence=px.colors.sequential.Oranges)
    fig.update_yaxes(title="Churn Rate", tickformat=".0%")
    cols[2].plotly_chart(fig, use_container_width=True)

# Dynamic text narrative
top_group = churn_gender.sort_values("attritionflag", ascending=False).iloc[0]["gender"] if "gender" in df.columns else None
st.markdown(f"🧠 **Narrative Insight:** Customers identified as **{top_group}** show higher churn risk. Education and demographic clusters also show disparities suggesting deeper behavioral segmentation may be required.")

# ============================================================
# ⚙️ 2️⃣ BEHAVIORAL INSIGHT
# ============================================================
st.header("2️⃣ Behavioral Insight: Spend & Activity Patterns")

if {"totalspend", "utilizationrate", "attritionflag"}.issubset(df.columns):
    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(df, x="utilizationrate", y="totalspend", color="attritionflag",
                         color_continuous_scale=["#10b981", "#ef4444"],
                         title="Spending vs Utilization Rate")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df["txn_bucket"] = pd.cut(df["totaltransactions"], bins=[0, 10, 50, 100, 500],
                                  labels=["Low", "Medium", "High", "Very High"])
        churn_txn = df.groupby("txn_bucket")["attritionflag"].mean().reset_index()
        fig = px.bar(churn_txn, x="txn_bucket", y="attritionflag", title="Churn by Transaction Level",
                     color="txn_bucket", color_discrete_sequence=px.colors.sequential.Oranges)
        fig.update_yaxes(title="Churn Rate", tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

avg_spend = df["totalspend"].mean()
avg_txn = df["totaltransactions"].mean()
st.markdown(f"💬 **Behavioral Insight:** Avg spend per customer is **${avg_spend:,.0f}**, with roughly **{avg_txn:.0f} transactions**. Higher churn observed among **low-spend, high-utilization** segments.")

# ============================================================
# ⏳ 3️⃣ EARLY WARNING — LIFECYCLE ANALYSIS
# ============================================================
st.header("3️⃣ Early Warning: Churn over Customer Lifecycle")

if "tenuregroup" in df.columns:
    churn_tenure = df.groupby("tenuregroup")["attritionflag"].mean().reset_index()
    fig = px.line(churn_tenure, x="tenuregroup", y="attritionflag",
                  color_discrete_sequence=["#f97316"], markers=True)
    fig.update_yaxes(title="Churn Rate", tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

# Dynamic insight
if len(churn_tenure) > 0:
    early_peak = churn_tenure.iloc[churn_tenure["attritionflag"].idxmax()]
    st.markdown(f"📉 **Early Warning:** Churn peaks for **{early_peak['tenuregroup']}** customers. Retention focus should be applied early in lifecycle.")

# ============================================================
# 🧭 4️⃣ STRATEGIC RETENTION — SEGMENT INTERACTION
# ============================================================
st.header("4️⃣ Strategic Retention: Behavior × Demographics Interaction")

if {"persona", "income_bucket", "attritionflag"}.issubset(df.columns):
    churn_heat = df.groupby(["persona", "income_bucket"])["attritionflag"].mean().reset_index()
    fig = px.density_heatmap(
        churn_heat, x="income_bucket", y="persona", z="attritionflag",
        color_continuous_scale="OrRd", title="Churn Risk by Persona & Income"
    )
    fig.update_traces(hovertemplate="Persona: %{y}<br>Income: %{x}<br>Churn: %{z:.1%}")
    st.plotly_chart(fig, use_container_width=True)

# Automatic summary narrative
if len(churn_heat) > 0:
    high_risk = churn_heat.sort_values("attritionflag", ascending=False).head(1)
    persona = high_risk.iloc[0]["persona"]
    income = high_risk.iloc[0]["income_bucket"]
    rate = high_risk.iloc[0]["attritionflag"] * 100
    st.markdown(f"🎯 **Retention Strategy:** Highest churn risk at **{rate:.1f}%** comes from **{persona}** customers with **{income}** income level. Prioritize targeted retention offers for this group.")

st.markdown("---")
st.success("✅ Dashboard ready: Use filters to dynamically explore churn across demographics, behavior, and lifecycle.")
