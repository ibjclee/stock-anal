import requests
from bs4 import BeautifulSoup

class CatalystAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol
        # 간단한 긍정/부정 키워드 사전
        self.positive_keywords = ['특징주', '수주', '단독', '흑자', '돌파', '상승', '급등', 'MOU', '개발', '최대', '신작']
        self.negative_keywords = ['하락', '적자', '횡령', '매도', '소송', '급락', '유상증자', '배임', '악재', '우려']

    def fetch_news_headlines(self):
        """네이버 금융에서 종목 뉴스 최신 기사 제목과 링크를 수집합니다."""
        url = f"https://finance.naver.com/item/main.naver?code={self.symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 제목 추출
            titles = soup.select('.news_section ul li a')
            headlines = []
            for a in titles:
                text = a.get_text().strip()
                if len(text) > 5:
                    link = "https://finance.naver.com" + a['href'] if a['href'].startswith('/') else a['href']
                    headlines.append({'title': text, 'url': link})
            return headlines
        except Exception as e:
            return []

    def analyze(self):
        """뉴스 제목을 바탕으로 재료(호재/악재) 점수를 평가합니다."""
        headlines = self.fetch_news_headlines()
        
        if not headlines:
            return {"score": 0, "reasons": ["최근 뉴스 기사를 불러올 수 없어 재료 파악이 제한적입니다."], "headlines": []}

        score = 0
        reasons = []
        pos_count = 0
        neg_count = 0
        
        for headline in headlines:
            title = headline['title']
            # 긍정 키워드 확인
            for keyword in self.positive_keywords:
                if keyword in title:
                    score += 2
                    pos_count += 1
                    break # 한 기사에 여러 키워드가 있어도 중복 적용 방지
            
            # 부정 키워드 확인
            for keyword in self.negative_keywords:
                if keyword in title:
                    score -= 5 # 악재는 리스크가 크므로 감점을 더 크게 설정
                    neg_count += 1
                    break

        if pos_count > 0:
            reasons.append(f"호재성 키워드 뉴스 {pos_count}건 발견: 단기적인 매수 심리를 자극할 좋은 재료가 존재합니다.")
        if neg_count > 0:
            reasons.append(f"악재성 키워드 뉴스 {neg_count}건 발견 (주의!): 투자 심리를 위축시킬 만한 리스크(악재)가 확인되었습니다.")
        
        if score == 0 and pos_count == 0 and neg_count == 0:
            reasons.append("최근 뉴스에서 특별한 호재/악재 키워드 미발견: 현재 주가를 크게 흔들 만한 강한 재료가 보이지 않습니다.")
            
        # 최대 점수 15점, 최저 점수 -15점 제한
        score = max(min(score, 15), -15)
            
        return {"score": score, "reasons": reasons, "headlines": headlines[:3]}
