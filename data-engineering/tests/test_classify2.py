import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from processing.classify import classify

BIZ = "Manage vendors, scheduling and procurement for daily operations. " * 5
TECHY = "You will use python, sql, docker, aws and git every day. " * 3


def test_systems_administrator_is_tech():
    assert classify("Junior Systems Administrator", "")[1] == "tech"


def test_personnel_is_hr():
    assert classify("Personnel Specialist", "")[:2] == ("hr_recruiting", "non_tech")


def test_generic_title_decided_by_description():
    assert classify("Project Manager", BIZ)[1] == "non_tech"
    assert classify("Project Manager", TECHY)[1] == "tech"
    assert classify("Project Manager", "")[1] == "unknown"


def test_everyday_words_are_not_tech_evidence():
    assert classify("Associate", "Take the rest of the day to react to the spring season. " * 5)[1] == "non_tech"


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("all ok")
