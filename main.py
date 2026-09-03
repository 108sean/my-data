import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 페이지 설정 및 타이틀
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="서울 100년 기온 변화 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 100년 기온 변화 분석 앱")
st.caption("공공데이터를 활용하여 서울의 지난 100여 년간 연평균, 최저, 최고 기온 트렌드를 시각화합니다.")

# -----------------------------------------------------------------------------
# 데이터 로드
# -----------------------------------------------------------------------------
# ... (데이터 로드 함수 및 실행)

# -----------------------------------------------------------------------------
# 요약 통계 출력
# -----------------------------------------------------------------------------
st.subheader("📌 원본 데이터 요약 통계")
# ...

col_stat1, col_stat2 = st.columns(2)

with col_stat1:
    st.markdown("##### 📅 일별 원본 데이터 요약 통계 (전체 기간)")
    # .describe() 기본 형태로 가로/세로 위치 설정
    raw_stats = raw_df[['평균기온', '최저기온', '최고기온']].describe()
    raw_stats = raw_stats.rename(index={
        'count': '개수',
        'mean': '평균',
        'std': '표준편차',
        'min': '최소',
        '25%': '25%',
        '50%': '중앙값',
        '75%': '75%',
        'max': '최대'
    })
    st.dataframe(raw_stats.style.format({
        '평균기온': '{:.2f}',
        '최저기온': '{:.2f}',
        '최고기온': '{:.2f}'
    }), use_container_width=True)

with col_stat2:
    st.markdown(f"##### 🗓️ 선택 구간({selected_years[0]}년 ~ {selected_years[1]}년) 연도별 요약 통계")
    yearly_stats = filtered_df[['평균기온', '최저기온', '최고기온']].describe()
    yearly_stats = yearly_stats.rename(index={
        'count': '개수',
        'mean': '평균',
        'std': '표준편차',
        'min': '최소',
        '25%': '25%',
        '50%': '중앙값',
        '75%': '75%',
        'max': '최대'
    })
    st.dataframe(yearly_stats.style.format({
        '평균기온': '{:.2f}',
        '최저기온': '{:.2f}',
        '최고기온': '{:.2f}'
    }), use_container_width=True)
