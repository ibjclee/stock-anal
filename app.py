import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_collector import StockDataFetcher
from chart_analyzer import ChartAnalyzer
from volume_analyzer import VolumeAnalyzer
from catalyst_analyzer import CatalystAnalyzer
from market_analyzer import MarketAnalyzer

# 페이지 기본 설정
st.set_page_config(page_title="재차거시 주식 분석", page_icon="📈", layout="wide")

st.title("📈 '재차거시' 주식 분석 대시보드")
st.markdown("""
**유목민의 '투자의 정석'**에서 강조하는 **재(재료), 차(차트), 거(거래량), 시(시황)** 4박자를 기반으로 종목을 분석합니다.
""")

# query_params를 읽어서 URL로 전달된 종목이 있으면 기본값으로 설정
if "symbol" in st.query_params:
    default_symbol = st.query_params["symbol"]
    auto_analyze = True
else:
    default_symbol = "삼성전자"
    auto_analyze = False

tab1, tab2 = st.tabs(["🔍 단일 종목 상세 분석", "🔥 주도주 스캐너 (발굴)"])

with tab1:
    st.subheader("개별 종목 분석")
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        symbol_input = st.text_input("종목명 또는 코드 입력", value=default_symbol, help="종목명(예: 삼성전자)이나 6자리 코드(예: 005930)를 입력하세요.")
    with col_btn:
        st.write("") # 마진 맞추기
        st.write("")
        analyze_btn = st.button("분석 시작", type="primary")

    if analyze_btn or auto_analyze or symbol_input:
        # 한 번 자동 분석 후에는 파라미터 초기화하여 무한 새로고침 방지
        st.query_params.clear()
        with st.spinner("데이터를 수집하고 분석 중입니다... 잠시만 기다려주세요."):
            fetcher = StockDataFetcher()
            krx_code = fetcher.get_code_by_name(symbol_input)
            
            if not krx_code:
                st.error(f"'{symbol_input}' 종목을 찾을 수 없습니다.")
                st.stop()
                
            krx_name = fetcher.get_name_by_code(krx_code)
                
            df = fetcher.get_ohlcv(krx_code)
            
            if df.empty:
                st.error("해당 종목의 주가 데이터를 불러오는 데 실패했습니다.")
                st.stop()
                
            cat_analyzer = CatalystAnalyzer(krx_code)
            cat_res = cat_analyzer.analyze()
            
            chart_analyzer = ChartAnalyzer(df)
            chart_res = chart_analyzer.analyze()
            
            vol_analyzer = VolumeAnalyzer(df)
            vol_res = vol_analyzer.analyze()
            
            market_analyzer = MarketAnalyzer()
            market_res = market_analyzer.analyze()
            
            total_score = cat_res['score'] + chart_res['score'] + vol_res['score'] + market_res['score']
            
            st.header(f"[{krx_code}] {krx_name} 분석 결과")
            
            if market_res['score'] < 0:
                opinion = "보수적 접근 (관망 또는 비중 축소)"
            elif total_score >= 30:
                opinion = "적극 매수 고려 (모든 지표가 긍정적)"
            elif total_score >= 15:
                opinion = "분할 매수 고려"
            elif total_score >= 0:
                opinion = "관망 (추세 전환 대기)"
            else:
                opinion = "매수 보류 (단기 하락 추세 지속)"

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("★ 종합 점수", f"{total_score} / 75점")
            col2.metric("📰 재료 점수", f"{cat_res['score']} / 15점")
            col3.metric("📈 차트 점수", f"{chart_res['score']} / 25점")
            col4.metric("📊 거래량 점수", f"{vol_res['score']} / 15점")
            col5.metric("🌐 시황 점수", f"{market_res['score']} / 20점")
            
            st.info(f"💡 **AI 종합 투자 의견**: {opinion}")

            st.subheader("📊 최근 1년(250 거래일) 차트 흐름")
            df_chart = df.tail(250).copy()
            df_analyzed = chart_analyzer.df.tail(250) 
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_chart.index,
                open=df_chart['Open'],
                high=df_chart['High'],
                low=df_chart['Low'],
                close=df_chart['Close'],
                name='주가',
                increasing_line_color='red', 
                decreasing_line_color='blue'
            ))
            fig.add_trace(go.Scatter(x=df_analyzed.index, y=df_analyzed['MA_20'], name='20일선', line=dict(color='orange', width=1.5)))
            fig.add_trace(go.Scatter(x=df_analyzed.index, y=df_analyzed['MA_60'], name='60일선', line=dict(color='green', width=1.5)))
            fig.add_trace(go.Scatter(x=df_analyzed.index, y=df_analyzed['MA_120'], name='120일선', line=dict(color='blue', width=1.5)))
            fig.add_trace(go.Scatter(x=df_analyzed.index, y=df_analyzed['MA_200'], name='200일선', line=dict(color='purple', width=1.5)))
            
            fig.update_layout(xaxis_rangeslider_visible=False, height=500, margin=dict(l=0, r=0, t=30, b=0), template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🔍 항목별 세부 분석 내역")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📰 재료 (News & Catalyst)")
                for reason in cat_res['reasons']:
                    st.info(f"👉 {reason}")
                if cat_res.get('headlines'):
                    with st.expander("🔗 최근 기사 제목 보기 (클릭 시 원문 이동)"):
                        for h in cat_res['headlines']:
                            st.markdown(f"• <a href='{h['url']}' target='_blank' style='text-decoration:none;'>{h['title']}</a>", unsafe_allow_html=True)
                st.divider()
                st.markdown("#### 📈 차트 (Price Action)")
                if not chart_res['reasons']:
                    st.write("- 특이 사항 없음")
                for reason in chart_res['reasons']:
                    st.info(f"👉 {reason}")

            with c2:
                st.markdown("#### 📊 거래량 (Volume)")
                if not vol_res['reasons']:
                    st.write("- 특이 사항 없음")
                for reason in vol_res['reasons']:
                    st.info(f"👉 {reason}")
                st.divider()
                st.markdown("#### 🌐 시황 (Market Trend)")
                for reason in market_res['reasons']:
                    st.info(f"👉 {reason}")

with tab2:
    st.header("🔥 재차거시 주도주 스캐너")
    st.markdown("당일 **거래대금 상위 50종목**을 빠르게 스캔하여, 재차거시 종합 점수가 높은 우량 종목을 자동으로 발굴합니다.")
    
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
        
    scan_btn = st.button("🚀 스캐너 실행 (약 30~50초 소요)", type="primary")
    
    if scan_btn:
        with st.spinner("시장의 주도주를 찾고 있습니다..."):
            fetcher = StockDataFetcher()
            krx_list = fetcher.krx_list
            
            if krx_list is None or krx_list.empty:
                st.error("종목 목록을 불러오지 못했습니다.")
                st.stop()
                
            # 1. 거래대금(Amount) 상위 50개 추출 (시장 주도주)
            top_50 = krx_list.sort_values(by='Amount', ascending=False).head(50)
            
            # 2. 시황 분석 (공통이므로 1번만 계산)
            market_analyzer = MarketAnalyzer()
            market_res = market_analyzer.analyze()
            market_score = market_res['score']
            
            results = []
            progress_text = "종목 분석 진행 중..."
            progress_bar = st.progress(0, text=progress_text)
            
            for i, row in enumerate(top_50.itertuples()):
                code = row.Code
                name = row.Name
                progress_bar.progress((i + 1) / 50, text=f"[{i+1}/50] {name} 분석 중...")
                
                # 최소 200일선 분석을 위해 1년(약 250일)치 데이터 로드 (기본값)
                df = fetcher.get_ohlcv(code)
                if df.empty or len(df) < 200:
                    continue
                    
                cat_analyzer = CatalystAnalyzer(code)
                cat_res = cat_analyzer.analyze()
                
                chart_analyzer = ChartAnalyzer(df)
                chart_res = chart_analyzer.analyze()
                
                vol_analyzer = VolumeAnalyzer(df)
                vol_res = vol_analyzer.analyze()
                
                total_score = cat_res['score'] + chart_res['score'] + vol_res['score'] + market_score
                
                # 점수가 30점 이상인 종목만 필터링 (기준 완화하여 여러개 보이게 함)
                if total_score >= 30:
                    results.append({
                        "🔍상세": f"/?symbol={code}",
                        "종목명": name,
                        "코드": code,
                        "총점": total_score,
                        "재료점수": cat_res['score'],
                        "차트점수": chart_res['score'],
                        "거래량점수": vol_res['score'],
                        "주요 특징": chart_res['reasons'][0].split(':')[0] if chart_res['reasons'] else "특이사항 없음"
                    })
                    
            progress_bar.empty()
            
            if results:
                res_df = pd.DataFrame(results)
                res_df = res_df.sort_values(by="총점", ascending=False).reset_index(drop=True)
                st.session_state.scan_results = res_df  # 세션에 결과 저장
                
                st.success(f"🎉 총 {len(results)}개의 유망 종목(30점 이상)을 발견했습니다!")
                
                # 데이터프레임 스타일링 (LinkColumn 사용)
                st.dataframe(
                    res_df.style.background_gradient(cmap='Greens', subset=['총점']),
                    column_config={
                        "🔍상세": st.column_config.LinkColumn(
                            "분석",
                            display_text="상세보기 🚀"
                        )
                    },
                    use_container_width=True,
                    height=400
                )
                st.info("💡 표 제일 왼쪽의 **'상세보기 🚀'** 글자를 클릭하시면 해당 종목의 상세 분석 화면으로 바로 이동합니다.")
            else:
                st.session_state.scan_results = None
                st.warning("현재 시장 상황에서 점수가 30점 이상인 주도주를 찾지 못했습니다.")
                
    elif st.session_state.scan_results is not None:
        # 스캔 버튼을 누르지 않았지만 저장된 결과가 있는 경우 렌더링
        res_df = st.session_state.scan_results
        st.success(f"📂 이전에 스캔한 총 {len(res_df)}개의 유망 종목 결과가 유지되고 있습니다. (다시 스캔하려면 버튼을 누르세요)")
        st.dataframe(
            res_df.style.background_gradient(cmap='Greens', subset=['총점']),
            column_config={
                "🔍상세": st.column_config.LinkColumn(
                    "분석",
                    display_text="상세보기 🚀"
                )
            },
            use_container_width=True,
            height=400
        )
        st.info("💡 표 제일 왼쪽의 **'상세보기 🚀'** 글자를 클릭하시면 해당 종목의 상세 분석 화면으로 바로 이동합니다.")
