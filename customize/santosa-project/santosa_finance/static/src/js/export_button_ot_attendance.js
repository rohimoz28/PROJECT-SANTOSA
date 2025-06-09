/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";

export class OdooOWLListController extends ListController {
   setup() {
       super.setup();
   }

   showOT() {
    this.env.services.action.doAction({
        type: 'ir.actions.act_window',
        name: 'Overtime Attendances',
        res_model: 'export.excel.ot.attendance',
        view_mode: 'tree',
        view_id: 'santosa_finance.export_excel_ot_attendance_action_wizard',
        views: [[false, 'form']],
        target: 'new'
    });
   }
}


const viewRegistry = registry.category("views");
export const OWLListController = {
    ...listView,
    Controller: OdooOWLListController,
};
viewRegistry.add("owl_list_controller_ot_attendance", OWLListController);