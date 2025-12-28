"""
Wrapper to re-run the build_embeddings process. Useful for cron or CI.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_embeddings.py"
PY = sys.executable


def main():
    print("=" * 60)
    print("Running reindex job:", BUILD_SCRIPT)
    print("=" * 60)
    
    rc = subprocess.call([PY, str(BUILD_SCRIPT)])
    
    if rc != 0:
        print("\n❌ Reindex failed with return code", rc)
        raise SystemExit(rc)
    
    print("\n✅ Reindex finished successfully.")


if __name__ == "__main__":
    main()
