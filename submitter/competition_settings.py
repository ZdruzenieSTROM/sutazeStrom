# Lomihlav

LOMIHLAV_CSV_FIELDS = [
    'team', 'school', 'members',
    'participant0_first_name', 'participant0_last_name', 'participant0_school_class',
    'participant1_first_name', 'participant1_last_name', 'participant1_school_class',
    'participant2_first_name', 'participant2_last_name', 'participant2_school_class',
    'participant3_first_name', 'participant3_last_name', 'participant3_school_class',
]

LOMIHLAV_SCHOOL_CLASS_MAPPER = {
    'siedmy': 7,
    'sekunda': 7,
    'ôsmy': 8,
    'tercia': 8,
    'deviaty': 9,
    'kvarta': 9,
}

LOMIHLAV_PROBLEM_CATEGORIES = [
    {'name': 'Úlohy', 'points': 1, 'count': 40, 'mcomp': True, 'is_problem': True},
    {'name': 'Hádanky', 'points': 2, 'count': 4,
        'mcomp': False, 'is_problem': False},
    {'name': 'Hlavolamy', 'points': 2, 'count': 4,
        'mcomp': False, 'is_problem': False},
]

LOMIHLAV_COMPENSATIONS = [
    {'class': 7, 'points': 0.95},
    {'class': 8, 'points': 0.85},
    {'class': 9, 'points': 0.75},
]

LOMIHLAV_TEAM_MEMBERS = 4

# Mamut

MAMUT_CSV_FIELDS = [
    'team', 'school', 'members',
    'participant0_first_name', 'participant0_last_name', 'participant0_school_class',
    'participant1_first_name', 'participant1_last_name', 'participant1_school_class',
    'participant2_first_name', 'participant2_last_name', 'participant2_school_class',
    'participant3_first_name', 'participant3_last_name', 'participant3_school_class',
    'participant4_first_name', 'participant4_last_name', 'participant4_school_class',
]

MAMUT_SCHOOL_CLASS_MAPPER = {
    '4. ročník ZŠ': 4,
    '5. ročník ZŠ': 5,
    '6. ročník ZŠ/Prima': 6,
}

MAMUT_PROBLEM_CATEGORIES = [
    {'name': 'Ľahké', 'points': 1, 'count': 30,
        'mcomp': False, 'is_problem': True},
    {'name': 'Stredné', 'points': 3, 'count': 25,
        'mcomp': False, 'is_problem': True},
    {'name': 'Ťažké', 'points': 5, 'count': 10,
        'mcomp': False, 'is_problem': True},
]

MAMUT_COMPENSATIONS = [
    {'class': 4, 'points': 5},
    {'class': 5, 'points': 3},
    {'class': 6, 'points': 1},
]

MAMUT_TEAM_MEMBERS = 5
