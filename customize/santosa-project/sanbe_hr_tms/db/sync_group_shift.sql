CREATE OR REPLACE FUNCTION fn_sync_group_shift()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
v_group_shift TEXT;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.shift_id = OLD.shift_id THEN
        RETURN NEW;
END IF;

SELECT sgs.name
INTO v_group_shift
FROM sb_group_shift sgs
WHERE sgs.id = NEW.shift_id;

UPDATE sb_employee_shift ses
SET group_shift = v_group_shift
    FROM hr_opening_closing hoc
WHERE ses.employee_id = NEW.employee_id
  AND ses.periode_id = hoc.id
  AND (lower(hoc.state_process) = 'running' or lower(hoc.state_process) = 'open') ;

RETURN NEW;
END;
$$;



CREATE TRIGGER trg_sync_group_shift
    AFTER INSERT OR UPDATE OF shift_id
                    ON sb_mapping_employee_shift
                        FOR EACH ROW
                        EXECUTE FUNCTION fn_sync_group_shift();