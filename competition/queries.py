RESULTS_QUERY = '''
SELECT
    participant_team.id AS id,
    participant_team.name AS team_name,
    participant_school.name AS school_name,
    participant_school.address AS school_address,
    participant_school.city AS school_city,
    members.members AS team_members,
    SUM(competition_problem.points) AS points,
    hardest_position.position AS hardest_position,
    hardest_time.time AS hardest_time
FROM competition_solution
JOIN participant_team ON competition_solution.team_id = participant_team.id
JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
JOIN participant_school ON participant_team.school_id = participant_school.id
LEFT OUTER JOIN (
    SELECT
        GROUP_CONCAT(participants.full_name, ", ") AS members,
        participants.team_id
    FROM (
        SELECT
            participant_participant.first_name || " " || participant_participant.last_name AS full_name,
            participant_participant.team_id
        FROM
            participant_participant
    ) AS participants
    GROUP BY participants.team_id
) AS members ON competition_solution.team_id = members.team_id
JOIN (
    SELECT
        MAX(competition_problem.position) AS position,
        competition_solution.team_id
    FROM competition_solution
    JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
    GROUP BY competition_solution.team_id
) AS hardest_position ON competition_solution.team_id = hardest_position.team_id
JOIN  (
    SELECT
        competition_solution.time AS time,
        competition_solution.team_id
    FROM competition_solution
    JOIN competition_problem ON competition_solution.problem_id = competition_problem.id
    GROUP BY competition_solution.team_id
    HAVING competition_problem.position = MAX(competition_problem.position)
) AS hardest_time ON competition_solution.team_id = hardest_time.team_id
WHERE competition_solution.event_id = %s
GROUP BY competition_solution.team_id
ORDER BY
    points DESC,
    hardest_position DESC,
    hardest_time ASC
'''
