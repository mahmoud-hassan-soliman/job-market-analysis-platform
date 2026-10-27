ROLES = ["data engineer", "software engineer", "data analyst", "machine learning engineer",
         "devops engineer", "backend developer", "frontend developer", "AI engineer"]
LOCATIONS = ["Egypt", "Cairo, Egypt", "Alexandria, Egypt"]

def plan():
    return [f"{r} in {l}" for r in ROLES for l in LOCATIONS]
