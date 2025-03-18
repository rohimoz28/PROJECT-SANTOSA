CREATE OR REPLACE PROCEDURE public.generate_ot_request()
    LANGUAGE plpgsql
AS $procedure$
begin
with ote as (select *
             from hr_overtime_employees hoe
             where hoe.planning_id is null),
     emp as (select ote.*, he.id as employeeid
             from ote,
                  hr_employee he
             where he.nik = ote.nik),
     empg as (select emp.*, hop.id as planningid
              from hr_overtime_planning hop,
                   emp
              where emp.planning_req_name = hop.name)
update hr_overtime_employees h
set employee_id = empg.employeeid,
    planning_id = empg.planningid
    from empg
where h.id = empg.id;

END;
$procedure$
;