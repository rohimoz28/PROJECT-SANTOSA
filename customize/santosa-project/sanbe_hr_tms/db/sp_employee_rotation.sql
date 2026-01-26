CREATE OR REPLACE FUNCTION public.sp_employee_rotation(
    IN p_mutasi_id integer,
    IN p_digantikan_id integer, 
    IN p_pengganti_id integer 
)
RETURNS boolean
LANGUAGE plpgsql
AS $function$
DECLARE
    v_updated_count INT := 0;
    v_rowcount INT := 0;
BEGIN
    /*
     * =====================================================
     * KASUS 1 : TIDAK ADA PENGGANTI
     * parent : digantikan → mutasi
     * =====================================================
     */
    IF p_pengganti_id IS NULL THEN

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
            area,
            bisnis_unit,
            department_id,
            division_id,
            parent_id,
            nik,
            job_title,
            job_status,
            emp_status,
            employee_group1s,
            trx_number
        )
        SELECT
            hem.service_type,
            hem.service_date,
            hem.service_end,
            he.area,
            he.branch_id,
            he.department_id,
            he.division_id,
            p_mutasi_id,
            he.nik,
            hj.name ->>'en_US',
            he.job_status,
            he.emp_status_id,
            he.employee_group1s,
            hem.name
        FROM updated_emp ue
        JOIN hr_employee he ON he.id = p_mutasi_id
        Join hr_job hj on hj.id=he.id
        JOIN LATERAL (
            SELECT *
            FROM hr_employee_mutations
            WHERE employee_id = p_mutasi_id
            ORDER BY id DESC
            LIMIT 1
        ) hem ON TRUE;

        GET DIAGNOSTICS v_updated_count = ROW_COUNT;
        RETURN v_updated_count > 0;

    /*
     * =====================================================
     * KASUS 2 : ADA PENGGANTI
     * 1) parent mutasi → pengganti
     * 2) parent digantikan → mutasi
     * =====================================================
     */
    ELSE

        /*
         * STEP 0
         * Ambil dulu data employee
         * yang parent_id = p_mutasi_id
         */
        WITH emp_step1_src AS (
            SELECT
                id,
                nik,
                job_id,
                job_status,
                emp_status_id,
                employee_group1s
            FROM hr_employee
            WHERE parent_id = p_mutasi_id
        ),
        /*
         * STEP 1
         * mutasi → pengganti
         */
        updated_step1 AS (
            UPDATE hr_employee he
            SET parent_id = p_pengganti_id
            FROM emp_step1_src src
            WHERE he.id = src.id
            RETURNING src.*
        )
        INSERT INTO hr_employment_log (
            service_type,
            start_date,
            end_date,
            area,
            bisnis_unit,
            department_id,
            division_id,
            parent_id,
            nik,
            job_title,
            job_status,
            emp_status,
            employee_group1s,
            trx_number
        )
        SELECT
            hem.service_type,
            hem.service_date,
            hem.service_end,
            he.area,
            he.branch_id,
            he.department_id,
            he.division_id,
            p_pengganti_id,
            ue.nik,
            hj.name ->>'en_US',
            ue.job_status,
            ue.emp_status_id,
            ue.employee_group1s,
            hem.name
        FROM updated_step1 ue
        JOIN hr_employee he ON he.id = p_pengganti_id
        join hr_job hj on hj.id=he.job_id
        JOIN LATERAL (
            SELECT *
            FROM hr_employee_mutations
            WHERE employee_id = p_pengganti_id
            ORDER BY id DESC
            LIMIT 1
        ) hem ON TRUE;

        GET DIAGNOSTICS v_rowcount = ROW_COUNT;
        v_updated_count := v_updated_count + v_rowcount;

        /*
         * STEP 2
         * digantikan → mutasi
         */
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
            area,
            bisnis_unit,
            department_id,
            division_id,
            parent_id,
            nik,
            job_title,
            job_status,
            emp_status,
            employee_group1s,
            trx_number
        )
        SELECT
            hem.service_type,
            hem.service_date,
            hem.service_end,
            he.area,
            he.branch_id,
            he.department_id,
            he.division_id,
            p_mutasi_id,
            he.nik,
            hj.name ->>'en_US',
            he.job_status,
            he.emp_status_id,
            he.employee_group1s,
            hem.name
        FROM updated_step2 u2
        JOIN hr_employee he ON he.id = p_mutasi_id
        join hr_job hj on hj.id=he.job_id
        JOIN LATERAL (
            SELECT *
            FROM hr_employee_mutations
            WHERE employee_id = p_mutasi_id
            ORDER BY id DESC
            LIMIT 1
        ) hem ON TRUE;

        GET DIAGNOSTICS v_rowcount = ROW_COUNT;
        v_updated_count := v_updated_count + v_rowcount;

        RETURN v_updated_count > 0;
    END IF;

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Update gagal: %', SQLERRM;
    RETURN FALSE;
END;
$function$;