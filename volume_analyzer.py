import pandas as pd

class VolumeAnalyzer:
    def __init__(self, df):
        """
        :param df: OHLCV DataFrame
        """
        self.df = df.copy()
        
    def analyze(self):
        """거래량 기반 점수 및 이유 분석"""
        if len(self.df) < 20:
            return {"score": 0, "reasons": ["데이터가 부족하여 거래량 분석 불가"]}
            
        latest = self.df.iloc[-1]
        
        score = 0
        reasons = []
        
        # 최근 20일 평균 거래량 (오늘 제외)
        avg_volume_20 = self.df['Volume'].rolling(window=20).mean().iloc[-2]
        
        # 오늘 거래량이 0이거나 데이터가 이상할 경우 방어 코드
        if pd.isna(avg_volume_20) or avg_volume_20 == 0:
            return {"score": 0, "reasons": ["평균 거래량 산출 불가"]}
            
        # 1. 거래량 급증 확인 (20일 평균 대비 300% 이상)
        vol_ratio = latest['Volume'] / avg_volume_20
        
        if vol_ratio >= 3.0:
            # 양봉인지 음봉인지 판단 (종가 >= 시가)
            if latest['Close'] >= latest['Open']:
                score += 15
                reasons.append(f"대량 거래량 동반 양봉 발생 (평균 대비 {vol_ratio:.1f}배 급증!): 평소보다 엄청난 매수세가 유입되었습니다. 세력의 매집이나 강력한 호재가 수반되었을 가능성이 커 주가 상승의 큰 원동력이 됩니다.")
            else:
                score -= 10
                reasons.append(f"대량 거래량 동반 음봉 발생 (평균 대비 {vol_ratio:.1f}배 급증!): 단기 고점에서 세력이나 큰 손들이 물량을 털고(차익실현) 나갔을 가능성이 높은 매우 위험한 신호입니다.")
        elif vol_ratio >= 1.5 and latest['Close'] >= latest['Open']:
            score += 5
            reasons.append(f"의미 있는 거래량 증가와 함께 상승 (평균 대비 {vol_ratio:.1f}배): 시장의 관심을 받으며 안정적인 매수세가 유입되고 있습니다.")
        else:
            reasons.append(f"거래량 특이사항 없음: 최근 20일 평균 거래량과 비슷한 수준({vol_ratio:.1f}배)입니다. 시장의 큰 이목을 끄는 폭발적인 수급 이동은 없는 상태입니다.")

        return {"score": score, "reasons": reasons}
