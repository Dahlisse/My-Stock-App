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