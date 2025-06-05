/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ExportDataDialog } from "@web/views/view_dialogs/export_data_dialog"
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { Dialog } from "@web/core/dialog/dialog";
import { unique } from "@web/core/utils/arrays";
import { useService } from "@web/core/utils/hooks";
import { fuzzyLookup } from "@web/core/utils/search";
import { useSortable } from "@web/core/utils/sortable_owl";
import { useDebounced } from "@web/core/utils/timing";
import { Component, useRef, useState, onMounted, onWillStart, onWillUnmount } from "@odoo/owl";

patch(ExportDataDialog.prototype, {
    setup() {
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.draggableRef = useRef("draggable");
        this.exportListRef = useRef("exportList");
        this.searchRef = useRef("search");

        this.knownFields = {};
        this.expandedFields = {};
        this.availableFormats = [];
        this.templates = [];

        this.state = useState({
            exportList: [],
            isCompatible: false,
            isEditingTemplate: false,
            search: [],
            selectedFormat: 0,
            templateId: null,
            isSmall: this.env.isSmall,
            disabled: false,
        });

        this.title = _t("Export Data");
        this.newTemplateText = _t("New template");
        this.removeFieldText = _t("Remove field");

        this.debouncedOnResize = useDebounced(this.updateSize, 300);

        useSortable({
            // Params
            ref: this.draggableRef,
            elements: ".o_export_field",
            enable: !this.state.isSmall,
            cursor: "grabbing",
            // Hooks
            onDrop: async ({ element, previous, next }) => {
                const indexes = [element, previous, next].map(
                    (e) =>
                        e &&
                        Object.values(this.state.exportList).findIndex(
                            ({ id }) => id === e.dataset.field_id
                        )
                );
                let target;
                if (indexes[0] < indexes[1]) {
                    target = previous ? indexes[1] : 0;
                } else {
                    target = next ? indexes[2] : this.state.exportList.length - 1;
                }
                this.onDraggingEnd(indexes[0], target);
            },
        });

        onWillStart(async () => {
            this.availableFormats = await this.rpc("/web/export/formats");
            if(this.props.list){
                this.templates = await this.orm.searchRead(
                    "ir.exports",
                    [["resource", "=", this.props.list.resModel]],
                    [],
                    {
                        context: this.props.context,
                    }
                );
            } else {
                 this.templates = await this.orm.searchRead(
                    "ir.exports",
                    [["resource", "=", this.props.root.resModel]],
                    [],
                    {
                        context: this.props.context,
                    }
                );
            }
            await this.fetchFields();
        });

        onMounted(() => {
            browser.addEventListener("resize", this.debouncedOnResize);
            this.updateSize();
        });

        onWillUnmount(() => browser.removeEventListener("resize", this.debouncedOnResize));
    },
    async loadExportList(value) {
        this.state.templateId = value === "new_template" ? value : Number(value);
        this.state.isEditingTemplate = value === "new_template";
        if (!value || value === "new_template") {
            return;
        }
        if (this.props.list){
            const fields = await this.rpc("/web/export/namelist", {
                model: this.props.list.resModel,
                export_id: Number(value),
            });
            this.state.exportList = fields.map(({ label, name }) => {
                return {
                    string: label,
                    id: name,
                };
            });
        } else {
            const fields = await this.rpc("/web/export/namelist", {
                model: this.props.root.resModel,
                export_id: Number(value),
            });
            this.state.exportList = fields.map(({ label, name }) => {
                return {
                    string: label,
                    id: name,
                };
            });
        }
    },
    async onSaveExportTemplate() {
        const name = this.exportListRef.el.value;
        if (!name) {
            return this.notification.add(_t("Please enter save field list name"), {
                type: "danger",
            });
        }
        if (this.props.list){
             const [id] = await this.orm.create(
                "ir.exports",
                [
                    {
                        name,
                        export_fields: this.state.exportList.map((field) => [
                            0,
                            0,
                            {
                                name: field.id,
                            },
                        ]),
                        resource: this.props.list.resModel,
                    },
                ],
                { context: this.props.context }
            );
            this.state.isEditingTemplate = false;
            this.state.templateId = id;
            this.templates.push({ id, name });
        }else{
            const [id] = await this.orm.create(
                "ir.exports",
                [
                    {
                        name,
                        export_fields: this.state.exportList.map((field) => [
                            0,
                            0,
                            {
                                name: field.id,
                            },
                        ]),
                        resource: this.props.root.resModel,
                    },
                ],
                { context: this.props.context }
            );
            this.state.isEditingTemplate = false;
            this.state.templateId = id;
            this.templates.push({ id, name });
        }

    },

    async loadFields(id, preventLoad = false) {
        let model;
         if (this.props.list){
           model = this.props.list.resModel;
         } else {
            model = this.props.root.resModel;
         }
        let parentField, parentParams;
        if (id) {
            if (this.expandedFields[id]) {
                // we don't make a new RPC if the value is already known
                return this.expandedFields[id].fields;
            }
            parentField = this.knownFields[id];
            model = parentField.params && parentField.params.model;
            parentParams = {
                ...parentField.params,
                parent_field_type: parentField.field_type,
                parent_field: parentField,
                parent_name: parentField.string,
                exclude: [parentField.relation_field],
            };
        }
        if (preventLoad) {
            return;
        }
        const fields = await this.props.getExportedFields(
            model,
            this.state.isCompatible,
            parentParams
        );
        for (const field of fields) {
            field.parent = parentField;
            if (!this.knownFields[field.id]) {
                this.knownFields[field.id] = field;
            }
        }
        if (id) {
            this.expandedFields[id] = { fields };
        }
        return fields;
    }
})
patch(ExportDataDialog,{
    props: {
        close: { type: Function },
        context: { type: Object, optional: true },
        defaultExportList: { type: Array },
        download: { type: Function },
        getExportedFields: { type: Function },
        root: { type: Object },
        list: { type: Object, optional: true },
    },
});
