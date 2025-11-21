/** @odoo-module */

import {ListController} from "@web/views/list/list_controller";
import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {useService} from "@web/core/utils/hooks";
import {useState, onWillStart} from "@odoo/owl";

export class OdooOWLListController extends ListController {
    setup() {
        super.setup();
        // Tambahkan service
        this.orm = useService("orm");
        this.actionService = useService("action");

        // State untuk group check
        this.state = useState({
            ...this.state,  // Keep existing state
            hasShiftHRDAccess: false,
        });

        // Check group saat component mount
        onWillStart(async () => {
            await this.checkGroupAccess();
        });
    }

    /**
     * Check if current user has specific group access
     * @returns {boolean}
     */
    get hasShiftHRDAccess() {
        // Method 1: Check by XML ID
        // Format: 'module_name.group_xml_id'
        return this.user.hasGroup('sanbe_hr_tms.group_shift_hrd');
    }

    /**
     * Check apakah user punya akses group
     */
    async checkGroupAccess() {
        try {
            const hasAccess = await this.orm.call(
                "res.users",
                "has_group",
                ["sanbe_hr_tms.group_shift_hrd"]
            );
            this.state.hasShiftHRDAccess = hasAccess;
        } catch (error) {
            console.error("Error checking group access:", error);
            this.state.hasShiftHRDAccess = false;
        }
    }
    
    showCustomers() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Rekap Perhitungan Kehadiran',
            res_model: 'export.excel.tms',
            view_mode: 'tree',
            view_id: 'sanbe_hr_tms.export_excel_tms_action_wizard',
            views: [[false, 'form']],
            target: 'new'
        });
    }

    showImportEmployee() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Search Employee',
            res_model: 'wiz.employee.shift',
            view_mode: 'form',
            view_id: 'sanbe_hr_tms.wiz_employee_shift_wizard_view_form',
            views: [[false, 'form']],
            target: 'new',
            context: {
                default_target_models: 'sb.employee.shift',
                default_target_process: 'generate',
            }
        });
    }

    showShifttoEMPgroup() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Process Shift to EMPGroup',
            res_model: 'wiz.employee.shift',
            view_mode: 'form',
            view_id: 'sanbe_hr_tms.wiz_employee_shift_wizard_view_form',
            views: [[false, 'form']],
            target: 'new',
            context: {
                default_target_models: 'sb.employee.shift',
                default_target_process: 'shif to EMP',
            }
        });
    }

    showImportxls() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Import XLS to Shift',
            res_model: 'wiz.employee.shift',
            view_mode: 'form',
            view_id: 'sanbe_hr_tms.wiz_employee_shift_wizard_view_form',
            views: [[false, 'form']],
            target: 'new',
            context: {
                default_target_models: 'sb.employee.shift',
                default_target_process: 'process xls',
            }
        });
    }

}


const viewRegistry = registry.category("views");
export const OWLListController = {
    ...listView,
    Controller: OdooOWLListController,
};
viewRegistry.add("owl_list_controller", OWLListController);