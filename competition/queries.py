RESULTS_QUERY = '''
SELECT
    participant_team.id AS id,
    participant_team.name AS team_name,
    participant_school.name AS school_name,
    participant_school.address AS school_address,
    participant_school.city AS school_city,
    members.names AS team_members,
    members.compensation AS compensation,
    SUM(competition_problem.points) + compensation AS points,
    hardest.position AS hardest_position,
    hardest.time AS hardest_time
FROM participant_team
JOIN participant_school ON participant_team.school_id = participant_school.id
LEFT OUTER JOIN competition_solution ON participant_team.id = competition_solution.team_id
LEFT OUTER JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
LEFT OUTER JOIN (
    SELECT
        GROUP_CONCAT(members.full_name, ", ") AS names,
        SUM(members.compensation) AS compensation,
        members.team_id
    FROM (
        SELECT
            participant_participant.first_name || " " || participant_participant.last_name AS full_name,
            IFNULL(competition_compensation.points, 0) AS compensation,
            participant_participant.team_id
        FROM participant_participant
        LEFT OUTER JOIN	competition_compensation ON participant_participant.school_class = competition_compensation.school_class
        ORDER BY
            last_name ASC,
            first_name ASC
    ) AS members
    GROUP BY members.team_id
) AS members ON participant_team.id = members.team_id
LEFT OUTER JOIN (
    SELECT
        competition_solution.time AS time,
        competition_problem.position AS position,
        competition_solution.team_id
    FROM competition_solution
    JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
    GROUP BY competition_solution.team_id
    HAVING competition_problem.position = MAX(competition_problem.position)
) AS hardest ON participant_team.id = hardest.team_id
WHERE participant_team.event_id = %s
GROUP BY participant_team.id
ORDER BY
    points DESC,
    hardest.position DESC,
    hardest.time ASC
'''
