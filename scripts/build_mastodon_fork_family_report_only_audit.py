from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from apk_sbom.no_maven_fork_family_experiment import main


if __name__ == "__main__":
    raise SystemExit(main())
