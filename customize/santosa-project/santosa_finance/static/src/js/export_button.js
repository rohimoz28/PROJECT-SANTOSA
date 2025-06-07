/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";

export class OdooOWLListController extends ListController {
   setup() {
       super.setup();
   }

   showCustomers() {
    this.env.services.action.doAction({
        type: 'ir.actions.act_window',
        name: 'Rekap Honor Dokter',
        res_model: 'export.honor.dokter',
        view_mode: 'tree',
        view_id: 'sanbe_finance.action_export_honor_dokter_wizard',
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
viewRegistry.add("owl_export_controller", OWLListController);