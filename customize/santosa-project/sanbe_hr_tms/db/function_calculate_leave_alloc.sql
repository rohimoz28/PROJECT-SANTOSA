CREATE OR REPLACE FUNCTION calculate_leave_alloc(join_date DATE, curr_date DATE, job_status TEXT)
    RETURNS INTEGER AS $$
DECLARE
leave_alloc INTEGER := 0;
    current_month DATE := join_date;
    permanent_date DATE;
BEGIN
    -- Loop until curr_date is reached or leave_alloc reaches 16
    WHILE current_month <= curr_date LOOP
            IF job_status = 'permanent' THEN
                -- Set the permanent_date to the 20th of the current month
                permanent_date := DATE_TRUNC('month', current_month) + INTERVAL '19 days';

                -- Check if curr_date has passed the 20th of the month
                IF curr_date >= permanent_date THEN
                    leave_alloc := leave_alloc + 1;
END IF;
ELSE
                -- For contract job status, use the join date logic
                IF curr_date >= current_month THEN
                    leave_alloc := leave_alloc + 1;
END IF;
END IF;

            -- Break the loop if leave_alloc reaches 16
            IF leave_alloc = 16 THEN
                EXIT;
END IF;

            -- Move to the first day of the next month
            current_month := (current_month + INTERVAL '1 month')::DATE;
END LOOP;

RETURN leave_alloc;
END;
$$ LANGUAGE plpgsql;