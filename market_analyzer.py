import FinanceDataReader as fdr
from datetime import datetime, timedelta

class MarketAnalyzer:
    def __init__(self):
        pass
        
    def fetch_index_data(self, symbol):
        """지수 데이터를 가져옵니다 (KS11: 코스피, KQ11: 코스닥)"""
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=120)).strftime('%Y-%m-%d')
        df = fdr.DataReader(symbol, start_date, end_date)
        return df

    def analyze(self):
        """코스피 지수를 기준으로 현재 시황을 점수화합니다."""
        df_kospi = self.fetch_index_data('KS11')
        
        if df_kospi.empty or len(df_kospi) < 60:
            return {"score": 0, "reasons": ["시황 데이터 수집 실패 또는 데이터 부족"]}
            
        # 20일선(단기/스윙)과 60일선(중기) 이평선 계산
        df_kospi['MA_20'] = df_kospi['Close'].rolling(window=20).mean()
        df_kospi['MA_60'] = df_kospi['Close'].rolling(window=60).mean()
        
        latest = df_kospi.iloc[-1]
        
        score = 0
        reasons = []
        
        # 시황 판단 로직: 코스피 종가가 20일선 위에 있는가?
        if latest['Close'] > latest['MA_20']:
            score += 10
            reasons.append("코스피 단기 추세 양호 (종가가 20일선 위): 시장 전체가 단기적인 상승 흐름을 타고 있어, 개별 종목 매매 시 승률이 비교적 높은 유리한 환경입니다.")
        else:
            score -= 5
            reasons.append("코스피 단기 하락 국면 (종가가 20일선 아래): 시장 전체가 조정을 받고 있으므로 무리한 단타나 추격 매수는 자제해야 합니다.")
            
        # 중기 추세 판단
        if latest['MA_20'] > latest['MA_60']:
            score += 10
            reasons.append("코스피 중기 추세 상승장 (20일선 > 60일선): 증시의 허리 역할을 하는 중기 추세가 살아있어 안정적인 스윙/중장기 투자가 가능합니다.")
        else:
            score -= 10
            reasons.append("코스피 중기 추세 하락장 (20일선 < 60일선): 증시에 전반적인 자금 이탈이 발생 중입니다. 현금 비중을 늘리고 매매를 보수적으로 해야 하는 시기입니다.")
            
        return {"score": score, "reasons": reasons}
