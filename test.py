import streamlit as st

st.set_page_config(layout="wide") # 화면을 넓게 쓰기 위한 필수 설정

# 1. 왼쪽 사이드바: 모든 필터(입력 변수)를 몰아넣음
with st.sidebar:
    st.header("⚙️ 대시보드 설정")
    # 토글 스위치 활용
    dark_mode = st.toggle("어두운 테마 적용")
    # 날짜 범위 입력 활용
    date_range = st.date_input("조회 기간")
    # 라디오 버튼 활용
    view_type = st.radio("분석 단위", ["일별", "월별"])

# 2. 메인 화면 상단: 메트릭 지표 배치 (가로로 3분할)
st.title("📊 비즈니스 핵심 대시보드")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 매출", "5,400만 원", "+12%")
with col2:
    st.metric("신규 방문자", "1,240명", "-3%")
with col3:
    st.metric("이탈률", "24.1%", "-1.5%", delta_color="inverse")

st.markdown("---") # 구분선

# 3. 메인 화면 하단: 탭을 활용해 차트 종류 분할
tab1, tab2 = st.tabs(["📈 트렌드 분석", "👥 고객 행동"])

with tab1:
    st.subheader("기간별 매출 추이 차트")
    #여기에 st.plotly_chart 등을 넣으시면 됩니다.
    st.info(f"현재 {view_type} 기준으로 데이터를 보여주고 있습니다.")

with tab2:
    st.subheader("고객 군집 분석 결과")
    # 다른 종류의 그래프나 분석 결과 배치

# 4. 맨 아래: 접이식 상자로 원본 데이터 숨겨두기
with st.expander("🔍 원본 데이터 확인하기"):
    st.write("여기에 st.dataframe()을 넣으면 필요할 때만 펼쳐서 볼 수 있습니다.")