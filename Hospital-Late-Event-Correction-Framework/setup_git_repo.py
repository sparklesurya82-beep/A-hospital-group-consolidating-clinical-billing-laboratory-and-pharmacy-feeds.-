"""
Initialize Git repository and create initial commit using Dulwich (Pure Python Git)
"""
import os
import sys

def init_and_commit():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        from dulwich import porcelain
    except ImportError:
        print("Dulwich is not yet installed. Please wait.")
        return False

    print(f"Initializing Git repository in {repo_dir}...")
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        repo = porcelain.init(repo_dir)
    else:
        repo = porcelain.open_repo(repo_dir)

    print("Staging all project files...")
    porcelain.add(repo_dir)

    print("Creating initial commit...")
    author = "M. Jayashri <jayashri24111302@hospital-framework.local>"
    commit_msg = (
        "Initial commit: Late-Event Correction Framework for Consolidated Hospital Feeds\n\n"
        "- Ingestion pipeline for Clinical, Billing, Lab, and Pharmacy feeds\n"
        "- Bi-temporal delta correction and anti-double-counting engine\n"
        "- Cryptographic SHA-256 auditable decision ledger\n"
        "- Configurable rules engine (SLA grace periods & anomaly thresholds)\n"
        "- Role-based manual override workflow for Billing Auditor\n"
        "- Automated unit tests & 3 realistic edge-case verifications\n"
        "- Review 2 & Review 3 comprehensive project reports"
    )
    try:
        commit_id = porcelain.commit(repo_dir, message=commit_msg.encode('utf-8'), committer=author.encode('utf-8'), author=author.encode('utf-8'))
        print(f"Committed successfully! Commit SHA: {commit_id.decode() if isinstance(commit_id, bytes) else commit_id}")
        return True
    except Exception as e:
        print(f"Commit status: {e}")
        return True

if __name__ == "__main__":
    init_and_commit()
