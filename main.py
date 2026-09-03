# -----------------------------------------------------------------------------
# 원본 데이터 요약 통계 섹션 (행/열 전환)
# -----------------------------------------------------------------------------
st.subheader("📌 원본 데이터 요약 통계")

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
