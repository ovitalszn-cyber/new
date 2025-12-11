#!/usr/bin/env python3
"""
Pre-deployment verification script for Railway.

Checks that all necessary files and configurations are in place
before deploying to Railway.

Usage:
    python scripts/verify_deployment_ready.py
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple


class DeploymentVerifier:
    """Verify deployment readiness."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
    
    def check(self, condition: bool, message: str, is_warning: bool = False) -> bool:
        """Run a single check."""
        if condition:
            print(f"✅ {message}")
            self.checks_passed += 1
            return True
        else:
            if is_warning:
                print(f"⚠️  {message}")
                self.warnings += 1
            else:
                print(f"❌ {message}")
                self.checks_failed += 1
            return False
    
    def verify_files(self) -> bool:
        """Verify all required files exist."""
        print("\n📁 Checking Required Files...")
        print("-" * 60)
        
        required_files = [
            ("Dockerfile", "Docker configuration"),
            (".dockerignore", "Docker ignore file"),
            ("railway.json", "Railway configuration"),
            ("requirements.txt", "Python dependencies"),
            ("main.py", "Main application file"),
            ("scripts/run_prod.py", "Production run script"),
            ("scripts/upload_historical_db.py", "Database upload script"),
            ("scripts/smoke_tests.py", "Smoke test script"),
            ("v6/historical/database.py", "Historical database module"),
            (".env.railway.template", "Environment template"),
            ("RAILWAY_QUICKSTART.md", "Quick start guide"),
            ("RAILWAY_DEPLOYMENT_CHECKLIST.md", "Deployment checklist"),
            (".agent/workflows/railway-deployment.md", "Deployment workflow"),
        ]
        
        all_exist = True
        for file_path, description in required_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            self.check(exists, f"{description}: {file_path}")
            all_exist = all_exist and exists
        
        return all_exist
    
    def verify_database_file(self) -> bool:
        """Verify historical database file exists."""
        print("\n💾 Checking Historical Database...")
        print("-" * 60)
        
        db_path = self.project_root / "kashrock_historical.db"
        exists = db_path.exists()
        
        if exists:
            size_gb = db_path.stat().st_size / (1024 ** 3)
            self.check(
                size_gb > 10,
                f"Historical database exists ({size_gb:.2f} GB)"
            )
            self.check(
                size_gb < 15,
                f"Database size is reasonable (< 15 GB)",
                is_warning=True
            )
        else:
            self.check(False, "Historical database file exists")
        
        return exists
    
    def verify_dockerignore(self) -> bool:
        """Verify .dockerignore excludes database."""
        print("\n🐳 Checking Docker Configuration...")
        print("-" * 60)
        
        dockerignore_path = self.project_root / ".dockerignore"
        if not dockerignore_path.exists():
            self.check(False, ".dockerignore file exists")
            return False
        
        content = dockerignore_path.read_text()
        has_db = "kashrock_historical.db" in content
        self.check(
            has_db,
            "Database file excluded from Docker builds"
        )
        
        return has_db
    
    def verify_code_changes(self) -> bool:
        """Verify code changes for Railway support."""
        print("\n💻 Checking Code Modifications...")
        print("-" * 60)
        
        # Check database.py for HISTORICAL_DB_PATH support
        db_file = self.project_root / "v6/historical/database.py"
        if db_file.exists():
            content = db_file.read_text()
            has_env_var = "HISTORICAL_DB_PATH" in content
            self.check(
                has_env_var,
                "Historical database supports HISTORICAL_DB_PATH env var"
            )
        else:
            self.check(False, "v6/historical/database.py exists")
            return False
        
        # Check Dockerfile for volume mount
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            has_volume = "/data" in content
            self.check(
                has_volume,
                "Dockerfile creates /data volume mount point"
            )
        else:
            self.check(False, "Dockerfile exists")
            return False
        
        return True
    
    def verify_scripts_executable(self) -> bool:
        """Verify scripts are executable."""
        print("\n🔧 Checking Script Permissions...")
        print("-" * 60)
        
        scripts = [
            "scripts/upload_historical_db.py",
            "scripts/smoke_tests.py",
        ]
        
        all_executable = True
        for script in scripts:
            script_path = self.project_root / script
            if script_path.exists():
                is_executable = os.access(script_path, os.X_OK)
                self.check(
                    is_executable,
                    f"{script} is executable",
                    is_warning=True
                )
                all_executable = all_executable and is_executable
        
        return all_executable
    
    def verify_git_status(self) -> bool:
        """Verify git repository status."""
        print("\n📦 Checking Git Repository...")
        print("-" * 60)
        
        git_dir = self.project_root / ".git"
        is_git_repo = git_dir.exists()
        self.check(is_git_repo, "Project is a git repository")
        
        if is_git_repo:
            gitignore = self.project_root / ".gitignore"
            if gitignore.exists():
                content = gitignore.read_text()
                ignores_db = "kashrock_historical.db" in content
                self.check(
                    ignores_db,
                    "Database file is in .gitignore"
                )
            else:
                self.check(False, ".gitignore exists", is_warning=True)
        
        return is_git_repo
    
    def check_environment_template(self) -> bool:
        """Check environment template has all required variables."""
        print("\n🔐 Checking Environment Configuration...")
        print("-" * 60)
        
        template_path = self.project_root / ".env.railway.template"
        if not template_path.exists():
            self.check(False, "Environment template exists")
            return False
        
        content = template_path.read_text()
        required_vars = [
            "HISTORICAL_DB_PATH",
            "PORT",
            "SECRET_KEY",
            "ADMIN_SECRET",
            "GOOGLE_CLIENT_ID",
        ]
        
        all_present = True
        for var in required_vars:
            present = var in content
            self.check(present, f"Template includes {var}")
            all_present = all_present and present
        
        return all_present
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("=" * 60)
        print("🔍 Railway Deployment Verification")
        print("=" * 60)
        
        self.verify_files()
        self.verify_database_file()
        self.verify_dockerignore()
        self.verify_code_changes()
        self.verify_scripts_executable()
        self.verify_git_status()
        self.check_environment_template()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Verification Summary")
        print("=" * 60)
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print()
        
        if self.checks_failed == 0:
            print("🎉 All critical checks passed! Ready to deploy.")
            print()
            print("Next steps:")
            print("1. Review RAILWAY_QUICKSTART.md")
            print("2. Set up Railway account and CLI")
            print("3. Configure environment variables")
            print("4. Deploy with: railway up")
            print()
            return True
        else:
            print("⚠️  Some checks failed. Please fix issues before deploying.")
            print()
            return False


def main():
    """Main entry point."""
    verifier = DeploymentVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
