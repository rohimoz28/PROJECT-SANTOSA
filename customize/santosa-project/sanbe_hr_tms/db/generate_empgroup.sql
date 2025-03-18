CREATE OR REPLACE PROCEDURE public.generate_empgroup()
    LANGUAGE plpgsql
AS $procedure$
begin
with flag as (select id, nik, valid_from, valid_to, wdcode_name, empgroup_name
              from hr_empgroup_details hed),
     empgroup as (select f.*, he.id as empgroup_id
                  from flag f,
                       hr_empgroup he
                  where name = f.empgroup_name),
     employee as (select h.name,
                         h.id         as employee_id,
                         h.department_id,
                         h.job_id,
                         eg.*,
                         h.area,
                         h.branch_id,
                         h.emp_status as employment_status
                  from empgroup eg,
                       hr_employee h
                  where h.nik = eg.nik),
     wd as (select e.*, hwd.id as wdcode
            from employee e
                     left join
                 hr_working_days hwd
                 on hwd.code = e.wdcode_name)
update hr_empgroup_details d
set empgroup_id   = wd.empgroup_id,
    department_id = wd.department_id,
    state         = wd.employment_status,
    branch_id     = wd.branch_id,
    area_id       = wd.area,
    wdcode        = wd.wdcode,
    employee_id   = wd.employee_id,
    job_id        = wd.job_id
    from wd
where d.id = wd.id;

END;
$procedure$
;