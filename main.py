import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "박스오피스 Top 10 진입 영화(216편) 데이터 기반의 장르, 국가, 관객수 분포 및 관계 분석 도감입니다."
)


# [데이터 불러오기 및 전처리] 캐시 적용
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 1. 장르 전처리: 세로막대 기호(|)로 여러 개 적힌 경우 첫 번째 장르만 추출
    df["main_genre"] = (
        df["genre"].astype(str).str.split("|").str[0].str.strip()
    )

    # 2. 날짜 및 수치형 데이터 변환
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d")

    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# 데이터 로드
try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# [구역 1] 장르별 영화 편수 분포 (도넛 그래프)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 1. 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = (
    df["main_genre"].value_counts().reset_index()
)
genre_counts.columns = ["장르", "영화편수"]

# Plotly 도넛 그래프(Pie Chart with hole) 생성
fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화편수",
    hole=0.4,  # 중앙에 구멍을 뚫어 도넛 형태로 제작
    title="<b>개봉 영화 장르별 비중 (Top 10 진입작 기준)</b>",
)

# 마우스 오버 툴팁 및 표시 텍스트 서식 지정
fig1.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>장르</b>: %{label}<br><b>영화 편수</b>: %{value}편<br><b>비율</b>: %{percent}<extra></extra>",
)

# 레이아웃 미세 조정
fig1.update_layout(
    legend=dict(title="장르 목록", orientation="v", yanchor="middle", y=0.5),
    margin=dict(l=40, r=40, t=60, b=40),
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 해설/인사이트
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "박스오피스 상위권에 진입한 영화들의 장르 다변화 정도와 한국 극장가에서 가장 많은 출품 비중을 차지하는 주류 장르 구조를 한눈에 파악할 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 2] 추후 새로운 분포/관계 그래프가 추가될 구역 (확장용 레이아웃)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 2. (추가 예정 구역)")
st.caption(
    "앞으로 이 공간에 제작 국가별 분포, 스크린수와 관객수의 상관관계, 10위권 상주 일수 분포 등 새로운 그래프가 계속 추가될 예정입니다."
)
