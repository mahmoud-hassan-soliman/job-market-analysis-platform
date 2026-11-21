import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from processing.classify import classify


def kind(title, desc=""):
    return classify(title, desc)[1]


def test_team_examples_are_not_tech():
    for t in ("Auditor", "Marketing Manager", "Recruiter"):
        assert kind(t) == "non_tech", t


def test_clear_tech_titles():
    for t in ("Software Engineer (Backend)", "DevOps Engineer", "Data Scientist", "Help Desk Technician"):
        assert kind(t) == "tech", t


def test_conflicting_title_is_unknown():
    assert kind("Cloud Sales Manager") == "unknown"
    assert kind("Data Analyst - Finance") == "unknown"
    assert kind("Technical Recruiter") == "non_tech"  # a recruiter is not a tech job


def test_unclear_title_needs_description_evidence():
    assert kind("Specialist", "we use python sql docker aws daily") == "tech"
    assert kind("Specialist", "great team, nice office") == "unknown"


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("all ok")
