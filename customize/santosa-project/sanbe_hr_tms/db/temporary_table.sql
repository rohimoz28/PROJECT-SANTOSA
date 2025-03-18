CREATE TABLE IF NOT EXISTS temp_sb_tms_tmsentry_details AS
SELECT *
FROM sb_tms_tmsentry_details;

CREATE TABLE IF NOT EXISTS temp_hr_tmsentry_summary AS
SELECT *
FROM hr_tmsentry_summary hts;

-- Adding columns with IF NOT EXISTS to temp_sb_tms_tmsentry_details
ALTER TABLE temp_sb_tms_tmsentry_details
    ADD COLUMN IF NOT EXISTS delay_allow INT,
    ADD COLUMN IF NOT EXISTS delay_level1 INT,
    ADD COLUMN IF NOT EXISTS delay_level2 INT;

-- Adding column with IF NOT EXISTS to temp_hr_tmsentry_summary
ALTER TABLE temp_hr_tmsentry_summary
    ADD COLUMN IF NOT EXISTS total_deduction FLOAT;

-- Dropping columns with IF NOT EXISTS from temp_hr_tmsentry_summary
ALTER TABLE temp_hr_tmsentry_summary
DROP COLUMN IF EXISTS hrd_approved,
    DROP COLUMN IF EXISTS checker_approved;

-- Adding multiple columns with IF NOT EXISTS to temp_hr_tmsentry_summary
ALTER TABLE temp_hr_tmsentry_summary
    ADD COLUMN IF NOT EXISTS completed_hrd INT,
    ADD COLUMN IF NOT EXISTS completed_ca INT,
    ADD COLUMN IF NOT EXISTS task_hrd INT,
    ADD COLUMN IF NOT EXISTS total_deduction FLOAT,
    ADD COLUMN IF NOT EXISTS task_ca INT;
