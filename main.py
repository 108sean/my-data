import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="서울 100년 기온 변화 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 100년 기온 변화 분석 앱")
st.caption("공공데이터를 활용하여 서울의 지난 100여 년간 연평균, 최저, 최고 기온 트렌드를 시각화합니다.")

# -----------------------------------------------------------------------------
# 데이터 로드 및 전처리 (캐싱 적용)
# -----------------------------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

@st.cache_data
def load_data():
    # 인코딩 예외 처리 (cp949 / utf-8)
    try:
        df = pd.read_csv(DATA_URL, encoding='cp949')
    except Exception:
        df = pd.read_csv(DATA_URL, encoding='utf-8')
    
    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 컬럼 매핑 (다양한 표기 방식 대응)
    col_map = {}
    for col in df.columns:
        if '날짜' in col:
            col_map[col] = '날짜'
        elif '지점' in col:
            col_map[col] = '지점'
        elif '평균' in col:
            col_map[col] = '평균기온'
        elif '최저' in col:
            col_map[col] = '최저기온'
        elif '최고' in col:
            col_map[col] = '최고기온'
    
    df = df.rename(columns=col_map)
    
    # 날짜 데이터 변환
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    df = df.dropna(subset=['날짜'])
    df['연도'] = df['날짜'].dt.year
    
    # 수치형 변환
    num_cols = ['평균기온', '최저기온', '최고기온']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 연도별 집계 (연간 관측일수 300일 이상인 정상 연도 기준)
    yearly_df = df.groupby('연도').agg(
        일수=('날짜', 'count'),
        평균기온=('평균기온', 'mean'),
        최저기온=('최저기온', 'min'),
        최고기온=('최고기온', 'max')
    ).reset_index()
    
    yearly_df = yearly_df[yearly_df['일수'] >= 300].copy()
    
    return yearly_df

with st.spinner("데이터를 불러오는 중입니다..."):
    yearly_df = load_data()

# -----------------------------------------------------------------------------
# 사이드바 설정
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ 분석 설정")

min_year = int(yearly_df['연도'].min())
max_year = int(yearly_df['연도'].max())

# 연도 범위 선택 슬라이더
selected_years = st.sidebar.slider(
    "조회 연도 범위 선택",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# 이동평균 선택
ma_window = st.sidebar.selectbox(
    "이동평균(Moving Average) 구간",
    options=[1, 3, 5, 10],
    index=2,
    format_func=lambda x: "미적용 (원본 데이터)" if x == 1 else f"{x}년 이동평균"
)

# 필터링된 데이터
filtered_df = yearly_df[
    (yearly_df['연도'] >= selected_years[0]) & 
    (yearly_df['연도'] <= selected_years[1])
].copy()

# 이동평균 계산
if ma_window > 1:
    filtered_df['평균기온_이동평균'] = filtered_df['평균기온'].rolling(window=ma_window, min_periods=1).mean()

# -----------------------------------------------------------------------------
# 요약 지표 (Metrics)
# -----------------------------------------------------------------------------
st.subheader("📊 주요 기온 지표 요약")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_temp = filtered_df['평균기온'].mean()
    st.metric(
        label="구간 전체 평균기온",
        value=f"{avg_temp:.1f} °C"
    )

with col2:
    highest_row = filtered_df.loc[filtered_df['평균기온'].idxmax()]
    st.metric(
        label="가장 따뜻했던 해 (연평균)",
        value=f"{highest_row['연도']:.0f}년",
        delta=f"{highest_row['평균기온']:.1f} °C"
    )

with col3:
    lowest_row = filtered_df.loc[filtered_df['평균기온'].idxmin()]
    st.metric(
        label="가장 추웠던 해 (연평균)",
        value=f"{lowest_row['연도']:.0f}년",
        delta=f"{lowest_row['평균기온']:.1f} °C",
        delta_color="inverse"
    )

with col4:
    first_10 = filtered_df.head(10)['평균기온'].mean()
    last_10 = filtered_df.tail(10)['평균기온'].mean()
    diff = last_10 - first_10
    st.metric(
        label="초기 대비 최근 기온 변화량",
        value=f"{last_10:.1f} °C",
        delta=f"{diff:+.1f} °C (최근 10년 평균)"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 메인 그래프 시각화 (Plotly)
# -----------------------------------------------------------------------------
st.subheader("📉 연도별 연평균 기온 추이 및 추세선")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=filtered_df['연도'],
    y=filtered_df['평균기온'],
    mode='lines+markers',
    name='연평균 기온',
    line=dict(color='#E74C3C', width=2),
    marker=dict(size=5),
    hovertemplate='%{x}년: %{y:.2f} °C'
))

if ma_window > 1:
    fig.add_trace(go.Scatter(
        x=filtered_df['연도'],
        y=filtered_df['평균기온_이동평균'],
        mode='lines',
        name=f'{ma_window}년 이동평균',
        line=dict(color='#2980B9', width=3, dash='dash'),
        hovertemplate='%{x}년 (%d년 평균): %%{y:.2f} °C' % ma_window
    ))

fig.update_layout(
    title=f"서울 연평균 기온 변화 ({selected_years[0]}년 ~ {selected_years[1]}년)",
    xaxis_title="연도",
    yaxis_title="기온 (°C)",
    hovermode="x unified",
    template="plotly_white",
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# 추가 분석 Tab
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🌡️ 연간 극값(최고/최저) 비교", "📋 원본 데이터 확인"])

with tab1:
    fig_ext = go.Figure()
    fig_ext.add_trace(go.Scatter(
        x=filtered_df['연도'], y=filtered_df['최고기온'],
        name='연중 최고기온', line=dict(color='#FF5722')
    ))
    fig_ext.add_trace(go.Scatter(
        x=filtered_df['연도'], y=filtered_df['최저기온'],
        name='연중 최저기온', line=dict(color='#03A9F4')
    ))
    fig_ext.update_layout(
        title="연도별 연중 최고/최저 기온 추이",
        xaxis_title="연도",
        yaxis_title="기온 (°C)",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_ext, use_container_width=True)

with tab2:
    st.dataframe(
        filtered_df[['연도', '평균기온', '최저기온', '최고기온', '일수']].style.format({
            '평균기온': '{:.2f} °C',
            '최저기온': '{:.1f} °C',
            '최고기온': '{:.1f} °C',
            '일수': '{:,.0f}일'
        }),
        use_container_width=True
    )

st.markdown("---")
st.caption("데이터 출처: 기상청 기후자료포털 (GitHub @greatsong/modudata 제공) | 제작: Streamlit App")
