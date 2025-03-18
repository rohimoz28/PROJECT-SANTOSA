/** @odoo-module **/
    import { patch } from "@web/core/utils/patch";
    import {Dialog} from "@web/core/dialog/dialog";
    import { useService } from "@web/core/utils/hooks";

patch(Dialog.prototype, {
        setup() {
            super.setup(...arguments);
            this.orm = useService("orm");
        },
        willStart() {
            var self = this;
            return super.willStart(... arguments).then(function () {
                self.$modal
                    .find(".dialog_button_extend")
                    .on("click", self.proxy("_extending"));
                self.$modal
                    .find(".dialog_button_restore")
                    .on("click", self.proxy("_restore"));
                return this.config.then(function (r) {
                    if (r.default_maximize) {
                        self._extending();
                    } else {
                        self._restore();
                    }
                });
            });
        },
        config(){
            const data = this.orm.call("ir.config_parameter", "get_web_dialog_size_config", []);
            return data;
        },
        opened() {
            return super.opened(... arguments).then(
                function () {
                    if (this.$modal) {
                        this.$modal.find(">:first-child").draggable({
                            handle: ".modal-header",
                            helper: false,
                        });
                    }
                }.bind(this)
            );
        },
        close() {
            return super.close(...arguments);
        },
        _extending() {
            var dialog = this.$modal.find(".modal-dialog");
            dialog.addClass("dialog_full_screen");
            dialog.find(".dialog_button_extend").hide();
            dialog.find(".dialog_button_restore").show();
            Promise.resolve();
        },

        _restore() {
            var dialog = this.$modal.find(".modal-dialog");
            dialog.removeClass("dialog_full_screen");
            dialog.find(".dialog_button_restore").hide();
            dialog.find(".dialog_button_extend").show();
            Promise.resolve();
        },
    });

