SELECT
    regexp_replace(jel.stepname, '\..*$', '', 'g') AS company,
    regexp_replace(split_part(jel.stepname, '.', 2), '\s*\(.*\)$', '', 'g') AS branch,
    to_char(log_date, 'YYYY-MM-DD') AS tanggal,
    to_char(log_date, 'HH24:MI:SS') AS waktu,
    CASE
        WHEN jel."RESULT" = 'true' THEN 'Succesed'
        ELSE 'Failed'
        END AS state,
    CASE
        WHEN now()::date - log_date::date = 1 THEN '1 last day'
        WHEN now()::date - log_date::date < 7
            THEN concat((now()::date - log_date::date), ' days ago')
        WHEN now()::date - log_date::date >= 7
            AND now()::date - log_date::date < 30
            THEN concat(floor((now()::date - log_date::date)/7), ' weeks ago')
        WHEN now()::date - log_date::date >= 30
            AND now()::date - log_date::date < 365
            THEN concat(floor((now()::date - log_date::date)/30), ' months ago')
        WHEN now()::date - log_date::date >= 365
            THEN concat(floor((now()::date - log_date::date)/365), ' years ago')
        WHEN EXTRACT(EPOCH FROM (now() - log_date)) >= 3600
            THEN concat(round(EXTRACT(EPOCH FROM (now() - log_date)) / 3600), ' hours ago')
        WHEN EXTRACT(EPOCH FROM (now() - log_date)) >= 60
            THEN concat(round(EXTRACT(EPOCH FROM (now() - log_date)) / 60), ' minutes ago')
        ELSE concat(round(EXTRACT(EPOCH FROM (now() - log_date))), ' seconds ago')
        END AS age
FROM job_entry_log jel
WHERE regexp_replace(jel.stepname, '\..*$', '', 'g') = 'BSP' and jel."RESULT"='false';