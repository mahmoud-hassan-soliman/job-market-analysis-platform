import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from processing.load import slug


def test_keys_are_ascii_only():
    assert slug("Daftra دفترة") == "daftra"
    assert slug("دفترة") == "unknown"
    assert slug("Example Tech, Inc.") == "exampletechinc"


if __name__ == "__main__":
    test_keys_are_ascii_only(); print("all ok")
