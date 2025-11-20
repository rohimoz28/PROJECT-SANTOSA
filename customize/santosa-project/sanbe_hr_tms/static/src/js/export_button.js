/** @odoo-module **/
import { ListController } from "@web/views/list/list_controller"
import { ListRenderer } from "@web/views/list/list_renderer"
import { registry } from "@web/core/registry"
import { listView } from "@web/views/list/list_view"
import { useState, onWillStart } from "@odoo/owl"

// Renderer custom (minimal)
export class OdooOWLListRenderer extends ListRenderer {}

// Controller custom
export class OdooOWLListController extends ListController {
    setup() {
        super.setup()

        // state untuk cek group HRD
        this.state = useState({ isHrd: false }) // 2. Akses context dari props
        const context = this.props.context || {}
        const hasGroupFromContext = context.hasgroup || false
        // jalankan sebelum render
        onWillStart(async () => {
            // Proses ini (hasGroup) ASINKRON
            // this.state.isHrd = await this.env.services.user.hasGroup("sanbe_hr_tms.group_shift_hrd")

            this.state.isHrd = await hasGroupFromContext
            console.log("isHrd (JS):", this.state.isHrd) // Hasil yang benar (True)
            this.render()
        })
    }

    getRendererProps() {
        // Meneruskan state dan methods ke Renderer props
        return {
            ...super.getRendererProps(),
            // Action methods
            showCustomers: this.showCustomers.bind(this),
            showImportEmployee: this.showImportEmployee.bind(this),
            showShifttoEMPgroup: this.showShifttoEMPgroup.bind(this),
            showImportxls: this.showImportxls.bind(this),
            // Meneruskan state isHrd (nilai Boolean)
            isHrd: this.state.isHrd,
        }
    }

    // Action buttons (metode dipanggil via t-on-click dari XML)
    showCustomers() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "Rekap Perhitungan Kehadiran",
            res_model: "export.excel.tms",
            view_mode: "form", // Biasanya form untuk wizard/pop-up
            views: [[false, "form"]],
            target: "new",
        })
    }

    showImportEmployee() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "Search Employee",
            res_model: "wiz.employee.shift",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_target_models: "sb.employee.shift",
                default_target_process: "generate",
            },
        })
    }

    showShifttoEMPgroup() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "Process Shift to EMPGroup",
            res_model: "wiz.employee.shift",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_target_models: "sb.employee.shift",
                default_target_process: "shift to EMP",
            },
        })
    }

    showImportxls() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "Import XLS to Shift",
            res_model: "wiz.employee.shift",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_target_models: "sb.employee.shift",
                default_target_process: "process xls",
            },
        })
    }
}

// Registrasi view
registry.category("views").add("owl_list_controller", {
    ...listView,
    Controller: OdooOWLListController,
    Renderer: OdooOWLListRenderer, // Atau langsung ListRenderer jika Anda tidak perlu kustomisasi di dalamnya
})
