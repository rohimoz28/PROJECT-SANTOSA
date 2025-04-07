/** @odoo-module **/
// model for patch the imageField and add function for image preview
import { ImageField } from '@web/views/fields/image/image_field';
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { CharField } from "@web/views/fields/char/char_field"
patch(CharField.prototype,{
    parse(value) {
        console.log('ini parse')
        this.props.records.model.root.save({})
        if (this.shouldTrim) {
            return value.trim();
        }
        return value;
    }
});