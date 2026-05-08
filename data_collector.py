import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import os

class StockDataFetcher:
    def __init__(self):
        # 종목명 검색을 위해 KRX 전체 종목 목록을 가져옵니다.
        try:
            self.krx_list = fdr.StockListing('KRX')
        except Exception as e:
            try:
                # Fallback: try KRX-DESC which uses a different endpoint
                self.krx_list = fdr.StockListing('KRX-DESC')
            except Exception as e2:
                # Fallback 2: Local CSV
                csv_path = os.path.join(os.path.dirname(__file__), 'krx_list.csv')
                if os.path.exists(csv_path):
                    self.krx_list = pd.read_csv(csv_path, dtype={'Code': str})
                else:
                    self.krx_list = None
                    self.krx_error = f"KRX: {e}, KRX-DESC: {e2}"
            
    def get_code_by_name(self, name_or_code):
        """이름을 입력하면 코드로, 코드를 입력하면 그대로 반환합니다."""
        if name_or_code.isdigit() and len(name_or_code) == 6:
            return name_or_code
            
        if self.krx_list is not None:
            # 종목명으로 검색
            result = self.krx_list[self.krx_list['Name'] == name_or_code]
            if not result.empty:
                return result.iloc[0]['Code']
        return None
        
    def get_name_by_code(self, code):
        """코드를 입력하면 해당하는 종목명을 반환합니다."""
        if self.krx_list is not None:
            result = self.krx_list[self.krx_list['Code'] == code]
            if not result.empty:
                return result.iloc[0]['Name']
        return code
        
    def get_ohlcv(self, symbol_or_name, start_date=None, end_date=None):
        """
        특정 종목의 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 가져옵니다.
        """
        symbol = self.get_code_by_name(symbol_or_name)
        if not symbol:
            print(f"[{symbol_or_name}] 종목을 찾을 수 없습니다. 이름이나 코드를 확인해주세요.")
            return pd.DataFrame()

        if not end_date:
            end_date = datetime.today().strftime('%Y-%m-%d')
        if not start_date:
            # 기본적으로 최근 2년치 데이터 수집 (장기 이평선 계산 및 1년치 차트 출력을 위해)
            start_date = (datetime.today() - timedelta(days=730)).strftime('%Y-%m-%d')
            
        print(f"[{symbol_or_name}({symbol})] 데이터를 {start_date}부터 {end_date}까지 불러옵니다...")
        df = fdr.DataReader(symbol, start_date, end_date)
        return df
        
if __name__ == "__main__":
    fetcher = StockDataFetcher()
    # 테스트용
    df = fetcher.get_ohlcv('005930')
    print(df.tail())
