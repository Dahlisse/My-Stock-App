# module_11.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import multiprocessing as mp
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

# from module_04 import simulate_strategy_once  # 현재 미사용
from modules.module_04 import generate_dummy_portfolio, calc_performance_metrics


class MassiveBacktester:
    def __init__(self, strategy_fn, scenario_generator, max_runs=100_000):
        self.strategy_fn = strategy_fn
        self.scenario_generator = scenario_generator
        self.max_runs = max_runs
        self.results = []

    def _run_single_simulation(self, args):
        scenario = args
        try:
            np.random.seed()  # 각 프로세스별 시드 분리
            result = self.strategy_fn(scenario)
            return result
        except Exception as e:
            return {"error": str(e)}

    def run(self, parallel=True):
        print(f"▶️ 시작: 전략 x 시나리오 반복 백테스트 (총 {self.max_runs:,}회)")
        scenarios = self.scenario_generator(self.max_runs)

        if parallel:
            with mp.Pool(processes=mp.cpu_count()) as pool:
                self.results = list(
                    tqdm(pool.imap(self._run_single_simulation, scenarios), total=self.max_runs)
                )
        else:
            self.results = [self._run_single_simulation(s) for s in tqdm(scenarios)]

        self.results = [
            r for r in self.results if isinstance(r, dict) and "return" in r and not "error" in r
        ]
        print(f"✅ 완료: 유효 결과 {len(self.results):,}건 저장됨")
        return pd.DataFrame(self.results)

    def summarize_distribution(self, df):
        print("📊 수익률/위험 분포 요약 중...")

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        sns.histplot(df["return"], bins=50, ax=axes[0], kde=True)
        axes[0].axvline(df["return"].mean(), color="red", linestyle="--", label="평균")
        axes[0].set_title("수익률 분포")
        axes[0].legend()

        sns.histplot(df["mdd"], bins=50, ax=axes[1], kde=True, color="orange")
        axes[1].set_title("최대 낙폭 (MDD) 분포")

        sns.histplot(df["volatility"], bins=50, ax=axes[2], kde=True, color="green")
        axes[2].set_title("변동성 분포")

        plt.tight_layout()
        plt.show()

        print(f"""
📌 통계 요약:
- 수익률 평균: {df['return'].mean():.2%}, 중앙값: {df['return'].median():.2%}
- MDD 평균: {df['mdd'].mean():.2%}
- 변동성 평균: {df['volatility'].mean():.2%}
        """)

    def analyze_survival(self, df):
        print("📈 전략 생존력 분석 중...")

        df["cv"] = df["volatility"] / (df["return"] + 1e-6)
        df["stability_score"] = 1 / (1 + df["cv"])

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(df["stability_score"], bins=50, ax=ax, color="purple")
        ax.set_title("Stability Score 분포 (전략 안정성)")

        plt.axvline(df["stability_score"].mean(), color="red", linestyle="--", label="평균 안정성")
        plt.legend()
        plt.tight_layout()
        plt.show()

        print(f"""
📌 생존력 분석:
- 전략 평균 안정성 점수: {df["stability_score"].mean():.3f}
- 전략 수명 추정 (상대적 기준):
   - 최저 안정성 전략 수명 짧음
   - 최상위 10% 전략 장기 생존 가능성 높음
        """)

        return df.sort_values("stability_score", ascending=False).head(10)


# ✅ 시나리오 예시 생성기
def sample_scenario_generator(n):
    scenarios = []
    for _ in range(n):
        scenarios.append({
            "seed": np.random.randint(0, 1e6),
            "days": np.random.choice([252, 504, 756]),  # 1~3년
        })
    return scenarios


# ✅ 전략 함수 예시 (generate_dummy_portfolio 활용)
def example_strategy_fn(scenario):
    seed = scenario.get("seed", None)
    days = scenario.get("days", 252)
    df = generate_dummy_portfolio(days=days, seed=seed)
    metrics = calc_performance_metrics(df)
    metrics["scenario"] = scenario
    return metrics


# ✅ 실행 예시
if __name__ == "__main__":
    tester = MassiveBacktester(
        strategy_fn=example_strategy_fn,
        scenario_generator=sample_scenario_generator,
        max_runs=5000
    )
    df_results = tester.run()
    tester.summarize_distribution(df_results)
    top_strategies = tester.analyze_survival(df_results)
    print(top_strategies.head(3))