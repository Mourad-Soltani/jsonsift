# Tests for JsonSift
# Built by Mourad.Soltani

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent


def run_cli(*args, input_data=None):
    cmd = [sys.executable, str(ROOT / "jsonsift.py"), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, input=input_data)
    return result.returncode, result.stdout, result.stderr


def test_health():
    code, out, err = run_cli("health")
    assert code == 0
    data = json.loads(out)
    assert data["status"] == "ok"
    assert "Mourad.Soltani" in data["author"]
    assert "version" in data


def test_pretty():
    sample = {"name": "JsonSift", "version": 1, "ok": True}
    code, out, err = run_cli("pretty", "-", input_data=json.dumps(sample))
    assert code == 0
    loaded = json.loads(out)
    assert loaded == sample


def test_validate_ok():
    code, out, err = run_cli("validate", "-", input_data='{"a":1}')
    assert code == 0
    assert "Valid JSON" in out


def test_validate_bad():
    code, out, err = run_cli("validate", "-", input_data="{not json")
    assert code == 1
    assert "Invalid" in err


def test_extract():
    sample = {"user": {"name": "Ada", "roles": ["admin", "dev"]}}
    code, out, err = run_cli("extract", "-", "user.roles[0]", input_data=json.dumps(sample))
    assert code == 0
    assert "admin" in out


def test_diff_same():
    a = {"x": 1}
    code, out, err = run_cli("diff", "-", "-", input_data=json.dumps(a) + "\n" + json.dumps(a))
    # Note: stdin is consumed once; for real tests we use files
    # Use temp files instead
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1, \
         tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f2:
        json.dump(a, f1)
        json.dump(a, f2)
        f1.flush(); f2.flush()
        code, out, err = run_cli("diff", f1.name, f2.name)
        assert code == 0
        assert "No differences" in out


def test_diff_changed():
    left = {"name": "old", "count": 1}
    right = {"name": "new", "count": 2, "extra": True}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1, \
         tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f2:
        json.dump(left, f1)
        json.dump(right, f2)
        f1.flush(); f2.flush()
        code, out, err = run_cli("diff", f1.name, f2.name)
        assert code == 1
        assert "name" in out
        assert "count" in out
        assert "extra: added" in out


if __name__ == "__main__":
    test_health()
    test_pretty()
    test_validate_ok()
    test_validate_bad()
    test_extract()
    test_diff_same()
    test_diff_changed()
    print("All tests passed")
