CREATE OR REPLACE PROCEDURE procedure_leave_alloc()
LANGUAGE plpgsql AS $$
BEGIN
--     delete
--     from sb_leave_allocation sla;

--     WITH aa AS (
--         SELECT
--             name,
--             id AS employee_id,
--             he.join_date,
--             he.job_status,
--             area,
--             he.branch_id,
--             he.department_id,
--             he.job_id
--         FROM hr_employee he
--         WHERE he.emp_status = 'confirmed'
--           AND he.state = 'approved'
--         /*AND he.job_status = 'contract' AND he.join_date IS NOT NULL*/
--     ),
--          bb AS (
--              SELECT
-- --              aa.name,
-- aa.area,
-- aa.branch_id,
-- aa.department_id,
-- aa.job_id,
-- aa.employee_id,
-- --              aa.join_date,
-- --              aa.job_status,
-- calculate_leave_alloc(aa.join_date, CURRENT_DATE, aa.job_status) AS leave_allocation,
-- COALESCE(SUM(hpe.time_days) FILTER (WHERE hpe.is_approved = true), 0) AS leave_used
--              FROM aa
--                       LEFT JOIN hr_permission_entry hpe ON aa.employee_id = hpe.employee_id /*where hpe.is_approved is true*/
--              GROUP BY aa.name, aa.employee_id,aa.area,aa.branch_id,aa.department_id,aa.job_id, aa.join_date, aa.job_status
--          ),
--          cc as (SELECT bb.*,bb.leave_allocation - bb.leave_used as remaining_leave, NOW() AS create_date FROM bb)
-- -- select * from cc;
--     insert
--     into sb_leave_allocation as sla (area_id,branch_id,department_id,job_id,employee_id,leave_allocation, leave_used, leave_remaining, create_date)
--     select * from cc;

    INSERT INTO sb_leave_allocation (
		area_id,
		branch_id,
		department_id,
		job_id,
		employee_id,
		leave_allocation,
		leave_remaining,
		leave_used,
		remarks,
		date,
		description
	)
	with aa as(
		SELECT
		    "name",
		    he.area,
		    he.branch_id,
		    he.department_id,
		    he.job_id,
		    he.id as employee_id,
		    CASE 
		        WHEN leave_calculation = 'first_month' THEN 1  -- Mengambil tanggal 1
		        WHEN leave_calculation = 'contract_based' AND job_status = 'contract' THEN EXTRACT(DAY FROM contract_datefrom)::INT  -- Mengambil tanggal (day) dari tanggal muali kontrak
				WHEN leave_calculation = 'contract_based' AND job_status = 'permanent' THEN EXTRACT(DAY FROM join_date)::INT  -- Mengambil tanggal (day) dari join_date
		        ELSE NULL
		    END AS leave_allocation_date,
		    he.leave_calculation
		FROM hr_employee he
		WHERE leave_calculation IS NOT NULL 
		AND he.emp_status = 'confirmed'
	    AND he.state = 'approved'
	),
	last_record AS (
	    SELECT
		    id,
		    employee_id,
		    leave_remaining
		FROM sb_leave_allocation
		where /*employee_id = 478968 and*/ id IN (
		    SELECT MAX(id)
		    FROM sb_leave_allocation
		    GROUP BY employee_id
		)    -- Mengambil record dengan ID tertinggi (terbaru)
	)
	select
	aa.area,
	aa.branch_id,
	aa.department_id,
	aa.job_id,
	aa.employee_id,
	--lr.employee_id,
	1 as leave_allocation,
	case 
		when COALESCE(lr.leave_remaining, 0) < 16 then (COALESCE(lr.leave_remaining, 0) + 1)
		else 16
	end as leave_remaining,
	--(COALESCE(lr.leave_remaining, 0) + 1) as leave_remaining2
	0 as leave_used,
	'TAMBAH KUOTA CUTI' as remarks,
	current_date as date,
	'TAMBAH KUOTA CUTI 1' as description
	from aa
	left join last_record lr on aa.employee_id = lr.employee_id
	where aa.leave_allocation_date = EXTRACT(DAY FROM current_date)::INT;
    
END;
$$;
