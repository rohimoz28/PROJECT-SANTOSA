/** @odoo-module **/
// model for patch the imageField and add function for image preview
import { ImageField } from '@web/views/fields/image/image_field';
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { Component, xml, useRef, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import WebcamDialog from '@sanbe_login/js/webcam_widget/webcam_component';


patch(ImageField.prototype, {
    async setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");

    },
    _tampilWebcam(ev){
        ev.stopPropagation();
        ev.preventDefault();
        this.dialogService.add(WebcamDialog, {
            tittle: 'Image WebCam',
            mode: true,
            onWebcamCallback: (data) => this.onWebcamCallback(data),
        });
    },

    async onWebcamCallback(base64) {
        this.onFileUploaded(base64);
//        this.props.record.data[this.props.name] = base64;
    }

});

