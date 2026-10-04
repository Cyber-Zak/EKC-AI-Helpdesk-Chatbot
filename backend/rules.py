# Rule data for the EKC chatbot (separated from the logic in nlp_engine.py).
# Edit these lists to change behaviour; no other code needs to change.

# A query with NONE of these words goes to fallback (unless a keyword rule matches first).
DOMAIN_WORDS = {
    # Institution
    "ekc", "eranad", "college", "campus",
    # University
    "ktu", "apj", "university", "affiliated",
    # Academics
    "course", "branch", "department", "btech", "engineering",
    "cse", "ece", "eee", "mechanical", "civil", "ai",
    "semester", "exam", "internal", "external", "result",
    "grading", "cgpa", "sgpa", "credit", "attendance",
    "activity", "portal", "registration", "marklist",
    # Admission
    "admission", "apply", "keam", "eligibility",
    "seat", "quota", "nri", "lateral", "intake",
    # Finance
    "fee", "fees", "tuition", "scholarship", "loan",
    "egrant", "waiver",
    # Campus facilities
    "hostel", "library", "transport", "bus", "placement",
    "internship", "training", "nss", "fest", "ragging",
    "discipline", "conduct",
    # Contact
    "contact", "phone", "email", "address",
    # Greetings
    "hi", "hello", "hey", "bye", "goodbye", "thanks", "thank",
}

# (phrases, intent). The longest matching phrase wins.
KEYWORD_RULES = [
    (["hi", "hello", "hey", "good morning", "good evening", "good afternoon"], "greeting"),
    (["bye", "goodbye", "see you", "thank you", "thanks"], "goodbye"),

    (["fee structure", "tuition fee", "btech fee", "college fee", "hostel fee",
      "management quota fee", "government quota fee", "nri fee",
      "how much is the fee", "total fee", "mess fee"], "fees"),

    (["hostel", "boys hostel", "girls hostel", "hostel facility",
      "hostel accommodation"], "hostel"),

    (["college bus", "bus route", "transport facility",
      "bus timing", "bus pickup"], "transport"),

    (["library", "digital library", "ebooks", "reference books",
      "library timings"], "library"),

    (["placement", "campus recruitment", "top recruiters", "placement cell",
      "placement record", "average package", "job opportunities"], "placements"),

    (["internship", "industrial training", "summer internship",
      "industry exposure"], "internships"),

    (["scholarship", "egrant", "financial aid", "fee waiver",
      "minority scholarship", "merit scholarship",
      "education loan", "apply for scholarship"], "scholarships"),

    (["attendance", "attendance shortage", "minimum attendance",
      "attendance percentage", "attendance rule"], "attendance_rules"),

    (["ktu result", "semester result", "revaluation", "marklist",
      "check result", "result website"], "results"),

    (["ktu exam", "semester exam", "internal exam", "external exam",
      "exam schedule", "exam pattern", "exam rules"], "exams"),

    (["activity points", "activity point", "nss points",
      "how to get activity points", "minimum activity points"], "activity_points"),

    (["ktu portal", "student portal", "student login",
      "online exam registration", "exam registration"], "student_portal"),

    (["ragging", "anti ragging", "ragging complaint",
      "ragging helpline"], "anti_ragging"),

    (["discipline policy", "code of conduct", "disciplinary action",
      "student conduct", "college rules", "rules and regulations"], "discipline"),

    (["contact ekc", "college phone", "college email",
      "college address", "admission office contact",
      "how to contact"], "contact"),

    (["courses offered", "btech courses", "engineering branches",
      "departments in ekc", "cse in ekc", "what courses",
      "branches in ekc"], "courses_offered"),

    (["seat structure", "approved seats", "nri seats",
      "government quota seats", "management quota seats",
      "seat matrix", "intake capacity"], "seat_structure"),

    (["eligibility criteria", "btech eligibility", "lateral entry",
      "minimum marks for admission", "pcm marks",
      "who can apply"], "eligibility"),

    (["admission process", "how to apply", "keam admission",
      "steps for admission", "how to join ekc",
      "documents required for admission",
      "how to get admission"], "admission_process"),

    (["what is ktu", "about ktu", "ktu university", "ktu full form",
      "ktu affiliation", "apj abdul kalam technological",
      "ktu established"], "ktu_about"),

    (["about ekc", "what is ekc", "ekc college", "eranad knowledge",
      "tell me about ekc", "ekc overview",
      "ekc technical campus"], "about_ekc"),

    (["placement training", "placement preparation", "soft skill training", "aptitude training",
      "mock interview", "resume training",
      "personality development"], "training_programs"),

    (["campus life", "student life", "cultural events",
      "technical fest", "student clubs",
      "college events"], "campus_life"),

    (["grading system", "cgpa", "sgpa", "credit system",
      "year back", "promotion rules", "ktu regulations",
      "passing marks", "ktu academic rules"], "ktu_academics"),
]
