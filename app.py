import streamlit as st
import pandas as pd
import plotly.express as px

# st.title("스트림릿에 대해 배워보자!")
# st.header("위젯")
# st.text("위젯이란? 사용자 입력을 받는 UI 요소들... python 변수로 들어온다.")

# # 텍스트 입력
# name = st.text_input("이름을 입력하세요.", placeholder="홍길동")
# st.write(f"{name}님 안녕하세요!")

# # 드롭다운 선택
# gender = st.selectbox("성별", ["male", "female", "선택"])
# st.write(f"성별: {gender}")


# # 범위 슬라이더
# age_min, age_max = st.slider("나이 범위", 0, 100, (20, 60))

# # 버튼
# if st.button("확인"):
#     st.write("버튼이 눌렸습니다!")

# # 체크박스
# show = st.checkbox("원본 데이터 보기")

# # 다중 선택
# opts = st.multiselect("등급", [1, 2, 3], default=[1, 2, 3])

@st.cache_data
def load_titanic():
    url = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
    return pd.read_csv(url)

titanic = load_titanic().copy()

# ── 위젯 ──────────────────────────────────────────────────────────────────────
pclass = st.selectbox("객실 등급", [1, 2, 3])
survived_only = st.checkbox("생존자만 보기")

# ── 필터 적용 ─────────────────────────────────────────────────────────────────
filtered = titanic[titanic['Pclass'] == pclass]
if survived_only:
    filtered = filtered[filtered['Survived'] == 1]

st.write(f"결과: {len(filtered)}명")
st.dataframe(filtered.head(20))

st.metric(label = "생존율", value="38.4%", delta = "+2.3%")
st.metric("비용", "1,500원", "-100원", delta_color="red")
st.metric("비용", "1,500원", "-100원", delta_color="inverse") # 색상을 반대

@st.cache_data
def load_titanic():
    url = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
    return pd.read_csv(url)

titanic = load_titanic()

fig = px.scatter(
    titanic, x='Age', y='Fare',
    color='Survived',
    hover_name='Name',
    title='나이 vs 요금',
    template='simple_white'
)

# ✅ width='stretch': 전체 너비 (최신 API)
st.plotly_chart(fig, width='stretch', key='chart1')

# 컬럼을 나누고 싶다
col1 , col2 , col3 = st.columns(3) # 개수 혹은 비율 조정 가능
with col1:
    st.metric("생존자수", 342)
with col2:
    st.metric("생존율", "38.4%")


fig2 = px.scatter(
    titanic, x='Age', y='Fare',
    color='Survived',
    hover_name='Name',
    title='나이 vs 요금',
    template='simple_white'
)

# ✅ width='stretch': 전체 너비 (최신 API)
st.plotly_chart(fig2, width='stretch', key='chart2')