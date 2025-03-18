/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { FormController } from '@web/views/form/form_controller';
import { FormCompiler } from "@web/views/form/form_compiler";
import { FormRenderer } from "@web/views/form/form_renderer";
import { useService } from "@web/core/utils/hooks";

export class MonitoringContractFormController extends FormController {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.orm = useService("orm");


    }
    async beforeExecuteActionButton(clickParams) {
        const action = clickParams.name;
        const record = this.model.root;
        console.log()
        if(action==="pencarian_data"){
            const canProceed = this.model.root.save({
                stayInEdition: true,
                useSaveErrorDialog: true,
            });
            let area = false;
            if (record.data.area[0] !== undefined) {
                area = record.data.area[0]
            }
            let bisnis_unit= false;
            if (record.data.bisnis_unit[0] !== undefined) {
                bisnis_unit = record.data.bisnis_unit[0];
            }
            let job_status= false;
            if(record.data.job_status !== undefined) {
                job_status = record.data.job_status;
            }
            let emp_status= false;
            if(record.data.emp_status !== undefined) {
                emp_status=record.data.emp_status;
            }
            let department_id= false;
            if (record.data.department_id[0] !== undefined) {
                department_id = record.data.department_id[0]
            }
            let contractend_start= false;
            if( record.data.contractend_start !== undefined) {
                 contractend_start = record.data.contractend_start
            }
            let contractend_end= false;
            if (record.data.contractend_end !== undefined) {
                 contractend_end = record.data.contractend_end;
            }
            let bsdate_from= false;
            if(record.data.bsdate_from !== undefined) {
                bsdate_from = record.data.bsdate_from;
            }
            let bsdate_to= false;
            if (record.data.bsdate_to !== undefined) {
                bsdate_to = record.data.bsdate_to;
            }
            let pension_start= false;
            if (record.data.pension_start !== undefined) {
                pension_start = record.data.pension_start;
            }
            let pension_end= false;
            if (record.data.pension_end !== undefined) {
                pension_end = record.data.pension_end
            }
            const datakelurahan = await this.orm.call("hr.monitoring.contract", "pencarian_data", [this.model.root.resId,area,bisnis_unit,job_status,emp_status,department_id,contractend_start,contractend_end,bsdate_from,bsdate_to,pension_start,pension_end], {
            });

//            let operation;
//            operation = { operation: "TRIGGER_ONCHANGE" };
//            this.model.root.__syncParent(operation);
//            await this.model.load();
            await this.model.root.load();
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

//        this.closePopover();
//        await this.orm.call(this.props.record.resModel, 'js_remove_outstanding_partial', [moveId, partialId], {});
//        await this.props.record.model.root.load();
//        this.props.record.model.notify();
}
//RouteAssignFormController.template = 'pest_widget.RouteAssignRouteListRenderer'
MonitoringContractFormController.components = {
    ...FormController.components,
};

export const MonitoringContractFormViews = {
    ...formView,
    Controller: MonitoringContractFormController,
};
registry.category("views").add("hr_monitoring_contract", MonitoringContractFormViews);