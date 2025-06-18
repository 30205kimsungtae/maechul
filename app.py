import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------
# 앱 설정
# ------------------------
st.set_page_config(page_title="서울시 매출 성장 상권 분석", layout="wide")
st.title("📈 서울시 추정매출 기반 성장 상권 분석")

# ------------------------
# 데이터 로딩 함수
# ------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("서울시 상권분석서비스(추정매출-상권배후지).csv", encoding="cp949")
    df = df.dropna(subset=["기준_년_코드", "기준_분기_코드", "서비스_업종_코드", "총_매출_금액"])
    df["총_매출_금액"] = df["총_매출_금액"].astype(float)
    return df

# 데이터 불러오기
df = load_data()

# ------------------------
# 필터 사이드바 설정
# ------------------------
years = sorted(df["기준_년_코드"].unique())
quarters = sorted(df["기준_분기_코드"].unique())
selected_year = st.sidebar.selectbox("연도 선택", years, index=len(years)-1)
selected_quarter = st.sidebar.selectbox("분기 선택", quarters, index=len(quarters)-1)

# 최신 분기 데이터 필터링
recent_df = df[(df["기준_년_코드"] == selected_year) & (df["기준_분기_코드"] == selected_quarter)]

# 전 분기 데이터 추출
if selected_quarter > 1:
    prev_year, prev_quarter = selected_year, selected_quarter - 1
else:
    prev_year, prev_quarter = selected_year - 1, 4

prev_df = df[(df["기준_년_코드"] == prev_year) & (df["기준_분기_코드"] == prev_quarter)]

# ------------------------
# 성장률 계산
# ------------------------
growth_df = pd.merge(
    recent_df,
    prev_df,
    on="상권_코드",
    suffixes=("_최근", "_이전")
)

growth_df["매출_증가율"] = (
    (growth_df["총_매출_금액_최근"] - growth_df["총_매출_금액_이전"]) / growth_df["총_매출_금액_이전"] * 100
)

# ------------------------
# 시각화 및 결과
# ------------------------
st.subheader(f"{selected_year}년 {selected_quarter}분기 매출 성장률 TOP 10 상권")

top_growth = growth_df.sort_values("매출_증가율", ascending=False).head(10)
st.dataframe(top_growth[[
    "상권_코드", "상권_이름_최근", "총_매출_금액_최근", "총_매출_금액_이전", "매출_증가율"
]].rename(columns={
    "상권_이름_최근": "상권명",
    "총_매출_금액_최근": "최근 매출",
    "총_매출_금액_이전": "이전 매출"
}))

fig = px.bar(
    top_growth,
    x="상권_이름_최근",
    y="매출_증가율",
    title="매출 증가율 TOP 10",
    labels={"상권_이름_최근": "상권명", "매출_증가율": "증가율(%)"},
    color="매출_증가율",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig, use_container_width=True)

# ------------------------
# 인사이트
# ------------------------
st.markdown("""
### 🔍 인사이트
- 전 분기 대비 매출 증가율이 높은 상권은 창업 유망지역일 가능성이 높습니다.
- 지속적으로 성장 중인 상권을 추적하여 전략적인 입지 선정이 가능합니다.
""")
