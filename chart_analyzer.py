import pandas as pd
from ta.momentum import StochasticOscillator
from ta.trend import SMAIndicator

class ChartAnalyzer:
    def __init__(self, df):
        """
        :param df: OHLCV DataFrame
        """
        self.df = df.copy()
        
    def add_indicators(self):
        """이동평균선 및 스토캐스틱 지표 추가"""
        # 이동평균선 추가 (5, 20, 60, 120, 200일)
        for period in [5, 20, 60, 120, 200]:
            sma = SMAIndicator(close=self.df['Close'], window=period)
            self.df[f'MA_{period}'] = sma.sma_indicator()
            
        # 스토캐스틱 슬로우 (Stochastic Slow)
        # ta 라이브러리의 StochasticOscillator는 Fast %K, Slow %K(=Fast %D)를 제공함.
        stoch = StochasticOscillator(
            high=self.df['High'], 
            low=self.df['Low'], 
            close=self.df['Close'], 
            window=12, 
            smooth_window=5
        )
        # Slow %K
        self.df['Stoch_Slow_K'] = stoch.stoch_signal() 
        # Slow %D (Slow %K의 5일 이동평균)
        self.df['Stoch_Slow_D'] = self.df['Stoch_Slow_K'].rolling(window=5).mean()
        
        return self.df

    def analyze(self):
        """차트 기반 점수 및 이유 분석"""
        self.add_indicators()
        
        # 분석에 필요한 데이터가 충분하지 않으면 예외처리
        if len(self.df) < 120:
            return {"score": 0, "reasons": ["데이터가 120일 미만이라 분석이 제한적입니다."]}
            
        latest = self.df.iloc[-1]
        prev = self.df.iloc[-2]
        
        score = 0
        reasons = []
        
        # 1. 이동평균선 분석
        if latest['MA_5'] > latest['MA_20'] > latest['MA_60'] > latest['MA_120'] > latest['MA_200']:
            score += 10
            reasons.append("이동평균선 완벽 정배열 (5>20>60>120>200): 단기부터 장기까지 모든 추세가 우상향하고 있어 매우 강력하고 안정적인 상승 추세입니다.")
        elif latest['MA_5'] > latest['MA_20'] > latest['MA_60'] > latest['MA_120']:
            score += 8
            reasons.append("이동평균선 정배열 (장단기 상승 추세): 주가가 꾸준히 오르며 상승 흐름을 타고 있습니다.")
        elif latest['MA_5'] < latest['MA_20'] < latest['MA_60'] < latest['MA_120']:
            score -= 10
            reasons.append("이동평균선 역배열 (하락 추세 지속 중): 겹겹이 저항선이 자리 잡고 있어 당분간 의미 있는 상승이 어려울 수 있습니다.")
            
        # 2. 스토캐스틱 슬로우 분석
        # 골든크로스 파악 (이전엔 K < D 였는데 최근엔 K > D)
        if prev['Stoch_Slow_K'] <= prev['Stoch_Slow_D'] and latest['Stoch_Slow_K'] > latest['Stoch_Slow_D']:
            if latest['Stoch_Slow_K'] <= 20:
                score += 15
                reasons.append("스토캐스틱 침체권(20 이하) 골든크로스 발생: 주가가 과도하게 하락한 상태(과매도)에서 매수세가 들어오며 단기적인 강력한 반등 타점입니다.")
            else:
                score += 5
                reasons.append("스토캐스틱 골든크로스 발생: 단기적인 추세가 하락에서 상승으로 턴(Turn)하려는 신호입니다.")
                
        # 데드크로스 파악
        if prev['Stoch_Slow_K'] >= prev['Stoch_Slow_D'] and latest['Stoch_Slow_K'] < latest['Stoch_Slow_D']:
            if latest['Stoch_Slow_K'] >= 80:
                score -= 15
                reasons.append("스토캐스틱 과열권(80 이상) 데드크로스 발생: 주가가 과열(과매수)되어 곧 차익실현 매물이 쏟아질 수 있는 단기 고점 신호입니다.")
            else:
                score -= 5
                reasons.append("스토캐스틱 데드크로스 발생: 단기 상승 흐름이 꺾이고 하락 전환될 위험이 있습니다.")

        return {"score": score, "reasons": reasons}
