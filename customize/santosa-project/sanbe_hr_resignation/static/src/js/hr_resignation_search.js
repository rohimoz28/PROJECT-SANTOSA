/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from '@web/views/form/form_controller';
import { FormCompiler } from "@web/views/form/form_compiler";
import { FormRenderer } from "@web/views/form/form_renderer";
import { useOwnedDialogs, useService } from "@web/core/utils/hooks";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";

export class HRResignationFormController extends FormController {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
        this.addDialog = useOwnedDialogs();
        this.IdsData = this.orm.call("hr.employee", "get_all_ids", []);

    }
    async beforeExecuteActionButton(clickParams) {
        const action = clickParams.name;
        if(action==="button_cari_data"){
            this._open_search_wizard()
            return false
        } else if(action==="clear_list_Data"){


            return false;
        }


         else       if (clickParams.special!== "cancel" || clickParams.special=== "cancel") {
            this.model.root.save();
            return true
        }
       return super.beforeExecuteActionButton(clickParams);
    }

    _open_search_wizard(){
            var self = this;
            const dynamicFilters = this.IdsData.length
                ? [
                      {
                          domain: [["id", 'in', this.IdsData]],
                      },
                  ]
                : undefined;
            this.addDialog(SelectCreateDialog, {
                noCreate: true,
                multiSelect: false,
                resModel: 'hr.employee',
                dynamicFilters,
                 context: {},
                onSelected: async (resIds) => {
                     const proms = [];
                    const record = self.model.root;
                    const params = { reload: !(this.env.inDialog && clickParams.close) };

                    console.log( 'data id ', record.emp_no)
                    const myemp = await this.orm.call("hr.employee", "get_all_emp_byid", [resIds]);
//                    const myemps = await this.orm.call("hr.employee.mutations", "isi_data_employee", [record.resId,myemp.emp_no]);


//                    console.log('this emp ', JSON.stringify(myemp))
                    record.data.emp_no = myemp.emp_no
                    record.data.emp_nik = myemp.nik
                    record.data.employee_id = myemp.employee_id
                    record.data.area = myemp.service_area
                    record.data.bisnis_unit = myemp.service_bisnisunit
                    record.data.departmentid = myemp.service_departmentid
                    record.data.directorateid = myemp.service_directorateid
                    record.data.hrmsdepartmentid = myemp.service_hrmsdepartmentid
                    record.data.divisionid = myemp.service_divisionid
                    record.data.bondservice_from = myemp.service_from
                    record.data.bondservice_to = myemp.service_to
                    console.log('data res id ',)
                    let changes = {
                       emp_no: myemp.emp_no,
                    };
//                    changes = Object.assign(changes, {
//                        emp_no: myemp.emp_no,
//                        emp_nik: myemp.nik,
//                        employee_id: myemp.employee_id,
//                        area: myemp.service_area,
//                        bisnis_unit: myemp.service_bisnisunit,
//                        departmentid: myemp.service_departmentid,
//                        bondservice_from: myemp.service_from,
//                        bondservice_to: myemp.service_to
//                    });
                    record.update({ [this.props.name]: 'test' });
//                    record.update({ [record]: record.data.emp_no });
//                    const myemps = await this.orm.call("hr.resignation", "isi_asset", [[this.model.root.resIds],resIds]);

               // window.location.reload(true);
//                     proms.push(myemps);
//                     await Promise.all(proms);
//                    record.data.subdepartment = myemp.subdepartment
//                    record.data.jobstatus = myemp.jobstatus
//                    record.data.employementstatus = myemp.employementstatus
//                    record.data.jobtitle = myemp.jobtitle
//                    record.data.empgroup = myemp.empgroup
//
//                    record.data.service_nik = myemp.service_nik
//                    record.data.service_area = myemp.service_area
//                    record.data.service_bisnisunit = myemp.service_bisnisunit
//                    record.data.service_departmentid = myemp.service_departmentid
//                    record.data.service_subdepartment = myemp.service_subdepartment
//                    record.data.service_jobstatus = myemp.service_jobstatus
//                    record.data.service_employementstatus =  myemp.service_employementstatus
//                    record.data.service_jobtitle = myemp.service_jobtitle
//                    record.data.service_empgroup = myemp.service_empgroup
                },
            });
       }
}
//RouteAssignFormController.template = 'pest_widget.RouteAssignRouteListRenderer'
HRResignationFormController.components = {
    ...FormController.components,
};

export const hrResignationFormViews = {
    ...formView,
    Controller: HRResignationFormController,
};
registry.category("views").add("hr_resignation", hrResignationFormViews);