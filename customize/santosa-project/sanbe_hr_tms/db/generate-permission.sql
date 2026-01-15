-- DROP FUNCTION public.generate_cuti_permission(int4, int4);

CREATE OR REPLACE FUNCTION public.generate_cuti_permission(p_periode_id integer, p_branch_id integer)
    RETURNS boolean
    LANGUAGE plpgsql
AS
$function$
DECLARE
    v_changed BOOLEAN := FALSE;
    v_count   INTEGER;
BEGIN
    -------------------------------------------
    -- INSERT CUTI BARU
    -------------------------------------------
    WITH master AS (SELECT s.id,
                           s.periode_id,
                           s.employee_id,
                           s.branch_id,
                           s.hrms_department_id,
                           s.directorate_id,
                           s.job_id,
                           s.area_id,
                           v.day_str,
                           v.shift_code
                    FROM sb_employee_shift s
                             CROSS JOIN LATERAL (
                        VALUES ('21', s.date_21),
                               ('22', s.date_22),
                               ('23', s.date_23),
                               ('24', s.date_24),
                               ('25', s.date_25),
                               ('26', s.date_26),
                               ('27', s.date_27),
                               ('28', s.date_28),
                               ('29', s.date_29),
                               ('30', s.date_30),
                               ('31', s.date_31),
                               ('01', s.date_01),
                               ('02', s.date_02),
                               ('03', s.date_03),
                               ('04', s.date_04),
                               ('05', s.date_05),
                               ('06', s.date_06),
                               ('07', s.date_07),
                               ('08', s.date_08),
                               ('09', s.date_09),
                               ('10', s.date_10),
                               ('11', s.date_11),
                               ('12', s.date_12),
                               ('13', s.date_13),
                               ('14', s.date_14),
                               ('15', s.date_15),
                               ('16', s.date_16),
                               ('17', s.date_17),
                               ('18', s.date_18),
                               ('19', s.date_19),
                               ('20', s.date_20)
                        ) AS v(day_str, shift_code)
                    WHERE s.periode_id = p_periode_id
                      AND s.branch_id = p_branch_id),
         master_join AS (SELECT hwd.code AS hwd_code,
                                hoc.open_periode_from,
                                hoc.open_periode_to,
                                master.*,
                                CASE
                                    WHEN master.day_str::int >= 21 THEN
                                        (date_trunc('month', hoc.open_periode_from)::date + (master.day_str::int - 1))
                                    ELSE
                                        (date_trunc('month', hoc.open_periode_to)::date + (master.day_str::int - 1))
                                    END  AS tanggal_shift
                         FROM master
                                  JOIN hr_working_days hwd ON master.shift_code = hwd.id
                                  JOIN hr_opening_closing hoc ON master.periode_id = hoc.id),
         data_permission AS (SELECT mj.*,
                                    hpe.id               AS id_hpe,
                                    hpe.permission_status,
                                    hlt.name ->> 'en_US' AS holiday_name,
                                    slb.name             as cuti_name
                             FROM master_join mj
                                      LEFT JOIN hr_permission_entry hpe
                                                ON hpe.branch_id = mj.branch_id
                                                    AND hpe.employee_id = mj.employee_id
                                                    AND hpe.permission_date_from = mj.tanggal_shift
                                                    and
                                                   hpe.permission_date_from between mj.open_periode_from and mj.open_periode_to
                                      LEFT JOIN hr_leave_type hlt
                                                ON hpe.holiday_status_id = hlt.id
                                      left join sb_leave_benefit slb on hpe.permission_type_id = slb.id and
                                                                        (hpe.permission_status ilike '%draft%' or
                                                                         hpe.permission_status ilike '%approved%'))
    INSERT
    INTO hr_permission_entry (employee_id, branch_id, hrms_department_id, directorate_id, job_id, time_days,
                              permission_type_id, holiday_status_id, area_id,
                              permission_date_from, "permission_date_To",
                              permission_status, create_uid, write_uid, create_date, write_date)
    SELECT data_permission.employee_id,
           data_permission.branch_id,
           data_permission.hrms_department_id,
           data_permission.directorate_id,
           data_permission.job_id,
           1,
           slb.id,
           19,
           data_permission.area_id,
           data_permission.tanggal_shift,
           data_permission.tanggal_shift,
           'draft',
           88,
           88,
           NOW(),
           NOW()
    FROM data_permission
             join sb_leave_allocation_request slar on slar.employee_id = data_permission.employee_id
             join sb_leave_benefit slb on slb.leave_req_id = slar.id and slb.code = 'A1'
    WHERE id_hpe IS NULL
      AND lower(hwd_code) = 'c';

    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN v_changed := TRUE; END IF;


    -------------------------------------------
    -- DELETE CUTI SALAH DRAFT
    -------------------------------------------
    WITH master AS (SELECT *
                    FROM sb_employee_shift s
                             CROSS JOIN LATERAL (
                        VALUES ('21', s.date_21),
                               ('22', s.date_22),
                               ('23', s.date_23),
                               ('24', s.date_24),
                               ('25', s.date_25),
                               ('26', s.date_26),
                               ('27', s.date_27),
                               ('28', s.date_28),
                               ('29', s.date_29),
                               ('30', s.date_30),
                               ('31', s.date_31),
                               ('01', s.date_01),
                               ('02', s.date_02),
                               ('03', s.date_03),
                               ('04', s.date_04),
                               ('05', s.date_05),
                               ('06', s.date_06),
                               ('07', s.date_07),
                               ('08', s.date_08),
                               ('09', s.date_09),
                               ('10', s.date_10),
                               ('11', s.date_11),
                               ('12', s.date_12),
                               ('13', s.date_13),
                               ('14', s.date_14),
                               ('15', s.date_15),
                               ('16', s.date_16),
                               ('17', s.date_17),
                               ('18', s.date_18),
                               ('19', s.date_19),
                               ('20', s.date_20)
                        ) AS v(day_str, shift_code)
                    WHERE s.periode_id = p_periode_id
                      AND s.branch_id = p_branch_id),
         master_join AS (SELECT hwd.code AS hwd_code,
                                hoc.open_periode_from,
                                hoc.open_periode_to,
                                master.*,
                                CASE
                                    WHEN master.day_str::int >= 21 THEN
                                        (date_trunc('month', hoc.open_periode_from)::date + (master.day_str::int - 1))
                                    ELSE
                                        (date_trunc('month', hoc.open_periode_to)::date + (master.day_str::int - 1))
                                    END  AS tanggal_shift
                         FROM master
                                  JOIN hr_working_days hwd ON master.shift_code = hwd.id
                                  JOIN hr_opening_closing hoc ON master.periode_id = hoc.id),
         data_permission AS (SELECT mj.*,
                                    hpe.id               AS id_hpe,
                                    hpe.permission_status,
                                    hlt.name ->> 'en_US' AS holiday_name,
                                    slb.name             as cuti_name
                             FROM master_join mj
                                      LEFT JOIN hr_permission_entry hpe
                                                ON hpe.branch_id = mj.branch_id
                                                    AND hpe.employee_id = mj.employee_id
                                                    AND hpe.permission_date_from = mj.tanggal_shift
                                                    and
                                                   hpe.permission_date_from between mj.open_periode_from and mj.open_periode_to
                                      LEFT JOIN hr_leave_type hlt
                                                ON hpe.holiday_status_id = hlt.id
                                      left join sb_leave_benefit slb on hpe.permission_type_id = slb.id and
                                                                        (hpe.permission_status ilike '%draft%' or
                                                                         hpe.permission_status ilike '%approved%'))
    DELETE
    FROM hr_permission_entry hpe
        USING data_permission dp
    WHERE hpe.id = dp.id_hpe
      AND dp.permission_status = 'draft'
      AND lower(dp.hwd_code) <> 'c'
      AND (dp.cuti_name ILIKE '%cuti%' OR dp.cuti_name IS NULL);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN v_changed := TRUE; END IF;


    -------------------------------------------
    -- CANCEL CUTI APPROVED
    -------------------------------------------
    WITH master AS (SELECT *
                    FROM sb_employee_shift s
                             CROSS JOIN LATERAL (
                        VALUES ('21', s.date_21),
                               ('22', s.date_22),
                               ('23', s.date_23),
                               ('24', s.date_24),
                               ('25', s.date_25),
                               ('26', s.date_26),
                               ('27', s.date_27),
                               ('28', s.date_28),
                               ('29', s.date_29),
                               ('30', s.date_30),
                               ('31', s.date_31),
                               ('01', s.date_01),
                               ('02', s.date_02),
                               ('03', s.date_03),
                               ('04', s.date_04),
                               ('05', s.date_05),
                               ('06', s.date_06),
                               ('07', s.date_07),
                               ('08', s.date_08),
                               ('09', s.date_09),
                               ('10', s.date_10),
                               ('11', s.date_11),
                               ('12', s.date_12),
                               ('13', s.date_13),
                               ('14', s.date_14),
                               ('15', s.date_15),
                               ('16', s.date_16),
                               ('17', s.date_17),
                               ('18', s.date_18),
                               ('19', s.date_19),
                               ('20', s.date_20)
                        ) AS v(day_str, shift_code)
                    WHERE s.periode_id = p_periode_id
                      AND s.branch_id = p_branch_id),
         master_join AS (SELECT hwd.code AS hwd_code,
                                hoc.open_periode_from,
                                hoc.open_periode_to,
                                master.*,
                                CASE
                                    WHEN master.day_str::int >= 21 THEN
                                        (date_trunc('month', hoc.open_periode_from)::date + (master.day_str::int - 1))
                                    ELSE
                                        (date_trunc('month', hoc.open_periode_to)::date + (master.day_str::int - 1))
                                    END  AS tanggal_shift
                         FROM master
                                  JOIN hr_working_days hwd ON master.shift_code = hwd.id
                                  JOIN hr_opening_closing hoc ON master.periode_id = hoc.id),
         data_permission AS (SELECT mj.*,
                                    hpe.id               AS id_hpe,
                                    hpe.permission_status,
                                    hlt.name ->> 'en_US' AS holiday_name,
                                    slb.name             as cuti_name
                             FROM master_join mj
                                      LEFT JOIN hr_permission_entry hpe
                                                ON hpe.branch_id = mj.branch_id
                                                    AND hpe.employee_id = mj.employee_id
                                                    AND hpe.permission_date_from = mj.tanggal_shift
                                                    and
                                                   hpe.permission_date_from between mj.open_periode_from and mj.open_periode_to
                                      LEFT JOIN hr_leave_type hlt
                                                ON hpe.holiday_status_id = hlt.id
                                      left join sb_leave_benefit slb on hpe.permission_type_id = slb.id and
                                                                        (hpe.permission_status ilike '%draft%' or
                                                                         hpe.permission_status ilike '%approved%'))
    UPDATE hr_permission_entry hpe
    SET permission_status = 'cancel',
        write_uid         = 88,
        write_date        = NOW()
    FROM data_permission dp
    WHERE hpe.id = dp.id_hpe
      AND dp.permission_status = 'approved'
      AND lower(dp.hwd_code) <> 'c'
      AND dp.cuti_name ILIKE '%cuti%';

    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF v_count > 0 THEN v_changed := TRUE; END IF;

    RETURN v_changed;
END;
$function$
;

-- Permissions
--
-- ALTER FUNCTION public.generate_cuti_permission(int4, int4) OWNER TO odoo;
-- GRANT ALL ON FUNCTION public.generate_cuti_permission(int4, int4) TO public;
-- GRANT ALL ON FUNCTION public.generate_cuti_permission(int4, int4) TO odoo;
