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

    # 결측치 처리
    df["main_genre"] = df["main_genre"].fillna("기타")
    df["movieNm"] = df["movieNm"].fillna("제목 없음")
    df["nation"] = df["nation"].fillna("기타 국가")

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
    hole=0.4,
    title="<b>개봉 영화 장르별 비중 (Top 10 진입작 기준)</b>",
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>장르</b>: %{label}<br><b>영화 편수</b>: %{value}편<br><b>비율</b>: %{percent}<extra></extra>",
)

fig1.update_layout(
    legend=dict(title="장르 목록", orientation="v", yanchor="middle", y=0.5),
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "박스오피스 상위권에 진입한 영화들의 장르 다변화 정도와 한국 극장가에서 가장 많은 출품 비중을 차지하는 주류 장르 구조를 한눈에 파악할 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 2] 장르-영화별 총 관객수 분포 (트리맵)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 2. 장르 및 영화별 총 관객수 분포")

treemap_df = df[df["total_audi"] > 0].copy()

fig2 = px.treemap(
    treemap_df,
    path=[px.Constant("전체 장르"), "main_genre", "movieNm"],
    values="total_audi",
    title="<b>장르별·영화별 총 관객수 트리맵</b>",
    color="main_genre",
)

fig2.update_traces(
    hovertemplate="<b>영화명/장르</b>: %{label}<br><b>총 관객수</b>: %{value:,}명<extra></extra>"
)

fig2.update_layout(
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "전체 시장 관객수를 장르별 및 개별 영화별로 나눈 면적 비중을 통해, 어떤 장르가 총 관객수를 많이 창출했는지와 특정 흥행작이 속한 장르 내 기여도를 명확히 파악할 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 3] 총 관객수 분포 (히스토그램)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 3. 총 관객수 분포")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="<b>총 관객수 분포 히스토그램</b>",
    labels={"total_audi": "총 관객수 (명)"},
)

fig3.update_traces(
    hovertemplate="<b>관객수 구간</b>: %{x:,}명<br><b>영화 수</b>: %{y}편<extra></extra>"
)

fig3.update_layout(
    yaxis_title="영화 수 (편)",
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 관객수가 많은 영화 산출
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = int(top_movie["total_audi"])

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** "
    f"대부분의 영화가 **100만 명 이하(주로 50만 명 미만)** 구간에 집중되어 있으며, "
    f"가장 관객수가 많은 영화는 **'{top_movie_name}'** (총 {top_movie_audi:,}명)입니다. "
    f"이를 통해 극장 흥행 시장이 소수의 대형 흥행작에 쏠려 있는 롱테일(Long-tail) 구조임을 파악할 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 4] 개봉일 스크린수와 총 관객수의 관계 (산점도)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 4. 개봉일 스크린수와 총 관객수의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="main_genre",
    hover_name="movieNm",
    title="<b>개봉일 스크린수 vs 총 관객수 관계 분석</b>",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "main_genre": "장르",
    },
)

fig4.update_traces(
    hovertemplate="<b>영화명</b>: %{hovertext}<br><b>개봉일 스크린수</b>: %{x:,}개<br><b>총 관객수</b>: %{y:,}명<extra></extra>"
)

fig4.update_layout(
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "개봉 초기 확보한 스크린수가 많을수록 최종 총 관객수가 증가하는 양(+)의 상관관계를 보여주며, "
    "초기 스크린 배점이 흥행 성공의 주요 요소로 작용함을 입증합니다."
)


# -----------------------------------------------------------------------------
# [구역 5] 주요 장르별 총 관객수 상자 그림 (박스플롯)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 5. 주요 장르별 총 관객수 분포 (10편 이상 장르)")

genre_counts_series = df["main_genre"].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index
filtered_df = df[df["main_genre"].isin(top_genres)].copy()

fig5 = px.box(
    filtered_df,
    x="main_genre",
    y="total_audi",
    color="main_genre",
    hover_name="movieNm",
    points="outliers",
    title="<b>주요 장르별 총 관객수 상자 그림 (영화 10편 이상 장르 대상)</b>",
    labels={
        "main_genre": "장르",
        "total_audi": "총 관객수 (명)",
    },
)

fig5.update_traces(
    hovertemplate="<b>영화명</b>: %{hovertext}<br><b>총 관객수</b>: %{y:,}명<extra></extra>"
)

fig5.update_layout(
    showlegend=False,
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "각 장르의 관객수 중앙값과 편차 범위, 그리고 상자 위로 돌출된 초대형 흥행 이상치(Outlier) 영화들의 존재를 비교 분석할 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 6] 스크린수, 총 관객수 및 첫 주 관객수의 관계 (버블 차트)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 6. 스크린수·총 관객수·첫 주 관객수 종합 분석 (버블 차트)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="main_genre",
    hover_name="movieNm",
    size_max=50,
    title="<b>개봉일 스크린수 vs 총 관객수 (버블 크기: 개봉 첫 주 관객수)</b>",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "first_week_audi": "개봉 첫 주 관객수",
        "main_genre": "장르",
    },
)

fig6.update_traces(
    hovertemplate="<b>영화명</b>: %{hovertext}<br><b>개봉일 스크린수</b>: %{x:,}개<br><b>총 관객수</b>: %{y:,}명<br><b>첫 주 관객수</b>: %{marker.size:,}명<extra></extra>"
)

fig6.update_layout(
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig6, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "스크린수와 총 관객수 외에도 버블 크기를 통해 개봉 첫 주 초반 흥행 동력이 최종 흥행(총 관객수)으로 어떻게 이어지는지 3차원적 관계를 입체적으로 확인할 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 7] 제작 국가 및 장르별 영화 편수 구조 (선버스트 차트)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 7. 제작 국가 및 장르별 영화 편수 계층 구조")

sunburst_df = (
    df.groupby(["nation", "main_genre"]).size().reset_index(name="movie_count")
)

fig7 = px.sunburst(
    sunburst_df,
    path=["nation", "main_genre"],
    values="movie_count",
    title="<b>제작 국가 → 장르별 영화 편수 선버스트 차트</b>",
)

fig7.update_traces(
    hovertemplate="<b>국가/장르</b>: %{label}<br><b>영화 편수</b>: %{value}편<extra></extra>"
)

fig7.update_layout(
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig7, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "주요 제작 국가별 영화 점유율과 함께 각 국가 내에서 주로 공급되는 장르적 특성과 구조적 분포를 동심원 계층으로 쉽게 비교할 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 8] 관객수 Top 10 영화 순위 (막대그래프)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 8. 관객수 Top 10 영화 순위")

# 총 관객수 기준 상위 10개 영화 추출
top10_df = df.nlargest(10, "total_audi").copy()

# 시각적 내림차순 정렬을 위해 순위열 생성 및 정렬
top10_df["rank"] = range(1, 11)
top10_df = top10_df.sort_values(by="total_audi", ascending=True)

# 막대그래프 생성
fig8 = px.bar(
    top10_df,
    x="total_audi",
    y="movieNm",
    orientation="h",
    color="total_audi",
    color_continuous_scale="Viridis",
    title="<b>역대영화 관객수와 영화을 1등부터10등까지 보여줘</b>",
    labels={
        "total_audi": "총 관객수 (명)",
        "movieNm": "영화명",
    },
)

# 마우스 오버(Hover) 시 영화명, 순위, 관객수 표출
fig8.update_traces(
    hoverinfo="all",
    hovertemplate="<b>영화명</b>: %{y}<br><b>총 관객수</b>: %{x:,}명<extra></extra>",
)

fig8.update_layout(
    coloraxis_showscale=False,
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig8, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "전체 216편 중 총 관객수가 가장 많은 상위 10개 흥행작의 순위와 관객수 격차를 한눈에 비교할 수 있습니다."
)
