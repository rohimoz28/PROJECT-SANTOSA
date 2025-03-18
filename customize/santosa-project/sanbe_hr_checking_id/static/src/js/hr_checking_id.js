/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from '@web/views/form/form_controller';
import { FormCompiler } from "@web/views/form/form_compiler";
import { FormRenderer } from "@web/views/form/form_renderer";
import { useOwnedDialogs, useService } from "@web/core/utils/hooks";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { Component, onRendered, useEffect, useRef, useState } from "@odoo/owl";

export class HRCheckingIDFormController extends FormController {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
        this.addDialog = useOwnedDialogs();
        this.actionService = useService("action");
        this.IdsData = this.orm.call("hr.employee", "get_all_ids", []);
    }
    async beforeExecuteActionButton(clickParams) {
        const action = clickParams.name;
        const record = this.model.root;
        if(action==="pencarian_data"){
                    const record = this.model.root;
                    const myemp = await this.orm.call("hr.checking.id", "cari_data_npwp_or_nik", [record.data.resIds,record.data.noktp,record.data.nonpwp,record.data.nonik,record.data.nonik_lama]);
                    if (JSON.stringify(myemp) == '{}'){
                        alert("DATA Not Found")
                    }else {
                        var test = $('#nonpwp_0')
                        record.data.emp_no = myemp.emp_no
                        record.nonpwp = myemp.no_npwp
                        record.noktp = myemp.no_ktp
                        record.nonik = myemp.service_nik
                        record.nonik_lama = myemp.nik_lama
                        record.data.nik = myemp.nik
                        record.data.employee_id = myemp.employee_id
                        record.data.employee_name = myemp.employee_name
                        record.data.area = myemp.area
                        record.data.bisnis_unit = myemp.bisnis_unit
                        record.data.departmentid = myemp.departmentid
                        record.data.jobstatus = myemp.jobstatus
                        record.data.employementstatus = myemp.employementstatus
                        record.data.jobtitle = myemp.jobtitle
                        record.data.empgroup = myemp.empgroup
                    }
            return false
        } else if(action==="aktivasi_data"){
            console.log('2222222222222222222222222');
            console.log('aktivasi_data1');
            console.log(record.data.nik);
            console.log('2222222222222222222222222');
            this.mymut = await this.orm.call("hr.checking.id", "aktivasi_data", [record.data.resIds,record.data.nik],{});
            console.log('------');
            console.log(this.mymut);
            console.log('------');
            this.model.root.save();
            console.log('2222222222222222222222222');
            if (this.mymut){
                this.actionService.doAction({
                    type: 'ir.actions.act_window',
                    views: [[false, 'form']],
                    res_model: 'hr.employee.mutations',
                    res_id: this.mymut,
                    //target: 'current',
                    //context: {
                    //    create: false,
                    //    edit: false
                    //}
                });
            } else {
                return false
            }
        } else if(action==="clear_list_Data"){
            console.log('clear_list_Data')
            return false;
        } else if (clickParams.special!== "cancel" || clickParams.special=== "cancel") {
            console.log('clickParams.special')
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
                    const canProceed = record.save({
                        stayInEdition: true,
                        useSaveErrorDialog: true,
                    });
                    console.log('0000000000000000000')
                    console.log(resIds)
                    console.log(record.data.resIds)
                    console.log('0000000000000000000')
                    const myemp = await this.orm.call("hr.employee", "get_all_emp_byid", [resIds]);
                    record.data.emp_no = myemp.emp_no
                    record.data.nik = myemp.nik
                    record.data.nik_lama = myemp.nik_lama
                    record.data.employee_id = myemp.employee_id
                    record.data.employee_name = myemp.employee_name
                    record.data.area = myemp.area
                    record.data.bisnis_unit = myemp.bisnis_unit
                    record.data.departmentid = myemp.departmentid
                    record.data.jobstatus = myemp.jobstatus
                    record.data.employementstatus = myemp.employementstatus
                    record.data.jobtitle = myemp.jobtitle
                    record.data.empgroup = myemp.empgroup

                    await self.orm.call("hr.employment.tracking", "isi_details_tracking",[record.resId]);
                },
            });
       }

//        this.closePopover();
//        await this.orm.call(this.props.record.resModel, 'js_remove_outstanding_partial', [moveId, partialId], {});
//        await this.props.record.model.root.load();
//        this.props.record.model.notify();
}
//RouteAssignFormController.template = 'pest_widget.RouteAssignRouteListRenderer'
HRCheckingIDFormController.components = {
    ...FormController.components,
};

export const HRCheckingIDFormViews = {
    ...formView,
    Controller: HRCheckingIDFormController,
};
registry.category("views").add("hr_checking_id", HRCheckingIDFormViews);