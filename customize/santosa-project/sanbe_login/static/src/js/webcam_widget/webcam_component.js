/** @odoo-module **/
// model for patch the imageField and add function for image preview
import { Component, useRef, useState, onMounted } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { session } from '@web/session';


class WebcamDialog extends Component {
    async setup() {
        super.setup();
        this.state = useState({
            snapshot: ""
        });
        this.video = useRef("video");
        this.saveButton = useRef("saveButton");
        this.selectCamera = useRef("selectCamera");
        onMounted(() => this._mounted());
    }
    async _mounted() {
        await this.initSelectCamera();
        await this.startVideo();
        $('.save_close_btn').attr('disabled', 'disabled');

    }


    onChangeDevice(e) {
        const device = $(e.target).val();
        this.stopVideo()
        this.startVideo(device)
    }

    async initSelectCamera() {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices =devices;// devices.filter(device => device.kind === 'videoinput');
        videoDevices.map(videoDevice => {
            let opt = document.createElement('option');
            opt.value = videoDevice.deviceId;
            opt.innerHTML = videoDevice.label;
            this.selectCamera.el.append(opt);
            return opt;
        });

    }
    async startVideo(device = null) {
        var self = this;
        try {
            let config = {
                width: { ideal: session.am_webcam_width || 1280 },
                height: { ideal: session.am_webcam_height || 720 },
                    frameRate: {
                          min: 24,
                          ideal: 30,
                          max: 30,
                    },
                    advanced: [
                         { sharpness: true },
                    ],
            }
            if (device)
                config.deviceId = { exact: device }
            var mylive = $('#live_webcam')[0];
            Webcam.set({
                width: 788,
                height: 531,
                dest_width: 788,
                dest_height: 531,
                image_format: 'jpeg',
                jpeg_quality: 100,
                force_flash: false,
                fps: 645,
                swfURL: '/sanbe_login/static/src/lib/webcamjs/webcam.swf',
                constraints: config,
            });
            Webcam.attach(mylive);
            Webcam.on('live', function() {
                $('video').css('filter',' brightness(135%) contrast(120%)  blur(0px)  opacity(140%)');
                $('video').css('-webkitTransform','scaleX(-1)');
                $('video').css('transform','scaleX(-1)');
                self.video = document.getElementById('face_video');
            });

        } catch (e) {
            console.error('*** getUserMedia', e)
        } finally {
        }
    }
    stopVideo() {
        if (this.video.srcObject)
            this.video.srcObject.getTracks().forEach((track) => {
                track.stop();
            });
    }
    _onClickCancel(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this.stopVideo();
        this.props.close();
        Webcam.off('live');
        Webcam.reset();
    }
    takeSnapshot(video) {
        const canvas = document.createElement("canvas");
        canvas.width = video.clientWidth;
        canvas.height = video.clientHeight;
        const canvasContext = canvas.getContext("2d");
        canvasContext.drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg');
    }
    urltoFile(url, filename, mimeType) {
        return (fetch(url)
            .then(function (res) { return res.arrayBuffer(); })
            .then(function (buf) { return new File([buf], filename, { type: mimeType }); })
        );
    }


    async onwebcam(base64, mimetype) {
        let info = {'data': base64,
                    'name': 'test'}
        await this.props.onWebcamCallback(info);
    }

    _onWebcamSnapshot() {
        this.video = $('#face_video')[0]
        this.state.snapshot = this.takeSnapshot(this.video)
    }


    async _onWebcamSave(ev) {
        console.log('snapshot '+this.state.snapshot)
        if (!this.state.snapshot)
            return;

        await this.onwebcam(this.state.snapshot.split(',')[1], "image/jpeg");
        this._onClickCancel(ev);

    }
}
WebcamDialog.template = "WebCamDialog";
WebcamDialog.props = {
    contentClass: { type: String, optional: true },
    bodyClass: { type: String, optional: true },
    tittle: String,
    mode: { type: Boolean, optional: true },
    onWebcamCallback: { type: Function, optional: true },
    close: Function,
};
WebcamDialog.components = {
    Dialog,
};
WebcamDialog.defaultProps = {
    mode: false,
    onWebcamCallback: () => { },
};
export default WebcamDialog;