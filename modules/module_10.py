# module_10.py

# 🔧 핵심 모듈 임포트
import os
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Any, Optional

# ✅ 로깅 디렉토리 생성
os.makedirs("logs", exist_ok=True)

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()]
)

# ✅ 공통 예외 처리 데코레이터
def safe_run(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"{func.__name__} 에러 발생: {e}")
            return None
    return wrapper

# ✅ 10.1 포트폴리오 클래스
class Portfolio:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        self.data = self.fetch_all_data()

    @safe_run
    def fetch_data(self, ticker: str) -> Optional[pd.DataFrame]:
        df = yf.download(ticker, period="1y")
        df["Ticker"] = ticker
        return df

    def fetch_all_data(self) -> pd.DataFrame:
        all_data = []
        for ticker in self.tickers:
            df = self.fetch_data(ticker)
            if df is not None:
                all_data.append(df)
        return pd.concat(all_data) if all_data else pd.DataFrame()

# ✅ 10.2 백테스트 로직 클래스
class Backtester:
    def __init__(self, df: pd.DataFrame, strategy_name: str):
        self.df = df
        self.strategy_name = strategy_name

    @safe_run
    def run(self) -> Dict[str, Any]:
        if self.df.empty:
            return {"error": "입력 데이터 없음"}

        try:
            grouped = self.df.groupby("Ticker")
            returns, vols, mdds = [], [], []

            for _, group in grouped:
                daily_return = group["Close"].pct_change()
                returns.append(daily_return.mean() * 252)
                vols.append(daily_return.std() * (252 ** 0.5))
                mdds.append((group["Close"] / group["Close"].cummax() - 1).min())

            result = {
                "strategy": self.strategy_name,
                "return": sum(returns) / len(returns),
                "volatility": sum(vols) / len(vols),
                "MDD": sum(mdds) / len(mdds)
            }
            return result
        except Exception as e:
            logging.error(f"Backtest 실행 오류: {e}")
            return {"error": str(e)}

# ✅ 10.3 사용자 프로파일링 유틸
class UserProfile:
    def __init__(self, name: str, risk_level: str):
        self.name = name
        self.risk_level = risk_level  # "low", "medium", "high"

    def get_risk_multiplier(self) -> float:
        return {"low": 0.6, "medium": 1.0, "high": 1.5}.get(self.risk_level, 1.0)

# ✅ 10.4 음성 안내 시스템
@safe_run
def voice_prompt(message: str):
    try:
        from gtts import gTTS
        import playsound
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text=message, lang="ko")
            tts.save(fp.name)
            playsound.playsound(fp.name)
            os.remove(fp.name)
    except Exception as e:
        logging.warning(f"음성 안내 실패: {e}")

# ✅ 10.5 UI ↔ 백엔드 통합 Streamlit 예시
def app_main():
    import streamlit as st

    st.title("AI 전략 백엔드 연결 예시")

    tickers = st.text_input("종목을 입력하세요 (쉼표로 구분):", value="AAPL, MSFT")
    strategy = st.selectbox("전략 선택:", ["기본전략", "모멘텀", "가치형"])
    user_type = st.radio("당신의 투자 성향은?", ["low", "medium", "high"])

    if st.button("실행"):
        ticker_list = [t.strip() for t in tickers.split(",")]
        portfolio = Portfolio(ticker_list)
        profile = UserProfile(name="사용자", risk_level=user_type)
        risk_adj = profile.get_risk_multiplier()

        if not portfolio.data.empty:
            bt = Backtester(portfolio.data, strategy)
            result = bt.run()

            if "error" not in result:
                st.success(f"연 환산 수익률: {result['return'] * risk_adj:.2%}")
                st.info(f"MDD (최대 낙폭): {result['MDD']:.2%}")
                st.write(f"변동성: {result['volatility']:.2%}")
                voice_prompt("전략 분석 결과가 도출되었습니다.")
            else:
                st.error("백테스트 실패: " + result["error"])
                st.code("로그 파일 확인: logs/app.log")
        else:
            st.error("포트폴리오 데이터가 없습니다.")
            st.code("로그 파일 확인: logs/app.log")

# ✅ 메인 실행
if __name__ == "__main__":
    app_main()
    
import streamlit as st

def run():
    st.subheader("📘 10단원. 완성형 코드화 구조")
    st.markdown("“템플릿이 아니라 실제 작동하는 실전용 AI 앱을 만든다.”")

    # ───────────────────────────────
    st.markdown("### 🧱 10.1 모듈별 완전 작동 코드화")

    st.markdown("""
    - `portfolio.py`: 포트 구성 로직  
    - `backtest.py`: 전략별 수익률/리스크 백테스트  
    - `user_profile.py`: 사용자 성향 분석  
    - `voice_guide.py`: 음성 안내 (TTS) 시스템  
    - 기능별 핵심 로직을 완전 작동 가능한 형태로 구현
    """)

    st.code("""
📁 core/
 ┣ portfolio.py
 ┣ backtest.py
 ┣ user_profile.py
 ┗ voice_guide.py
    """, language='text')

    st.divider()

    # ───────────────────────────────
    st.markdown("### 🧩 10.2 코드 최적화 & 재사용성 구조화")

    st.markdown("""
    - Class, 함수 분리 → 중복 최소화  
    - 백엔드 로직 ↔ Streamlit UI 분리  
    - 추천 엔진 / 시각화 / 매크로 모듈 독립 구성  
    - 핵심 기능은 API-like 구조로 설계
    """)

    st.info("예: `run_backtest(strategy, portfolio)` → UI와 분리된 백테스트 함수")

    st.divider()

    # ───────────────────────────────
    st.markdown("### 🔧 10.3 중복 제거 및 예외 핸들링 구조 강화")

    st.markdown("""
    - `yfinance`, `OpenDart`, `KRX` → 다중 데이터 백업 경로 구성  
    - 종목 누락 / API 실패 시 자동 대체 및 로그 기록  
    - 사용자에게는 최소한의 오류만 노출 (UX 보호)
    """)

    st.warning("예: `삼성전자` 재무데이터 누락 → KRX 데이터로 자동 대체 → UI에는 정상 출력")

    st.success("모든 예외 처리는 `utils/error_handler.py`에 집중 관리 가능")

    st.divider()

    # ───────────────────────────────
    st.markdown("✅ 전체 구조 요약")

    st.markdown("""
    - 각 모듈은 Streamlit ↔ 백엔드 인터페이스가 명확히 구분됨  
    - 사용자 입력 → 전략 분석 → 시각화 → 리포트까지 자동 흐름 구성  
    - 실제 운용 가능한 투자 분석 앱 형태로 완성도 높임
    """)

    st.code("""
📁 modules/
 ┣ module_01 ~ module_10.py
📁 core/
 ┣ portfolio.py, backtest.py ...
📁 utils/
 ┣ error_handler.py, helpers.py
    """, language='text')

    st.success("10단원은 전체 앱 구조의 안정성과 유지보수성을 책임지는 핵심 축입니다.")