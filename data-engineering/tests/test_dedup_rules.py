import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from processing.dedup import tnorm


def test_backend_and_mobile_titles_differ():
    assert tnorm("Software Engineer (Backend)") != tnorm("Software Engineer (Mobile)")


def test_noise_words_still_ignored():
    assert tnorm("Data Engineer (m/f)") == tnorm("Data Engineer")
    assert tnorm("Data Engineer - Remote") == tnorm("Data Engineer")


if __name__ == "__main__":
    test_backend_and_mobile_titles_differ(); test_noise_words_still_ignored(); print("all ok")
