-- DROP FUNCTION public.sp_employee_rotation(int4, int4, int4);

CREATE OR REPLACE FUNCTION public.sp_employee_rotation(p_mutasi_id integer, p_digantikan_id integer, p_pengganti_id integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_updated_count INT := 0;
    v_log RECORD;
BEGIN
    /*
     * =====================================================
     * KASUS 1 : TIDAK ADA PENGGANTI
     * =====================================================
     */
    IF p_pengganti_id IS NULL THEN

        FOR v_log IN
            WITH updated_emp AS (
                UPDATE hr_employee
                SET parent_id = p_mutasi_id
                WHERE parent_id = p_digantikan_id
                RETURNING id
            )
            INSERT INTO hr_employment_log (
                service_type,
                start_date,
                end_date,
                model_name,
                area,
                bisnis_unit,
                directorate_id,
                hrms_department_id,
                division_id,
                parent_id,
                nik,
                job_title,
                job_status,
                emp_status,
                employee_group1s,
                trx_number,
                employee_id,
				create_uid,
				create_date,
				write_uid,
				write_date,
				model_id
            )
            SELECT
                upper(hem.service_type),
                hem.service_date,
                hem.service_end,
                'hr.employee.mutations',
                he.area,
                he.branch_id,
                he.directorate_id,
                he.hrms_department_id,
                he.division_id,
                p_mutasi_id,
                he.nik,
                hj.name->>'en_US',
                he.job_status,
                'confirmed',
                eg.name,
                hem.name,
                he.id,
				2,
				now(),
				2,
				now(),
				hem.id
            FROM updated_emp ue
            JOIN hr_employee he ON he.id = ue.id
            JOIN hr_job hj ON hj.id = he.job_id
            JOIN emp_group eg ON he.employee_group1s = eg.id
            cross JOIN (
                SELECT *
                FROM hr_employee_mutations
                WHERE employee_id = p_mutasi_id
                ORDER BY id DESC
                LIMIT 1
            ) hem 
            RETURNING employee_id, nik, parent_id, trx_number
        LOOP
            v_updated_count := v_updated_count + 1;

            RAISE NOTICE
                'INSERT LOG [KASUS 1] → employee_id=%, nik=%, parent_id=%, trx=%',
                v_log.employee_id,
                v_log.nik,
                v_log.parent_id,
                v_log.trx_number;
        END LOOP;

        RAISE NOTICE 'TOTAL INSERT KASUS 1: % row', v_updated_count;
        RETURN v_updated_count > 0;

    /*
     * =====================================================
     * KASUS 2 : ADA PENGGANTI
     * =====================================================
     */
    ELSE
        /*
         * STEP 1 : mutasi → pengganti
         */
        FOR v_log IN
            WITH updated_step1 AS (
                UPDATE hr_employee
                SET parent_id = p_pengganti_id
                WHERE parent_id = p_mutasi_id
                RETURNING id
            )
            INSERT INTO hr_employment_log (
                service_type,
                start_date,
                end_date,
                model_name,
                area,
                bisnis_unit,
                directorate_id,
                hrms_department_id,
                division_id,
                parent_id,
                nik,
                job_title,
                job_status,
                emp_status,
                employee_group1s,
                trx_number,
                employee_id,
				create_uid,
				create_date,
				write_uid,
				write_date,
				model_id
            )
            SELECT
                upper(hem.service_type),
                hem.service_date,
                hem.service_end,
                'hr.employee.mutations',
                he.area,
                he.branch_id,
                he.directorate_id,
                he.hrms_department_id,
                he.division_id,
                p_pengganti_id,
                he.nik,
                hj.name->>'en_US',
                he.job_status,
                'confirmed',
                eg.name,
                hem.name,
                he.id,
				2,
				now(),
				2,
				now(),
				hem.id
            FROM updated_step1 ue
            JOIN hr_employee he ON he.id = ue.id
            JOIN hr_job hj ON hj.id = he.job_id
            JOIN emp_group eg ON he.employee_group1s = eg.id
            cross JOIN (
                SELECT *
                FROM hr_employee_mutations
                WHERE employee_id = p_mutasi_id
                ORDER BY id DESC
                LIMIT 1
            ) hem 
            RETURNING employee_id, nik, parent_id, trx_number
        LOOP
            v_updated_count := v_updated_count + 1;

            RAISE NOTICE
                'INSERT LOG [STEP 1] → employee_id=%, nik=%, parent_id=%, trx=%',
                v_log.employee_id,
                v_log.nik,
                v_log.parent_id,
                v_log.trx_number;
        END LOOP;

        /*
         * STEP 2 : digantikan → mutasi
         */
        FOR v_log IN
            WITH updated_step2 AS (
                UPDATE hr_employee
                SET parent_id = p_mutasi_id
                WHERE parent_id = p_digantikan_id
                RETURNING id
            )
            INSERT INTO hr_employment_log (
                service_type,
                start_date,
                end_date,
                model_name,
                area,
                bisnis_unit,
                directorate_id,
                hrms_department_id,
                division_id,
                parent_id,
                nik,
                job_title,
                job_status,
                emp_status,
                employee_group1s,
                trx_number,
                employee_id,
				create_uid,
				create_date,
				write_uid,
				write_date,
				model_id
            )
            SELECT
                upper(hem.service_type),
                hem.service_date,
                hem.service_end,
                'hr.employee.mutations',
                he.area,
                he.branch_id,
                he.directorate_id,
                he.hrms_department_id,
                he.division_id,
                p_mutasi_id,
                he.nik,
                hj.name->>'en_US',
                he.job_status,
                'confirmed',
                eg.name,
                hem.name,
                he.id,
				2,
				now(),
				2,
				now(),
				hem.id
            FROM updated_step2 ue
            JOIN hr_employee he ON he.id = ue.id
            JOIN hr_job hj ON hj.id = he.job_id
            JOIN emp_group eg ON he.employee_group1s = eg.id
            cross JOIN (
                SELECT *
                FROM hr_employee_mutations
                WHERE employee_id = p_mutasi_id
                ORDER BY id DESC
                LIMIT 1
            ) hem 
            RETURNING employee_id, nik, parent_id, trx_number
        LOOP
            v_updated_count := v_updated_count + 1;

            RAISE NOTICE
                'INSERT LOG [STEP 2] → employee_id=%, nik=%, parent_id=%, trx=%',
                v_log.employee_id,
                v_log.nik,
                v_log.parent_id,
                v_log.trx_number;
        END LOOP;

        RAISE NOTICE 'TOTAL INSERT KASUS 2: % row', v_updated_count;
        RETURN v_updated_count > 0;
    END IF;

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'ERROR sp_employee_rotation: %', SQLERRM;
    RETURN FALSE;
END;
$function$
;
-- DROP FUNCTION public.sp_employee_rotation(int4, int4, int4);

CREATE OR REPLACE FUNCTION public.sp_employee_rotation(p_mutasi_id integer, p_digantikan_id integer, p_pengganti_id integer)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_updated_count INT := 0;
    v_log RECORD;
BEGIN
    /*
     * =====================================================
     * KASUS 1 : TIDAK ADA PENGGANTI
     * =====================================================
     */
    IF p_pengganti_id IS NULL THEN

        FOR v_log IN
            WITH updated_emp AS (
                UPDATE hr_employee
                SET parent_id = p_mutasi_id
                WHERE parent_id = p_digantikan_id
                RETURNING id
            )
            INSERT INTO hr_employment_log (
                service_type,
                start_date,
                end_date,
                model_name,
                area,
                bisnis_unit,
                directorate_id,
                hrms_department_id,
                division_id,
                parent_id,
                nik,
                job_title,
                job_status,
                emp_status,
                employee_group1s,
                trx_number,
                employee_id,
				create_uid,
				create_date,
				write_uid,
				write_date,
				model_id
            )
            SELECT
                upper(hem.service_type),
                hem.service_date,
                hem.service_end,
                'hr.employee.mutations',
                he.area,
                he.branch_id,
                he.directorate_id,
                he.hrms_department_id,
                he.division_id,
                p_mutasi_id,
                he.nik,
                hj.name->>'en_US',
                he.job_status,
                'confirmed',
                eg.name,
                hem.name,
                he.id,
				2,
				now(),
				2,
				now(),
				hem.id
            FROM updated_emp ue
            JOIN hr_employee he ON he.id = ue.id
            JOIN hr_job hj ON hj.id = he.job_id
            JOIN emp_group eg ON he.employee_group1s = eg.id
            cross JOIN (
                SELECT *
                FROM hr_employee_mutations
                WHERE employee_id = p_mutasi_id
                ORDER BY id DESC
                LIMIT 1
            ) hem 
            RETURNING employee_id, nik, parent_id, trx_number
        LOOP
            v_updated_count := v_updated_count + 1;

            RAISE NOTICE
                'INSERT LOG [KASUS 1] → employee_id=%, nik=%, parent_id=%, trx=%',
                v_log.employee_id,
                v_log.nik,
                v_log.parent_id,
                v_log.trx_number;
        END LOOP;

        RAISE NOTICE 'TOTAL INSERT KASUS 1: % row', v_updated_count;
        RETURN v_updated_count > 0;

    /*
     * =====================================================
     * KASUS 2 : ADA PENGGANTI
     * =====================================================
     */
    ELSE
        /*
         * STEP 1 : mutasi → pengganti
         */
        FOR v_log IN
            WITH updated_step1 AS (
                UPDATE hr_employee
                SET parent_id = p_pengganti_id
                WHERE parent_id = p_mutasi_id
                RETURNING id
            )
            INSERT INTO hr_employment_log (
                service_type,
                start_date,
                end_date,
                model_name,
                area,
                bisnis_unit,
                directorate_id,
                hrms_department_id,
                division_id,
                parent_id,
                nik,
                job_title,
                job_status,
                emp_status,
                employee_group1s,
                trx_number,
                employee_id,
				create_uid,
				create_date,
				write_uid,
				write_date,
				model_id
            )
            SELECT
                upper(hem.service_type),
                hem.service_date,
                hem.service_end,
                'hr.employee.mutations',
                he.area,
                he.branch_id,
                he.directorate_id,
                he.hrms_department_id,
                he.division_id,
                p_pengganti_id,
                he.nik,
                hj.name->>'en_US',
                he.job_status,
                'confirmed',
                eg.name,
                hem.name,
                he.id,
				2,
				now(),
				2,
				now(),
				hem.id
            FROM updated_step1 ue
            JOIN hr_employee he ON he.id = ue.id
            JOIN hr_job hj ON hj.id = he.job_id
            JOIN emp_group eg ON he.employee_group1s = eg.id
            cross JOIN (
                SELECT *
                FROM hr_employee_mutations
                WHERE employee_id = p_mutasi_id
                ORDER BY id DESC
                LIMIT 1
            ) hem 
            RETURNING employee_id, nik, parent_id, trx_number
        LOOP
            v_updated_count := v_updated_count + 1;

            RAISE NOTICE
                'INSERT LOG [STEP 1] → employee_id=%, nik=%, parent_id=%, trx=%',
                v_log.employee_id,
                v_log.nik,
                v_log.parent_id,
                v_log.trx_number;
        END LOOP;

        /*
         * STEP 2 : digantikan → mutasi
         */
        FOR v_log IN
            WITH updated_step2 AS (
                UPDATE hr_employee
                SET parent_id = p_mutasi_id
                WHERE parent_id = p_digantikan_id
                RETURNING id
            )
            INSERT INTO hr_employment_log (
                service_type,
                start_date,
                end_date,
                model_name,
                area,
                bisnis_unit,
                directorate_id,
                hrms_department_id,
                division_id,
                parent_id,
                nik,
                job_title,
                job_status,
                emp_status,
                employee_group1s,
                trx_number,
                employee_id,
				create_uid,
				create_date,
				write_uid,
				write_date,
				model_id
            )
            SELECT
                upper(hem.service_type),
                hem.service_date,
                hem.service_end,
                'hr.employee.mutations',
                he.area,
                he.branch_id,
                he.directorate_id,
                he.hrms_department_id,
                he.division_id,
                p_mutasi_id,
                he.nik,
                hj.name->>'en_US',
                he.job_status,
                'confirmed',
                eg.name,
                hem.name,
                he.id,
				2,
				now(),
				2,
				now(),
				hem.id
            FROM updated_step2 ue
            JOIN hr_employee he ON he.id = ue.id
            JOIN hr_job hj ON hj.id = he.job_id
            JOIN emp_group eg ON he.employee_group1s = eg.id
            cross JOIN (
                SELECT *
                FROM hr_employee_mutations
                WHERE employee_id = p_mutasi_id
                ORDER BY id DESC
                LIMIT 1
            ) hem 
            RETURNING employee_id, nik, parent_id, trx_number
        LOOP
            v_updated_count := v_updated_count + 1;

            RAISE NOTICE
                'INSERT LOG [STEP 2] → employee_id=%, nik=%, parent_id=%, trx=%',
                v_log.employee_id,
                v_log.nik,
                v_log.parent_id,
                v_log.trx_number;
        END LOOP;

        RAISE NOTICE 'TOTAL INSERT KASUS 2: % row', v_updated_count;
        RETURN v_updated_count > 0;
    END IF;

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'ERROR sp_employee_rotation: %', SQLERRM;
    RETURN FALSE;
END;
$function$
;
