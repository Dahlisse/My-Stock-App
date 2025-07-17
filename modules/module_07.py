import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime
from io import BytesIO

plt.switch_backend('Agg')  # 서버 환경에서도 시각화 가능하도록 설정

# =======================================
# 7.1 전략 시각화
# =======================================

def plot_strategy_radar_chart(scores: dict, title="Strategy Profile"):
    labels = list(scores.keys())
    values = list(scores.values())
    values += values[:1]  # 차트 닫기용

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, linestyle='solid')
    ax.fill(angles, values, alpha=0.4)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title(title, size=14)
    ax.grid(True)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf

def plot_return_curve(dates, returns, title="수익률 곡선"):
    df = pd.DataFrame({"Date": pd.to_datetime(dates), "Return": returns})
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=df, x="Date", y="Return")
    plt.title(title)
    plt.xlabel("날짜")
    plt.ylabel("누적 수익률 (%)")
    plt.grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def plot_drawdown_curve(dates, portfolio_values):
    peak = np.maximum.accumulate(portfolio_values)
    drawdown = (portfolio_values - peak) / peak * 100

    plt.figure(figsize=(8, 4))
    plt.fill_between(dates, drawdown, color='red')
    plt.title("드로우다운 그래프")
    plt.xlabel("날짜")
    plt.ylabel("Drawdown (%)")
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf

def plot_monthly_heatmap(returns_df):
    returns_df['Year'] = returns_df['Date'].dt.year
    returns_df['Month'] = returns_df['Date'].dt.month
    pivot = returns_df.pivot(index='Year', columns='Month', values='Return')

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, cmap='RdYlGn_r', annot=True, fmt=".1f", linewidths=.5, center=0)
    plt.title("월간 수익률 히트맵")
    plt.xlabel("월")
    plt.ylabel("연도")
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# =======================================
# 7.2 전략 전환 흐름도
# =======================================

def plot_strategy_switch_points(dates, returns, switch_points):
    df = pd.DataFrame({'Date': pd.to_datetime(dates), 'Return': returns})
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=df, x='Date', y='Return', label='수익률')
    for idx, switch_date in enumerate(switch_points):
        plt.axvline(pd.to_datetime(switch_date), color='orange', linestyle='--',
                    label='전략 전환' if idx == 0 else None)
    plt.title("전략 전환 시점 및 수익률")
    plt.xlabel("날짜")
    plt.ylabel("누적 수익률 (%)")
    plt.grid(True)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

# =======================================
# 7.3 전략 설명 보고서 (PDF 버전)
# =======================================

class StrategyReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "AI 전략 보고서", ln=True, align='C')

    def add_section_title(self, title):
        self.ln(10)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)

    def add_text(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 7, text)

    def add_image_stream(self, img_buf, w=180):
        self.image(img_buf, x=10, y=None, w=w)
        self.ln(5)

def generate_strategy_pdf_report(output_path, summary_text, radar_buf, return_buf, dd_buf, switch_buf, heatmap_buf):
    pdf = StrategyReportPDF()
    pdf.add_page()
    pdf.add_section_title("1. 전략 요약")
    pdf.add_text(summary_text)

    pdf.add_section_title("2. 전략 레이더 차트")
    pdf.add_image_stream(radar_buf)

    pdf.add_section_title("3. 수익률 곡선")
    pdf.add_image_stream(return_buf)

    pdf.add_section_title("4. 드로우다운 분석")
    pdf.add_image_stream(dd_buf)

    pdf.add_section_title("5. 전략 전환 시점")
    pdf.add_image_stream(switch_buf)

    pdf.add_section_title("6. 월간 수익률 히트맵")
    pdf.add_image_stream(heatmap_buf)

    pdf.output(output_path)

# =======================================
# 예시 실행 코드 (테스트용)
# =======================================

if __name__ == "__main__":
    import random
    date_range = pd.date_range(start="2022-01-01", periods=500, freq="D")
    returns = np.cumsum(np.random.randn(500))
    portfolio_values = np.cumprod(1 + np.random.normal(0.001, 0.01, 500))

    radar_scores = {
        "수익성": 82,
        "안정성": 75,
        "유연성": 68,
        "심리 적합도": 71,
        "성장성": 87
    }

    switch_dates = ["2022-05-01", "2022-09-15", "2023-02-01"]

    radar_buf = plot_strategy_radar_chart(radar_scores)
    return_buf = plot_return_curve(date_range, returns)
    dd_buf = plot_drawdown_curve(date_range, portfolio_values)
    switch_buf = plot_strategy_switch_points(date_range, returns, switch_dates)

    df_monthly = pd.DataFrame({
        "Date": pd.date_range(start="2021-01-01", periods=36, freq="M"),
        "Return": np.random.normal(0.01, 0.03, 36) * 100
    })
    heatmap_buf = plot_monthly_heatmap(df_monthly)

    summary_text = (
        "이 전략은 수익성과 성장성이 높으며, 심리적 적합도도 우수한 편입니다.\n"
        "과거 데이터 기준으로 누적 수익률이 안정적이며, 드로우다운도 관리 가능한 수준입니다.\n"
        "총 3회 전략 전환이 있었으며, 매 전환 이후 성과가 개선되는 양상을 보였습니다."
    )

    output_path = "strategy_report.pdf"
    generate_strategy_pdf_report(
        output_path, summary_text,
        radar_buf, return_buf, dd_buf, switch_buf, heatmap_buf
    )
    print(f"[완료] 전략 보고서 PDF가 생성되었습니다: {output_path}")