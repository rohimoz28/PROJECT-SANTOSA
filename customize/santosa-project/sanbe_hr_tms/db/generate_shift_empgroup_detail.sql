CREATE OR REPLACE FUNCTION public.generate_empgroup(p_periode_id integer, p_empgroup_id integer)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_empgroup_exists BOOLEAN;
BEGIN
    -- Cek apakah empgroup_id valid (opsional: tambahkan AND state='draft' kalau ingin dipaksa)
    SELECT EXISTS(
        SELECT 1
        FROM hr_empgroup
        WHERE id = p_empgroup_id
          --AND state = 'draft'
    ) INTO v_empgroup_exists;

    IF NOT v_empgroup_exists THEN
        RAISE NOTICE 'Empgroup ID % tidak ditemukan atau tidak berstatus draft. Proses dibatalkan.', p_empgroup_id;
        RETURN;
    END IF;

    --  Mulai blok transaksi manual agar bisa rollback jika gagal
    BEGIN
        -- Hapus data lama
        DELETE FROM hr_empgroup_details;

        -- Insert data baru
        INSERT INTO public.hr_empgroup_details
            (empgroup_id, department_id, employee_id, job_id, create_uid, write_uid, nik, create_date, write_date, 
             branch_id, area_id, wdcode, valid_from, valid_to, empgroup_name, wdcode_name, state, division_id, 
             hrms_department_id, directorate_id, area, "name")
	  WITH base AS (
    		SELECT
        		ses.employee_id,
        		ses.periode_id,
        		ses.period_text,
        		hoc.open_periode_from,
        		hoc.open_periode_to,
        		(hoc.open_periode_to - hoc.open_periode_from + 1) AS jumlah_hari,
        		ses.state,
        		ses.directorate_id,
        		ses.hrms_department_id,
        		ses.division_id,
        		ses.branch_id,
        		he.nik,
        		he.job_id,
        		he.area,
        		jsonb_build_array(
            		ses.date_21, ses.date_22, ses.date_23, ses.date_24, ses.date_25,
            		ses.date_26, ses.date_27, ses.date_28, ses.date_29, ses.date_30, ses.date_31,
            		ses.date_01, ses.date_02, ses.date_03, ses.date_04, ses.date_05,
            		ses.date_06, ses.date_07, ses.date_08, ses.date_09, ses.date_10,
            		ses.date_11, ses.date_12, ses.date_13, ses.date_14, ses.date_15,
            		ses.date_16, ses.date_17, ses.date_18, ses.date_19, ses.date_20
        		) AS nilai_semua
    		FROM public.sb_employee_shift ses
    		JOIN hr_employee he ON he.id = ses.employee_id
    		JOIN hr_opening_closing hoc ON ses.periode_id = hoc.id
	),

	expanded AS (
    		SELECT
       		 b.employee_id,
       		 b.periode_id,
        		 b.period_text,
        		 b.open_periode_from,
        		 b.open_periode_to,
          		 b.state,
        		 b.directorate_id,
        		 b.hrms_department_id,
        		 b.division_id,
        		 b.branch_id,
        		 b.nik,
        		 b.job_id,
        		 b.area,
        		(b.open_periode_from + (idx - 1) * interval '1 day')::date AS tanggal,
        		(b.nilai_semua ->> (idx - 1))::int AS wdcode,
        			hwd.code AS wd_name
    			FROM base b
    			CROSS JOIN generate_series(1, 31) AS gs(idx)
    			LEFT JOIN hr_working_days hwd ON (b.nilai_semua ->> (idx - 1))::int = hwd.id
    			WHERE gs.idx <= (b.open_periode_to - b.open_periode_from + 1)
	)
        SELECT 
            empg.empgroup_id,
            NULL AS department_id,
            e.employee_id,
            e.job_id,
            88 AS create_uid,
            88 AS write_uid,
            e.nik,
            NOW() AS create_date,
            NOW() AS write_date,
            e.branch_id,
            NULL AS area_id,
            e.wdcode,
            e.tanggal AS valid_from,
            e.tanggal AS valid_to,
            empg.empgroup_name,
            e.wd_name,
            --NULL AS state,
		'approved' as state,
            e.division_id,
            e.hrms_department_id,
            e.directorate_id,
            NULL AS area,
            NULL AS name
        FROM expanded e
        CROSS JOIN (
            SELECT id AS empgroup_id, name AS empgroup_name 
            FROM hr_empgroup 
            WHERE id = p_empgroup_id 
		-- and state='darft'
        ) empg
        WHERE e.state = 'approved'
          AND e.periode_id = p_periode_id
        ORDER BY 
            e.employee_id, 
            e.tanggal, 
            e.periode_id, 
            e.branch_id;

        --  Jika semua berhasil
        RAISE NOTICE 'Data inserted successfully for periode_id=% and empgroup_id=%', 
            p_periode_id, p_empgroup_id;

    EXCEPTION
        WHEN OTHERS THEN
            -- Rollback otomatis untuk semua perubahan di dalam fungsi
            RAISE NOTICE 'Error inserting data for periode_id=%, empgroup_id=%. Semua perubahan dibatalkan. Error: %', 
                p_periode_id, p_empgroup_id, SQLERRM;
            ROLLBACK; -- membatalkan seluruh transaksi aktif
            RETURN;
    END;
END;
$$;
