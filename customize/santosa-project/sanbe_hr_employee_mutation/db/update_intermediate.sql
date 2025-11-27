-- DROP PROCEDURE public.updateintermediate(int4, int4);

CREATE OR REPLACE PROCEDURE public.updateintermediate(p_employee_id integer, p_employee_id_baru integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    v_updated_coach INT := 0;
    v_updated_parent INT := 0;
BEGIN
    -- Pastikan ID berbeda
    IF p_employee_id <> p_employee_id_baru THEN

        -- Update coach_id
        UPDATE hr_employee he
        SET coach_id = p_employee_id_baru
        WHERE he.coach_id = p_employee_id;
        GET DIAGNOSTICS v_updated_coach = ROW_COUNT;

        -- Update parent_id
        UPDATE hr_employee he
        SET parent_id = p_employee_id_baru
        WHERE he.parent_id = p_employee_id;
        GET DIAGNOSTICS v_updated_parent = ROW_COUNT;

        -- Log untuk coach_id saja
        IF v_updated_coach > 0 AND v_updated_parent = 0 THEN
            INSERT INTO public.hr_employment_log (
                employee_id, bisnis_unit, department_id, create_uid, write_uid,
                service_type, job_title, job_status, emp_status, start_date, end_date,
                create_date, write_date, model_id, model_name, trx_number, doc_number,
                label, end_contract, contract_id --rehire, 
				--area, 
				--directorate_id,
                --hrms_department_id, division_id, 
				  --nik,
 --employee_group1s
            )
            SELECT 
                 he.id AS employee_id,
                he.branch_id AS bisnis_unit,
                NULL::INT AS department_id,
                2 AS create_uid,
                2 AS write_uid,
                'NEWS' AS service_type,
                he.job_title,
                he.job_status,
                he.emp_status,
                NULL::DATE AS start_date,
                NULL::DATE AS end_date,
                NOW() AS create_date,
                NOW() AS write_date,
                NULL::INT AS model_id,
                NULL::VARCHAR AS model_name,
                NULL::VARCHAR AS trx_number,
                NULL::VARCHAR AS doc_number,
                'Open View' AS label,
                FALSE AS end_contract,
                NULL::INT AS contract_id
                --FALSE AS rehire,
                --he.area,
                --he.directorate_id,
                --he.hrms_department_id,
                --he.division_id,
                --he.emp_status,
              ---he.parent_id,
                --he.nik
                --he.employee_group1s
            FROM hr_employee he
            WHERE he.coach_id = p_employee_id_baru;

        -- Log untuk parent_id saja
       ELSIF v_updated_parent > 0 AND v_updated_coach = 0 THEN
    INSERT INTO public.hr_employment_log (
        employee_id, bisnis_unit, department_id, create_uid, write_uid,
        service_type, job_title, job_status, emp_status, start_date, end_date,
        create_date, write_date, model_id, model_name, trx_number, doc_number,
        label, end_contract, contract_id
         --nik, 
--employee_group1s
    )
    SELECT 
        he.id AS employee_id,
        he.branch_id AS bisnis_unit,
        NULL::INT AS department_id,
        2 AS create_uid,
        2 AS write_uid,
        'NEWS' AS service_type,
        he.job_title,
        he.job_status,
        he.emp_status,
        NULL::DATE AS start_date,
        NULL::DATE AS end_date,
        NOW() AS create_date,
        NOW() AS write_date,
        NULL::INT AS model_id,
        NULL::VARCHAR AS model_name,
        NULL::VARCHAR AS trx_number,
        NULL::VARCHAR AS doc_number,
        'Open View' AS label,
        FALSE AS end_contract,
        NULL::INT AS contract_id
        --he.emp_status,
        --he.nik,
       -- he.employee_group1s
    FROM hr_employee he
    WHERE he.parent_id = p_employee_id_baru;

        -- Log untuk coach_id dan parent_id sekaligus
        ELSIF v_updated_coach > 0 AND v_updated_parent > 0 THEN
            INSERT INTO public.hr_employment_log (
               employee_id, bisnis_unit, department_id, create_uid, write_uid,
                service_type, job_title, job_status, emp_status, start_date, end_date,
                create_date, write_date, model_id, model_name, trx_number, doc_number,
                label, end_contract, contract_id --rehire, 
				--area, 
				--directorate_id,
                --hrms_department_id, division_id,  
					 --nik, 
--employee_group1s
            )
 SELECT 
                he.id AS employee_id,
                he.branch_id AS bisnis_unit,
                NULL::INT AS department_id,
                2 AS create_uid,
                2 AS write_uid,
                'NEWS' AS service_type,
                he.job_title,
                he.job_status,
                he.emp_status,
                NULL::DATE AS start_date,
                NULL::DATE AS end_date,
                NOW() AS create_date,
                NOW() AS write_date,
                NULL::INT AS model_id,
                NULL::VARCHAR AS model_name,
                NULL::VARCHAR AS trx_number,
                NULL::VARCHAR AS doc_number,
                'Open View' AS label,
                FALSE AS end_contract,
                NULL::INT AS contract_id
                --FALSE AS rehire,
                --he.area,
                --he.directorate_id,
                --he.hrms_department_id,
                --he.division_id,
                ---he.emp_status,
                --he.parent_id,
                --he.nik
                --he.employee_group1s
            FROM hr_employee he
            WHERE he.coach_id = p_employee_id_baru OR he.parent_id = p_employee_id_baru;
        END IF;

        -- Debug notice
        RAISE NOTICE 'Update selesai: coach=% rows, parent=% rows', v_updated_coach, v_updated_parent;

    END IF;

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Update gagal: %', SQLERRM;

END;
$procedure$
;
