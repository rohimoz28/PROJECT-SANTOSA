/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from '@web/views/form/form_controller';
import { FormCompiler } from "@web/views/form/form_compiler";
import { FormRenderer } from "@web/views/form/form_renderer";
import { useOwnedDialogs, useService } from "@web/core/utils/hooks";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";

export class EmployeeMutationFormController extends FormController {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
        this.addDialog = useOwnedDialogs();
        this.IdsData = this.orm.call("hr.employee", "get_all_ids", []);
        this.dataid =false;
    }
    async beforeExecuteActionButton(clickParams) {
        const action = clickParams.name;
        const record = this.model.root;
        if(action==="pencarian_data"){
            this.dataid = record.data.res_id || false;
            this._open_search_wizard()
            return false
        }
        if(action==="button_approve"){
            record.save();
            return true
        }
         else if (clickParams.special!== "cancel" || clickParams.special=== "cancel") {
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
                    const record = self.model.root;
                    const params = { reload: !(this.env.inDialog && clickParams.close) };
                    await record.save(params);
                    console.log( 'data id ', record.resIds)
                    const myemp = await this.orm.call("hr.employee", "get_all_emp_byid", [resIds]);
                    const myemps = await this.orm.call("hr.employee.mutations", "isi_data_employee", [record.resId,myemp.emp_no]);

                     await record.save();
                     self.model.root.load()
//                    console.log('this emp ', JSON.stringify(myemp))
//                    record.data.emp_no = myemp.emp_no
//                    record.data.nik = myemp.nik
//                    record.data.employee_id = myemp.employee_id
//                    record.data.employee_name = myemp.employee_name
//                    record.data.area = myemp.area
//                    record.data.bisnis_unit = myemp.bisnis_unit
//                    record.data.departmentid = myemp.departmentid
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
EmployeeMutationFormController.components = {
    ...FormController.components,
};

export const EmployeeMutationFormViews = {
    ...formView,
    Controller: EmployeeMutationFormController,
};
registry.category("views").add("hr_employee_mutation", EmployeeMutationFormViews);