from data_collector import StockDataFetcher
from chart_analyzer import ChartAnalyzer
from volume_analyzer import VolumeAnalyzer
from catalyst_analyzer import CatalystAnalyzer
from market_analyzer import MarketAnalyzer

def main():
    print("="*60)
    print("      재차거시(재료, 차트, 거래량, 시황) 주식 분석 프로그램")
    print("="*60)
    
    symbol = input("\n분석할 종목 코드를 입력하세요 (예: 005930 또는 삼성전자): ").strip()
    
    if not symbol:
        symbol = '005930'
        print(f"입력값이 없어 기본값(삼성전자: {symbol})으로 진행합니다.")
        
    print("\n[1] 데이터 수집 중...")
    fetcher = StockDataFetcher()
    df = fetcher.get_ohlcv(symbol)
    krx_code = fetcher.get_code_by_name(symbol)
    
    if df.empty or not krx_code:
        print("데이터를 불러오지 못했습니다. 종목 코드가 올바른지 확인해주세요.")
        return
        
    print(f"-> 데이터 수집 완료: 총 {len(df)}영업일 데이터 확보")
    
    print("\n[2] 재료 분석 중 (최근 뉴스)...")
    catalyst_analyzer = CatalystAnalyzer(krx_code)
    cat_res = catalyst_analyzer.analyze()
    
    print("[3] 차트 분석 중 (이동평균선, 스토캐스틱)...")
    chart_analyzer = ChartAnalyzer(df)
    chart_res = chart_analyzer.analyze()
    
    print("[4] 거래량 분석 중...")
    volume_analyzer = VolumeAnalyzer(df)
    vol_res = volume_analyzer.analyze()

    print("[5] 시황 분석 중 (코스피 지수 흐름)...")
    market_analyzer = MarketAnalyzer()
    market_res = market_analyzer.analyze()
    
    print("\n" + "="*60)
    print("                      분석 결과 요약")
    print("="*60)
    
    today_data = df.iloc[-1]
    prev_data = df.iloc[-2] if len(df) > 1 else None
    
    close_price = int(today_data['Close'])
    open_price = int(today_data['Open'])
    high_price = int(today_data['High'])
    low_price = int(today_data['Low'])
    
    if prev_data is not None:
        prev_close = int(prev_data['Close'])
        price_diff = close_price - prev_close
        price_diff_percent = (price_diff / prev_close) * 100
    else:
        price_diff = 0
        price_diff_percent = 0.0
        
    sign = "+" if price_diff > 0 else ""
    print(f"\n▶ [오늘의 가격] 종가: {close_price:,}원 (시가: {open_price:,} / 고가: {high_price:,} / 저가: {low_price:,})")
    print(f"   -> 전일대비: {sign}{price_diff:,}원 ({sign}{price_diff_percent:.2f}%)")
    
    print(f"\n▶ [재료] 분석 점수: {cat_res['score']}점")
    for reason in cat_res['reasons']:
        print(f"  - {reason}")
    if cat_res.get('headlines'):
        print("  * 최근 주요 뉴스:")
        for h in cat_res['headlines']:
            print(f"    > {h}")

    print(f"\n▶ [차트] 분석 점수: {chart_res['score']}점")
    if not chart_res['reasons']:
        print("  - 특이 사항 없음")
    for reason in chart_res['reasons']:
        print(f"  - {reason}")
        
    print(f"\n▶ [거래량] 분석 점수: {vol_res['score']}점")
    if not vol_res['reasons']:
        print("  - 특이 사항 없음")
    for reason in vol_res['reasons']:
        print(f"  - {reason}")

    print(f"\n▶ [시황] 분석 점수: {market_res['score']}점")
    for reason in market_res['reasons']:
        print(f"  - {reason}")
        
    total_score = cat_res['score'] + chart_res['score'] + vol_res['score'] + market_res['score']
    print(f"\n★ 최종 '재차거시' 종합 점수: {total_score}점")
    
    # 종합 의견 도출
    if market_res['score'] < 0:
        print("   -> [종합 의견] 시황이 불안정합니다. 보수적인 접근(관망 또는 비중 축소)을 권장합니다.")
    elif total_score >= 30:
        print("   -> [종합 의견] 적극 매수 고려 (재차거시 모두 긍정적)")
    elif total_score >= 15:
        print("   -> [종합 의견] 분할 매수 고려")
    elif total_score >= 0:
        print("   -> [종합 의견] 관망 (추세 관찰 필요)")
    else:
        print("   -> [종합 의견] 매수 보류 (기술적 하락 추세)")

    print("="*60)

if __name__ == "__main__":
    main()
