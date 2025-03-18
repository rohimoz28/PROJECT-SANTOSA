/** @odoo-module **/

import {App, whenReady, Component, useState} from "@odoo/owl";
import Dialog from "@web/legacy/js/core/dialog";
import { _t } from "@web/core/l10n/translation";
import { utils } from "@web/core/ui/ui_service";
import { cookie } from "@web/core/browser/cookie";
import { isBrowserChrome, isMobileOS } from "@web/core/browser/feature_detection";


var WEB_CAMERA_QRCODE_WIDGET_COOKIE = 'web_camera_qrcode_widget_default_camera';
var audio = new Audio('/sanbe_login/static/audio/beep.mp3');
var DialogIDCard = Dialog.extend({
        template: 'QRCode.camera',
         xmlDependencies: [
         '/sanbe_login/static/src/xml/barcode_dialog.xml',
                  '/web/static/src/xml/dialog.xml'
         ],
         init: function (parent, options) {
            this._super(parent, options);
            this.browserType = _t("PC browser");
         },
});

class LoginIDCard extends Component{
        checkBrowserType() {
            var self = this;
            if (isMobileOS) {
                this.browserType = _t("Mobile browser");
            } else {
                this.browserType = _t("PC browser");
            }

        }
        displayNotification(text){
            this.notification.add(text, { type: "danger" });
        }
        async ImageCapture() {
            var self =this;
            var canvas = document.querySelector("#canvas");
            var video = document.querySelector("#scancode-video");
            canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
            var image_data_url = canvas.toDataURL();
            image_data_url=image_data_url.replace(/^data:image\/\w+;base64,/, "");
            self.datafoto= image_data_url

        }

        open_scan_dialog() {
            var self = this;
            $("button[class*='o_show_camera_button']").prop('disabled', true);
            $(".loading").removeClass("o_hidden");
            self.checkBrowserType();
             var dialog_title = this.browserType + ": " + _t("Login With QRCode/BarCode");
            this.dialog = new DialogIDCard(self, {
                size: 'large',
                dialogClass: 'o_act_window',
                title: dialog_title,
                buttons: self.getButtons(),
                renderHeader: false,
                click: function () {
                    self.closeDialog();
                }
            });
            this.dialog.opened().then(function (res) {
                self.initScanDialog();
            });
            self.dialog.open();
        }
       initScanDialog() {
            var self = this;

            this.modal_body = this.dialog.$modal.find(".modal-body");
            this.scan_result_value = this.modal_body.find(".scan_result_value")[0];

            this.dialog.$modal.find("footer").css({
                "padding": "4px 16px"
            });

            this.footer_last_button = this.dialog.$modal.find("footer").find("button:last");
            self.footer_last_button.after("<span class='scan_info text-right font-weight-bold' style='flex:1;'></span>");
            this.scan_info = this.dialog.$modal.find("footer").find(".scan_info");
            this.initWebScanner();
        }
        initWebScanner() {
            var self = this;
            var header_button = this.dialog.$modal.find("header").find("button");
            header_button.click(function () {
                self.closeDialog();
            });

            var camera_widget_options_panel = this.dialog.$modal.find("#camera_widget_options");

            var options_button = this.modal_body.find(".show_or_hide_options_panel");
            var options_button_icon = options_button.find("i");
            var options_button_text = options_button.find("span");

            $(camera_widget_options_panel).on('show.bs.collapse', function () {
                options_button_icon.addClass("fa-angle-double-up").removeClass("fa-angle-double-down");
                options_button_text.html(_t("Hide"));
            })
            $(camera_widget_options_panel).on('hide.bs.collapse', function () {
                options_button_icon.addClass("fa-angle-double-down").removeClass("fa-angle-double-up");
                options_button_text.html(_t("Show"));
            })

            if (this.getCameraCookie() == "") {
                self.vertical = false;
                self.horizontal = false;
            } else {
                if(this.getCameraCookie() !== undefined){
                    self.vertical = JSON.parse(this.getCameraCookie())["vertical"];
                    self.horizontal = JSON.parse(this.getCameraCookie())["horizontal"];
                }
            }


            this.flip_vertical_checkbox = self.modal_body.find("#flip_vertical");
            $(self.flip_vertical_checkbox).change(function () {
                self.vertical = self.flip_vertical_checkbox.prop("checked");
                self.set_flip();
                self.setDefaultCookie();
            });
            this.flip_horizontal_checkbox = self.modal_body.find("#flip_horizontal");
            $(self.flip_horizontal_checkbox).change(function () {
                self.horizontal = self.flip_horizontal_checkbox.prop("checked");
                self.set_flip();
                self.setDefaultCookie();
            });
            self.set_flip();

            this.scan_info.text(_t("The camera is being initialized. . .")).addClass("text-info").removeClass("text-danger").removeClass("text-success");

            self.initCodeReader();
        }
        set_flip() {
            var self = this;

            if (self.horizontal && self.vertical) {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-flip-both");
            } else if (self.horizontal) {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-flip-horizontal");
            } else if (self.vertical) {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-flip-vertically");
            } else {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-no-flip");
            }
        }
        getButtons() {
            var self = this;
            var buttons = [];
            buttons = [{
                    text: _t("Cancel"),
                    classes: 'btn-dark',
                    close: true,
                    click: function () {
                        self.closeDialog();
                    }
                }]

            return buttons;
        }
        updateResult(hasilScan) {
            var self = this;
            var LoadData = $.ajax({
                type: 'GET',
                url: window.location.origin +"/get_login_idcard",
                data: {
                    'idcard': hasilScan
                },
                success: function(data) {
                    if (data==='success'){
                         console.log('data hasil ', data)
                         $('.oe_login_form').submit();
                    }else {
                        alert('Wrong ID Cards')
                    }
                }
            });
        }
        closeDialog() {
            var self = this;
            if (self.codeReader) {
                self.stopCodeReader();
            }
            $(".loading").addClass("o_hidden");
            $("button[class*='o_show_camera_button']").prop('disabled', false);
            this.dialog.$modal.modal('hide');
        }

        initCodeReader() {
            this.camera_source = this.modal_body.find(".camera-select");
            this.start_button = this.modal_body.find(".scancode_start");
            this.stop_button = this.modal_body.find(".scancode_stop");
            this.show_options_button = this.modal_body.find(".show_or_hide_options_panel");
            this.scannerLaser = this.modal_body.find(".scanner-laser");

            var self = this;
            self.scannerLaser.addClass("o_hidden");
            this.codeReader = new ZXing.BrowserMultiFormatReader();

            self.codeReader.listVideoInputDevices()
                .then((videoInputDevices) => {
                    if (videoInputDevices.length >= 1) {
                        self.start_button.click(function () {
                            self.startCodeReader();
                        });
                        self.stop_button.click(function () {
                            self.stopCodeReader();
                        });
                        this.localDevices = videoInputDevices;
                        if (self.getCameraCookie() === undefined || self.getCameraCookie() === null || self.getCameraCookie() === "") {
                            if (videoInputDevices.length > 1) {
                                self.defaultCameraId = videoInputDevices[1].deviceId;
                                self.defaultCameraName = videoInputDevices[1].label;
                            } else {
                                self.defaultCameraId = videoInputDevices[0].deviceId;
                                self.defaultCameraName = videoInputDevices[0].label;
                            }
                            self.vertical = false;
                            self.horizontal = false;

                            self.setDefaultCookie();
                        } else {
                            self.flip_vertical_checkbox.prop("checked", self.vertical);
                            self.flip_horizontal_checkbox.prop("checked", self.horizontal);
                            if (!self.cookieDefaultIsExistInLocalDevices()) {
                                self.defaultCameraId = videoInputDevices[0].deviceId;
                                self.defaultCameraName = videoInputDevices[0].label;
                                self.setDefaultCookie();
                            } else {
                                self.defaultCameraId = JSON.parse(self.getCameraCookie())["defaultCamera"]["id"];
                            }
                            videoInputDevices.forEach((element) => {
                                var option;
                                if (element.deviceId === self.defaultCameraId) {
                                    option = new Option(element.label, element.deviceId, true, true);
                                } else {
                                    option = new Option(element.label, element.deviceId);
                                }
                                self.camera_source.append(option);
                            })
                            self.camera_source.change(function () {
                                self.defaultCameraId = $(this).children('option:selected').val();
                                self.defaultCameraName = $(this).children('option:selected').text();
                                self.setDefaultCookie();
                                self.toggleCodeReader();
                            });
                        }

                        this.scan_info.text(_t("The camera is initialized successfully!")).addClass("text-info").removeClass("text-danger").removeClass("text-success");
                        if (self.autoplay) {
                            self.start_button.prop('disabled', true);
                            self.stop_button.prop('disabled', false);

                            self.startCodeReader();
                        } else {
                            self.start_button.prop('disabled', false);
                            self.stop_button.prop('disabled', true);
                            self.scan_info.text(_("The camera has not started yet. Please click the start button.")).addClass("text-warning").removeClass("text-info").removeClass("text-success");
                        }
                    } else {
                        self.scan_info.text(_t("Startup failed: no cameras were found.")).removeClass("text-info").addClass("text-danger").removeClass("text-success");
                        self.scannerLaser.addClass("o_hidden");
                        self.camera_source.prop('disabled', true);
                        self.start_button.prop('disabled', true);
                        self.stop_button.prop('disabled', true);
                    }
                })
                .catch(function (err) {
                    if (err.TypeError === undefined) {
                        self.scan_info.text(_t("Startup failed: no cameras were found.")).removeClass("text-info").addClass("text-danger").removeClass("text-success");
                    }
                });
        }
        startCodeReader() {
            var self = this;
            self.scan_info.text(_t("Start camera...")).addClass("text-info").removeClass("text-danger").removeClass("text-success");

            self.codeReader.decodeFromVideoDevice(self.defaultCameraId, 'scancode-video', (result, err) => {

                self.start_button.prop('disabled', true);
                self.stop_button.prop('disabled', false);
                self.camera_source.prop('disabled', false);
                self.scannerLaser.removeClass("o_hidden");

                if (result) {
                    audio.play();
                    self.scan_result_value.textContent = result.text;
                    self.scanResult = result.text;

                    self.scan_info.text(_t("Scan the code successfully, Format:") + self.getZXingFormat(result.format)).addClass("text-success").removeClass("text-danger").removeClass("text-warning");


                    self.scannerLaser.fadeOut(0.5);
                    setTimeout(function () {
                        self.scannerLaser.fadeIn(0.5);
                    });
                    self.ImageCapture();
                    self.updateResult( result.text);
                }
                if (err && !(err instanceof ZXing.NotFoundException)) {
                    self.scan_result_value.textContent = err;

                    self.scan_info.text(_t("Startup failed:" + err)).removeClass("text-info").addClass("text-danger").removeClass("text-success");
                    self.scannerLaser.addClass("o_hidden");
                }
            });
            self.scan_info.text(_t("Started successfully. Please scan the code...")).removeClass("text-info").removeClass("text-danger").removeClass("text-warning").addClass("text-success");
        }
        stopCodeReader() {
            var self = this;
            self.codeReader.reset();
            self.scan_result_value.textContent = '';
            self.scannerLaser.hide();

            self.start_button.prop('disabled', false);
            self.scan_info.text("The camera stops working.").addClass("text-warning").removeClass("text-info").removeClass("text-success");
        }
        toggleCodeReader() {
            var self = this;
            self.stopCodeReader();
            self.startCodeReader();
        }

        getZXingFormat (value) {
            switch (value) {
                case 0:
                    return "AZTEC";
                    break;
                case 1:
                    return "CODABAR";
                    break;
                case 2:
                    return "CODE_39";
                    break;
                case 3:
                    return "CODE_93";
                    break;
                case 4:
                    return "CODE_128";
                    break;
                case 5:
                    return "DATA_MATRIX";
                    break;
                case 6:
                    return "PDF_417";
                    break;
                case 7:
                    return "EAN_13";
                    break;
                case 8:
                    return "ITF";
                    break;
                case 9:
                    return "MAXICODE";
                    break;
                case 10:
                    return "PDF_417";
                    break;
                case 11:
                    return "QR_CODE";
                    break;
                case 12:
                    return "RSS_14";
                    break;
                case 13:
                    return "RSS_EXPANDED";
                    break;
                case 14:
                    return "UPC_A";
                    break;
                case 15:
                    return "UPC_E";
                    break;
                case 16:
                    return "UPC_EAN_EXTENSION";
                    break;
                default:
                    return _("unknown");
            }
        }
        getCameraCookie() {
            return cookie.get(WEB_CAMERA_QRCODE_WIDGET_COOKIE);
        }
        setDefaultCookie() {
            this.devices = {
                "defaultCamera": {
                    "id": this.defaultCameraId,
                    "name": this.defaultCameraName,
                },
                "list": this.localDevices,
                "vertical": JSON.parse(this.vertical),
                "horizontal": JSON.parse(this.horizontal),
            }
            cookie.set(WEB_CAMERA_QRCODE_WIDGET_COOKIE, JSON.stringify(this.devices), 60 * 60 * 24 * 30); // 30 day cookie
        }
        cookieDefaultIsExistInLocalDevices() {
            var self = this;
            var list = JSON.parse(self.getCameraCookie())["list"];
            return JSON.stringify(list).indexOf(JSON.parse(self.getCameraCookie())["defaultCamera"]["id"]) !== -1;
        }
        _setValue() {
            var $input = this.$el.find('input');
            return this._super($input.val());
        }
}

export default LoginIDCard;