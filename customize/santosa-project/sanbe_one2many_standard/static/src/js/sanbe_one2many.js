/** @odoo-module **/
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { evaluateBooleanExpr } from "@web/core/py_js/py";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { patch } from "@web/core/utils/patch";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { useOwnedDialogs, useService, useBus } from "@web/core/utils/hooks";
import { DomainSelector } from "@web/core/domain_selector/domain_selector";
import { Domain } from "@web/core/domain";
import { ListController } from "@web/views/list/list_controller";
import { unique } from "@web/core/utils/arrays";
import { useModelWithSampleData } from "@web/model/model";
import {
    Component,
    onMounted,
    onPatched,
    onWillPatch,
    onWillStart,
    toRaw,
    useEffect,
    useRef,
    useState,
    useSubEnv,
} from "@odoo/owl";
import { usePager } from "@web/search/pager_hook";
import { Pager } from "@web/core/pager/pager";
import { download } from "@web/core/network/download";
import { ExportDataDialog } from "@web/views/view_dialogs/export_data_dialog";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { ListRenderer } from "@web/views/list/list_renderer";
import { computeViewClassName } from "@web/views/utils";
import { ViewButton } from "@web/views/view_button/view_button";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { useSearchBarToggler } from "@web/search/search_bar/search_bar_toggler";

export class O2MListRenderer extends ListRenderer {
    /** Replace the existing function to show selection in the One2many field
         when delete possible **/
    get hasSelectors() {
        const recss = ["hr.empgroup.details","hr.attendance"]
        if (this.props.list.resModel == 'hr.attendance' || this.props.list.resModel == 'hr.empgroup.details') {
            this.props.allowSelectors = true
        }
        
        let list = this.props.list
        list.selection = list.records.filter((rec) => rec.selected)
        list.selectDomain = (value) => {
            list.isDomainSelected = value;
            list.model.notify();
        }
        return this.props.allowSelectors && !this.env.isSmall;
    }
    async onCellClicked(record, column, ev) {
        if (this.props.list.resModel == 'hr.attendance') {
            console.log('0000000000')
            console.log(this.props.list.resModel)
            console.log(record)
            console.log(record.evalContext)
            console.log(record.evalContext.id)
            console.log('0000000000')
            const re_action = {
                name: "hr attendance",
                //'views': [[self.env.ref('sanbe_hr_tms.hr_tmsentry_form_ext').id, 'form']],
                res_model: "hr.attendance",
                res_id: record.evalContext.id,
                type: "ir.actions.act_window",
                views: [[false, "form"]],
                target: "current",
                context: {'create':"0",'edit':"0",'delete':"0",'force_save':"1",
                    dialog_size: 'medium',
                    form_view_ref: 'sanbe_hr_tms.hr_tmsentry_form_ext'
                }
            }
            this.env.services.action.doAction(re_action);
        }
        else{
            super.onCellClicked(record, column, ev);
        }
    }
    toggleSelection() {
        const list = this.props.list;
        if (!this.canSelectRecord) {
            return;
        }
        if (list.selection.length === list.records.length) {
            list.records.forEach((record) => {
                record.toggleSelection(false);
                list.selectDomain(false);
            });
        } else {
            list.records.forEach((record) => {
                record.toggleSelection(true);
            });
        }
    }
    /** Function that returns if selected any records **/
    get selectAll() {
        const list = this.props.list;
        const nbDisplayedRecords = list.records.length;
        if (list.isDomainSelected) {
          return true;
        }
        else {
          return false
        }
    }
}

export const ImportModuleListViewAtt = {
    ...listView,
    Renderer: O2MListRenderer,
}

registry.category("views").add("ir_module_module_tree_att_view", ImportModuleListViewAtt);

patch(X2ManyField.prototype, {

    onInputKeyUp() {
        const recsss = ["hr.empgroup.details","hr.attendance"]
        var value = $(event.currentTarget).val().toLowerCase();
        $(".o_list_table tr:not(:lt(1))").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    },
    
    setup() {
        super.setup(...arguments);
        const resModelx = this.list.resModel;
        if (resModelx == 'hr.attendance' || resModelx == 'hr.empgroup.details') {
            X2ManyField.components = { Pager, KanbanRenderer, ListRenderer: O2MListRenderer };
        }else{
            X2ManyField.components = { Pager, KanbanRenderer, ListRenderer};
        }
        
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.addDialog = useOwnedDialogs();
        this.action = useService("action");
        this.rpc = useService("rpc");
        this.optionalActiveFields = [];
        this.IdsData = this.props.record.data[this.props.name].currentIds;
        this.searchBarToggler = useSearchBarToggler();
        //this.firstLoad = true;
    },
    
    get hasSelected(){
        //if (this.list.resModel === "hr.empgroup.details") {
        return this.list.records.filter((rec) => rec.selected).length;
        //} else {
        //    return;
        //}
    },
    
    async deleteSelected(){
        if (this.list.resModel !== "hr.empgroup.details") {
            return;
        }
        var current_model = this.field.relation;
        var w_response = confirm("Do You Want to Delete ?");
        if (w_response){
            let selected = this.list.records.filter((rec) => rec.selected)
            if (selected[0].evalContext.empgroup_id.state == 'approved' || selected[0].evalContext.empgroup_id.state == 'close'){
              this.dialog.add(AlertDialog, {
                        body: _t("Can't able to delete This Record"),
                        });
            }
            else{
                selected.forEach((rec) => {
                            if (this.activeActions.onDelete) {
                                    selected.forEach((rec) => {
                                            this.activeActions.onDelete(rec);
                                    })
                            }
                })
            }
        }
    },
    //Function to delete all the unselected records
    async ApproveSelected(){
        let selectedx = this.list.records.filter((rec) => rec.selected)
        const record = this.list.model.root;
        
        if (this.list.resModel !== "hr.attendance") {
            return;
        }
        var current_model = this.field.relation;
        var w_response = confirm("Do You Want to Approve Selected Record ?");
        if (w_response){
            let selected = this.list.records.filter((rec) => rec.selected)
            if (selected.length > 0){
                selected.forEach((rec) => {
                    //this.activeActions.onDelete(rec);
                    console.log('uuuuuuuuuuuuuu');
                    console.log(rec.evalContext.id);
                    console.log(rec.evalContext.time_in);
                    console.log(rec.evalContext.time_in_edited);
                    console.log(rec.evalContext.time_out);
                    console.log(rec.evalContext.time_out_edited);
                    console.log('uuuuuuuuuuuuuu');
                    const message = this.orm.call(this.list.resModel, "approved_data_all", [rec.evalContext.id]);
                    rec.load();
                });
            }
            
            record.load();
            record.model.notify();
        }
    },
    async onDirectExportData() {
        await this.downloadExport(this.defaultExportList, false, "xlsx");
    },
    _open_search_wizard(){
        var self = this;
        const { fieldString, multiSelect, resModel } = this.list;
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
            resModel: resModel,
            dynamicFilters,
            context: self.props.context || {},
        });

    },
    async importRecords() {
        const { context } = this.list;
        const resModel = this.list.resModel;
        this.action.doAction({
            type: "ir.actions.client",
            tag: "import",
            params: { model: resModel, context },
        });
    },
    get defaultExportList() {
        const { archInfo } = this;
        return []
    },
    async onExportData() {
        const dialogProps = {
            context: this.props.context,
            defaultExportList: this.defaultExportList,
            download: this.downloadExport.bind(this),
            getExportedFields: this.getExportedFields.bind(this),
            root: this.list.model.root,
            list: this.list,
        };
        this.dialogService.add(ExportDataDialog, dialogProps);
    },
    async downloadExport(fields, import_compat, format) {
        let ids = false;
        if (!this.isDomainSelected) {
            const resIds = this.list.resIds;
            ids = resIds.length > 0 && resIds;
        }
        const exportedFields = fields.map((field) => ({
            name: field.name || field.id,
            label: field.label || field.string,
            store: field.store,
            type: field.field_type || field.type,
        }));
        if (import_compat) {
            exportedFields.unshift({
                name: "id",
                label: _t("External ID"),
            });
        }
        const domain =
            typeof this.props.domain === "function" ? this.props.domain() : this.props.domain;
        await download({
            data: {
                data: JSON.stringify({
                    import_compat,
                    context: this.props.context,
                    domain: domain,
                    fields: exportedFields,
                    groupby: this.list.model.root.groupBy,
                    ids,
                    model: this.list.resModel,
                }),
            },
            url: `/web/export/${format}`,
        });
    },
    async getExportedFields(model, import_compat, parentParams) {
        model = this.list.resModel;
        return await this.rpc("/web/export/get_fields", {
            ...parentParams,
            model,
            import_compat,
        });
    },

     async Print_excel_report(){
        var model = this.props.record.resModel
        var order = this.props.record.data.id
        var one2many = this.props.name
        var relation=this.activeField.relation
        var related_field = this.field.relation_field
        var action = {
                type: "ir.actions.report",
                report_type: "xlsx",
                report_name: 'Excel',
                report_file: "report.excel",
                context:{'model':relation,'id':order,'field':related_field},
        };
        return this.action.doAction(action);
    },

});