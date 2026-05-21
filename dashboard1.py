import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="🚢 Titanic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 데이터 로드 ──────────────────────────────────────────
@st.cache_data
def load_titanic():
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    return pd.read_csv(url)

df = load_titanic()

# ── 사이드바 필터 ─────────────────────────────────────────
st.sidebar.title("🔧 필터 설정")

# 나이 슬라이더
age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider(
    "나이 범위",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max)
)

# Pclass 멀티셀렉트
pclass_options = sorted(df["Pclass"].unique())
selected_pclass = st.sidebar.multiselect(
    "객실 등급 (Pclass)",
    options=pclass_options,
    default=pclass_options,
    format_func=lambda x: f"{x}등석"
)

# 성별 선택
gender_options = ["전체", "male", "female"]
selected_gender = st.sidebar.radio("성별", gender_options)

# 운임 슬라이더
fare_min, fare_max = int(df["Fare"].min()), int(df["Fare"].max())
fare_range = st.sidebar.slider(
    "운임 범위 ($)",
    min_value=fare_min,
    max_value=fare_max,
    value=(fare_min, fare_max)
)

# ── 필터 적용 ─────────────────────────────────────────────
filtered = df[
    df["Age"].between(*age_range) &
    df["Pclass"].isin(selected_pclass) &
    df["Fare"].between(*fare_range)
].dropna(subset=["Age"])

if selected_gender != "전체":
    filtered = filtered[filtered["Sex"] == selected_gender]

# ── 타이틀 ───────────────────────────────────────────────
st.title("🚢 Titanic Survival Dashboard")
st.markdown("---")

# ── 핵심 메트릭 (4 컬럼) ──────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total = len(filtered)
survived = filtered["Survived"].sum()
survival_rate = (survived / total * 100) if total > 0 else 0
avg_age = filtered["Age"].mean()
avg_fare = filtered["Fare"].mean()

col1.metric("👥 총 승객 수", f"{total}명")
col2.metric("✅ 생존자 수", f"{int(survived)}명")
col3.metric("📊 생존율", f"{survival_rate:.1f}%")
col4.metric("💰 평균 운임", f"${avg_fare:.1f}")

st.markdown("---")

# ── 차트 영역 (2 컬럼) ───────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("📦 객실 등급별 생존율")
    pclass_survival = (
        filtered.groupby("Pclass")["Survived"]
        .mean()
        .reset_index()
        .rename(columns={"Survived": "생존율", "Pclass": "객실 등급"})
    )
    pclass_survival["생존율"] = (pclass_survival["생존율"] * 100).round(1)
    pclass_survival["객실 등급"] = pclass_survival["객실 등급"].astype(str) + "등석"
    fig1 = px.bar(
        pclass_survival,
        x="객실 등급",
        y="생존율",
        color="객실 등급",
        text="생존율",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig1.update_traces(texttemplate="%{text}%", textposition="outside")
    fig1.update_layout(showlegend=False, yaxis_title="생존율 (%)", height=350)
    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("👫 성별 생존 비교")
    gender_survival = (
        filtered.groupby(["Sex", "Survived"])
        .size()
        .reset_index(name="인원수")
    )
    gender_survival["생존여부"] = gender_survival["Survived"].map({0: "사망", 1: "생존"})
    fig2 = px.bar(
        gender_survival,
        x="Sex",
        y="인원수",
        color="생존여부",
        barmode="group",
        color_discrete_map={"생존": "#2ecc71", "사망": "#e74c3c"},
        labels={"Sex": "성별"}
    )
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

# ── 2행 차트 ─────────────────────────────────────────────
left2, right2 = st.columns(2)

with left2:
    st.subheader("📈 나이 분포 (생존 여부)")
    fig3 = px.histogram(
        filtered,
        x="Age",
        color=filtered["Survived"].map({0: "사망", 1: "생존"}),
        nbins=30,
        barmode="overlay",
        opacity=0.7,
        color_discrete_map={"생존": "#3498db", "사망": "#e74c3c"},
        labels={"color": "생존여부"}
    )
    fig3.update_layout(height=350, xaxis_title="나이", yaxis_title="인원수")
    st.plotly_chart(fig3, use_container_width=True)

with right2:
    st.subheader("💵 운임 vs 나이 (생존 여부)")
    fig4 = px.scatter(
        filtered,
        x="Age",
        y="Fare",
        color=filtered["Survived"].map({0: "사망", 1: "생존"}),
        color_discrete_map={"생존": "#27ae60", "사망": "#c0392b"},
        opacity=0.6,
        labels={"color": "생존여부"}
    )
    fig4.update_layout(height=350, xaxis_title="나이", yaxis_title="운임 ($)")
    st.plotly_chart(fig4, use_container_width=True)

# ── 데이터 테이블 (토글) ──────────────────────────────────
st.markdown("---")
with st.expander("📋 원본 데이터 보기"):
    st.dataframe(
        filtered[["Name", "Age", "Sex", "Pclass", "Fare", "Survived"]].reset_index(drop=True),
        use_container_width=True,
        height=300
    )

st.caption("데이터 출처: datasciencedojo/datasets · Titanic CSV")