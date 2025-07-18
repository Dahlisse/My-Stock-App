"""
12단원. 자동 배포 및 CI/CD

- GitHub Actions 자동화
- API Key 보안 연동 (.streamlit/secrets.toml)
- Pytest 기반 테스트 자동화
"""

import os
import subprocess
from typing import List


class CICDManager:
    def __init__(self, project_root="."):
        self.project_root = project_root
        self.workflow_path = os.path.join(project_root, ".github", "workflows")
        self.secrets_path = os.path.join(project_root, ".streamlit", "secrets.toml")

    def init_github_actions(self):
        """
        GitHub Actions 설정 파일 생성: .github/workflows/deploy.yml
        """
        os.makedirs(self.workflow_path, exist_ok=True)
        deploy_script = """
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest coverage

      - name: Run tests
        run: |
          coverage run -m pytest
          coverage report

      - name: Deploy to Streamlit
        run: echo "✅ Streamlit deploy assumed via Streamlit Cloud"
        """.strip()

        workflow_file = os.path.join(self.workflow_path, "deploy.yml")
        with open(workflow_file, "w") as f:
            f.write(deploy_script)

        print(f"✅ GitHub Actions workflow 파일 생성 완료: {workflow_file}")

    def init_secrets_file(self, keys: dict):
        """
        secrets.toml 생성 및 API Key 저장 구조화
        """
        os.makedirs(os.path.dirname(self.secrets_path), exist_ok=True)

        with open(self.secrets_path, "w", encoding="utf-8") as f:
            for key, value in keys.items():
                safe_value = str(value).replace('"', '\\"')  # Escape safety
                f.write(f'{key} = "{safe_value}"\n')

        print(f"✅ secrets.toml 생성 완료: {self.secrets_path}")

    def run_tests(self, target_files: List[str] = ["tests"]):
        """
        pytest 테스트 실행 및 커버리지 출력
        """
        for path in target_files:
            if not os.path.exists(path):
                print(f"⚠️ 경고: 테스트 경로 없음 - {path}")

        try:
            print("🔍 테스트 실행 중...")
            subprocess.run(["coverage", "run", "-m", "pytest", *target_files], check=True, text=True)
            subprocess.run(["coverage", "report"], check=True, text=True)
            print("✅ 테스트 통과 및 커버리지 출력 완료")
        except subprocess.CalledProcessError:
            print("❌ 테스트 실패! 배포 중단됨.")
            raise

    def validate_git_status(self):
        """
        푸시 전 커밋/브랜치 상태 확인
        """
        try:
            branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
            print(f"🔁 현재 브랜치: {branch}")
        except subprocess.CalledProcessError:
            raise RuntimeError("❌ Git 브랜치를 확인할 수 없습니다.")

        if branch not in ["main", "staging"]:
            raise ValueError("⚠️ main 또는 staging 브랜치에서만 푸시 가능합니다.")


# CLI 실행 예시
if __name__ == "__main__":
    cicd = CICDManager()

    # 사용자 확인
    confirm = input("⚙️ CI/CD 자동화를 진행할까요? (y/n): ").lower().strip()
    if confirm != "y":
        print("❎ 중단됨.")
        exit()

    cicd.validate_git_status()
    cicd.init_github_actions()
    cicd.init_secrets_file({
        "YFINANCE_API_KEY": "your_yfinance_key",
        "OPENDART_API_KEY": "your_dart_key"
    })
    cicd.run_tests()
    print("🎉 CI/CD 자동 구성 완료. GitHub Actions 및 secrets.toml 설정 완료.")
    
    import streamlit as st

def run():
    st.subheader("📘 12. 사용자 성향 기반 전략 추천 & 트레이드 오프 분석")
    st.markdown("“사용자의 투자 성향에 맞는 전략을 AI가 자동 추천합니다.”")

    st.markdown("### ✅ 12.1 사용자 성향 분석")
    st.markdown("- 투자 성향, 리스크 선호도, 투자 목표 등을 기반으로 추천 전략을 달리합니다.")
    
    # 사용자 성향 간단 입력 (예시)
    risk_profile = st.selectbox("당신의 리스크 선호도는?", ["보수형", "중립형", "공격형"])
    goal = st.selectbox("주요 투자 목표는?", ["안정적인 수익", "균형된 성과", "고수익 추구"])
    
    st.markdown("### ✅ 12.2 전략 추천")
    if st.button("📌 나에게 맞는 전략 추천받기"):
        if risk_profile == "보수형":
            st.success("🛡 추천 전략: 안정형 배당주 중심 포트")
        elif risk_profile == "중립형":
            st.success("⚖️ 추천 전략: 성장+가치 균형 전략")
        else:
            st.success("🚀 추천 전략: 고성장 모멘텀 기반 AI 전략")
        # 실제 추천 알고리즘과 연동 가능

    st.markdown("### ✅ 12.3 전략 트레이드오프 분석")
    st.markdown("- 전략 A vs B vs C의 핵심 비교:")
    st.markdown("""
    - 📈 누적 수익률
    - 📉 최대 낙폭(MDD)
    - 📊 리스크-보상 비율
    - 🧠 심리/매크로 적합도 점수
    - ⏳ 최근 10년간 성공 확률
    """)

    if st.button("🔍 전략 트레이드오프 보기"):
        st.info("예: 전략 A는 수익률은 높지만 변동성이 크고, 전략 B는 안정적이지만 수익이 낮습니다.")
        # 실제 시각화 및 표/그래프 삽입 가능

    st.markdown("### ✅ 사용자 맞춤 전략 민감도 조정")
    st.markdown("- module_24를 통해 감지된 심리 편향(예: 조기매도 습관)은 전략 제안에 반영됩니다.")