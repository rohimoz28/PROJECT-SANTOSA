/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";

export class OvertimeBundlingController extends ListController {
    setup() {
        super.setup();
    }

    showOTBundling() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Overtime Bundling',
            res_model: 'export.excel.ot.bundling',
            view_mode: 'tree',
            view_id: 'sanbe_hr_tms.export_excel_ot_bundling_action_wizard',
            views: [[false, 'form']],
            target: 'new'
        });
    }
}

const viewRegistry = registry.category("views");
export const OtBundlingController = {
    ...listView,
    Controller: OvertimeBundlingController,
};
viewRegistry.add("owl_list_controller_ot_bundling", OtBundlingController)
