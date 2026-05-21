import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 가져오기
@st.cache_data
def load_titanic():
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    data = pd.read_csv(url)
    bins = [0, 20, 60, 80]
    labels = ["청소년", "성인", "노인"]

    data["AgeGroup"] = pd.cut(data["Age"], bins=bins, labels=labels, right=False)
    data["AgeGroup"] = data["AgeGroup"].astype(str).fillna("연령 미상")
    data["AgeGroup"] = data["AgeGroup"].replace("nan", "연령 미상")
    return data

df = load_titanic()

st.set_page_config(
    page_title="🚢 Titanic Survival Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 왼쪽 사이드바 필터
st.sidebar.title("대시보드 필터 설정")

# 생존자만 필터
show_survived = st.sidebar.toggle("생존자만", value=False)

# 연령대 그룹 선택
age_group_options = ["청소년", "성인", "노인", "연령 미상"]
selected_age_groups = st.sidebar.multiselect(
    "연령대 그룹 선택",
    options=age_group_options,
    default=["청소년", "성인", "노인"]
)

# Pclass 멀티셀렉트
pclass_options = sorted(df['Pclass'].unique())
selected_pclass = st.sidebar.multiselect(
    "객실 등급",
    options=pclass_options,
    default=pclass_options,
    format_func=lambda x : f"{x}등석"
)

# 성별 선택
gender_options = ["남성", "여성", "선택안함"]
selected_gender = st.sidebar.radio("성별", gender_options)

# 운임 슬라이더
fare_min, fare_max = int(df["Fare"].min()) , int(df["Fare"].max())
fare_range = st.sidebar.slider(
    "운임 범위($)",
    min_value = fare_min,
    max_value = fare_max,
    value = (fare_min, fare_max)
)

# 필터 적용 Logic
filtered = df[
    df["AgeGroup"].isin(selected_age_groups) &
    df["Pclass"].isin(selected_pclass) &
    df["Fare"].between(*fare_range)
]

# 생존자만 보기 토글 기능 반영
if show_survived:
    filtered = filtered[filtered["Survived"] == 1]

# 성별 필터 영어 데이터와 매칭
if selected_gender == "남성":
    filtered = filtered[filtered["Sex"] == "male"]
elif selected_gender == "여성":
    filtered = filtered[filtered["Sex"] == "female"]

# 타이틀
st.title("🚢 Titanic Survival Dashboard")
st.markdown("---")

# ── 메트릭 영역 (연령대별 생존율 분리를 위해 4컬럼으로 재배치) ──
col1, col2, col3, col4 = st.columns(4)

total = len(filtered)
survived = filtered["Survived"].sum()

# 안전장치: 데이터가 0건일 때 나누기 에러 방지
survival_rating = (survived / total * 100) if total > 0 else 0
avg_age = filtered["Age"].mean() if total > 0 else 0
avg_fare = filtered["Fare"].mean() if total > 0 else 0

# 연령대별 생존율 계산
age_survival_means = (
    filtered.groupby("AgeGroup")["Survived"]
    .mean()
)

# 메트릭 상단 기본 정보 출력
col1.metric("👥 총 승객 수", f"{total}명")
col2.metric("✅ 생존자 수", f"{int(survived)}명")
col3.metric("📈 전체 생존율", f"{survival_rating:.1f}%")
col4.metric("💰 평균 운임", f"${avg_fare:.1f}")

st.markdown(" ") # 좁은 간격을 위한 한 칸 띄우기

# 💡 [핵심 수정] 가로 폭이 제한 없는 본문 영역에 연령대별 생존율을 대형 배너 형태로 배치
if total > 0 and len(age_survival_means) > 0:
    # 각 연령대별 데이터를 예쁜 이모지와 함께 HTML/Markdown 태그로 넓게 뿌려줍니다.
    rate_items = [f"**{k}** {v*100:.1f}%" for k, v in age_survival_means.items()]
    age_survived_str = "     |     ".join(rate_items) # 간격을 넓게 벌려 가독성 확보
else:
    age_survived_str = "데이터 없음"

# 부드러운 배경이 들어간 안내 박스 형태로 널널하게 노출시킵니다.
st.info(f"📊 **연령대별 생존율 상세:**   {age_survived_str}")
st.markdown("---")


st.subheader("💵 운임(Fare)이 생존에 미친 영향 집중 분석")

male_analysis_df = filtered[filtered["Sex"] == "male"].copy()

# 분석을 위해 데이터가 있는 경우에만 실행
if len(male_analysis_df) > 0:
    analysis_df = male_analysis_df
    analysis_df["남성 생존여부"] = analysis_df["Survived"].map({0: "사망", 1: "생존"})

    # 화면을 반으로 나누어 두 가지 관점의 차트 배치
    fare_left, fare_right = st.columns(2)

    with fare_left:
        st.write("📊 **생존 여부별 운임 분포 (Box Plot)**")
        fig_box = px.box(
            analysis_df,
            x="남성 생존여부",
            y="Fare",
            color="남성 생존여부",
            points="all", 
            color_discrete_map={"생존": "#2ecc71", "사망": "#e74c3c"},
            # 💡 [수정] labels에 가로축 이름 변경 옵션 추가
            labels={"Fare": "지불한 운임 ($)", "남성 생존여부": "남성 생존 여부"}
        )
        fig_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    with fare_right:
        st.write("📈 **운임 구간별 생존/사망자 밀도 (Density Hint)**")
        fig_violin = px.violin(
            analysis_df,
            x="남성 생존여부",
            y="Fare",
            color="남성 생존여부",
            box=True, 
            color_discrete_map={"생존": "#2ecc71", "사망": "#e74c3c"},
            # 💡 [수정] labels에 가로축 이름 변경 옵션 추가
            labels={"Fare": "지불한 운임 ($)", "남성 생존여부": "남성 생존 여부"}
        )
        fig_violin.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_violin, use_container_width=True)

    # 💡 도메인 해석을 돕는 가이드 텍스트 자동화
    survived_fare = analysis_df[analysis_df["Survived"] == 1]["Fare"].mean()
    dead_fare = analysis_df[analysis_df["Survived"] == 0]["Fare"].mean()
    
    st.info(
        f"💡 **현재 필터링된 [남성 승객] 데이터 분석 결과:**\n"
        f"* 생존한 **남성 승객**들의 평균 운임: **${survived_fare:.1f}**\n"
        f"* 사망한 **남성 승객**들의 평균 운임: **${dead_fare:.1f}**\n"
        f"* 남성 집단 내에서도 생존자가 사망자에 비해 평균적으로 약 **{survived_fare / dead_fare if dead_fare > 0 else 0:.1f}배** 더 비싼 티켓을 가졌음을 입증할 수 있습니다."
    )
else:
    st.warning("필터링된 데이터가 없어 차트를 그릴 수 없습니다.")


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