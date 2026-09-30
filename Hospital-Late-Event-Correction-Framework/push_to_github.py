"""
Push the local Git repository to your GitHub repository
Usage:
    python push_to_github.py <github_repo_url>
Example:
    python push_to_github.py https://github.com/jayashri/Hospital-Late-Event-Correction-Framework.git
"""
import sys
import os
from dulwich import porcelain

def push_repo(remote_url=None):
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    if not remote_url:
        if len(sys.argv) > 1:
            remote_url = sys.argv[1]
        else:
            print("\n" + "="*70)
            print("GITHUB REPOSITORY PUSH UTILITY")
            print("="*70)
            print("1. Go to https://github.com/new and create a new repository")
            print("   (e.g., 'Hospital-Late-Event-Correction-Framework')")
            print("2. Copy your repository HTTPS URL.")
            print("="*70)
            remote_url = input("\nEnter your GitHub repository URL: ").strip()

    if not remote_url:
        print("Error: No repository URL provided.")
        return

    print(f"\nAdding remote 'origin' -> {remote_url}...")
    try:
        porcelain.remote_add(repo_dir, "origin", remote_url)
    except Exception as e:
        print(f"Remote note: {e}")

    print("Pushing 'master' branch to GitHub...")
    try:
        porcelain.push(repo_dir, remote_url, refspecs=["refs/heads/master:refs/heads/main"])
        print("\nSUCCESS! Successfully pushed your project to GitHub!")
    except Exception as e:
        print(f"\nPush notice: {e}")
        print("\nAlternative standard commands:")
        print(f"  git remote add origin {remote_url}")
        print("  git branch -M main")
        print("  git push -u origin main")

if __name__ == "__main__":
    push_repo()
