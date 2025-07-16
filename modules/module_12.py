# module_12.py

"""
12단원. 자동 배포 및 CI/CD

- GitHub Actions 자동화
- API Key 보안 연동 (.streamlit/secrets.toml)
- Pytest 기반 테스트 자동화
"""

import os
import json
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
        deploy_script = f"""
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
        run: echo "Streamlit deploy assumed via Streamlit Cloud"        
"""
        workflow_file = os.path.join(self.workflow_path, "deploy.yml")
        with open(workflow_file, "w") as f:
            f.write(deploy_script.strip())

    def init_secrets_file(self, keys: dict):
        """
        secrets.toml 생성 및 API Key 저장 구조화
        """
        os.makedirs(os.path.dirname(self.secrets_path), exist_ok=True)

        with open(self.secrets_path, "w") as f:
            for key, value in keys.items():
                f.write(f'{key} = "{value}"\n')

    def run_tests(self, target_files: List[str] = ["tests"]):
        """
        pytest 테스트 실행 및 커버리지 출력
        """
        try:
            subprocess.run(["coverage", "run", "-m", "pytest", *target_files], check=True)
            subprocess.run(["coverage", "report"], check=True)
        except subprocess.CalledProcessError as e:
            print("❌ 테스트 실패! 배포 중단됨.")
            raise e

    def validate_git_status(self):
        """
        푸시 전 커밋/브랜치 상태 확인
        """
        branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
        print(f"현재 브랜치: {branch}")
        if branch not in ["main", "staging"]:
            raise ValueError("⚠️ main 또는 staging 브랜치에서만 푸시 가능합니다.")


# CLI 실행 예시
if __name__ == "__main__":
    cicd = CICDManager()
    cicd.validate_git_status()
    cicd.init_github_actions()
    cicd.init_secrets_file({
        "YFINANCE_API_KEY": "your_yfinance_key",
        "OPENDART_API_KEY": "your_dart_key"
    })
    cicd.run_tests()
    print("✅ CI/CD 자동 구성 완료. GitHub Actions 및 secrets.toml 설정 완료.")