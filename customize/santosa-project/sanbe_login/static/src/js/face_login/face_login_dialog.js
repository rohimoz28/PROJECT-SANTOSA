/** @odoo-module **/
import Dialog from "@web/legacy/js/core/dialog";
import { _t } from "@web/core/l10n/translation";
import { useChildRef } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { Component } from "@odoo/owl";
import dom from "@web/legacy/js/core/dom";
import Widget from "@web/legacy/js/core/widget";
import { useDebounced } from "@web/core/utils/timing";
const heights = 560;
const widths = 720;
const minScore = 0.9;
const maxResults = 5;
const inputSize = 408
const scoreThreshold = 0.5
let isgranted;
let CanvasVideo;
let canvascontext;

 var FaceLoginDialog = Dialog.extend({
        template: 'YudhaFaceDialogVideoLegacy',
         xmlDependencies: [
         '/sanbe_login/static/src/xml/face_login_dialog.xml',
                  '/web/static/src/xml/dialog.xml'
         ],
         muka_photo: false,
         handlescanner: 0,
         handletimeout: 0,
         init: function (parent, options) {
            this.promise_face_recognition = this.load_models();
            options.fullscreen = true;
            options.dialogClass = options.dialogClass || '' + ' o_act_window';
            options.size = 'large';
            options.title =  _t("Login Face Recognizer");
            this.state_read = $.Deferred();
            this.state_save = $.Deferred();
            this.state_render = $.Deferred();
            this.labels_ids = options.labels_ids;
            this.descriptor_ids = options.descriptor_ids;
            this.face_age = options.face_age;
            this.images_ids = options.images_ids;
            this.user_name = options.user_name || [];
            this.parent = parent;
            this._super(parent, options);
         },
        load_models: function(){
            let models_path = '/sanbe_login/static/src/models'
            return Promise.all([
              faceapi.nets.tinyFaceDetector.loadFromUri(models_path),
              faceapi.nets.faceLandmark68Net.loadFromUri(models_path),
              faceapi.nets.faceRecognitionNet.loadFromUri(models_path),
              faceapi.nets.faceExpressionNet.loadFromUri(models_path),
              faceapi.nets.ageGenderNet.loadFromUri(models_path)
            ]);
        },
        start: function () {
            var self = this;

            this.handlescanner =0;
            this.handletimeout =0;
                self.width = document.body.scrollWidth;
                self.height = document.body.scrollHeight;
                var constraints =
                {
                        facingMode:  "user",
                        width: { min: 1280, ideal: 2880, max: 2880 },
                        height: { min: 720 , ideal: 1800, max: 1800 },
                        frameRate: {
                              min: 24,
                              ideal: 30,
                              max: 30,
                        },
                        advanced: [
                             { sharpness: true },
                             {focusMode: "manual"},
                             {focusDistance: { min: 0.05, ideal: 0.45, max: 0.7 }},
                        ],
                };
                let configstrain = {
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
                Webcam.set({
                    width: self.width,
                    dest_width: self.width,
                    height: self.height,
                    dest_height: self.height,
                    image_format: 'jpeg',
                    jpeg_quality: 100,
                    force_flash: false,
                    fps: 30,
                    swfURL: '/sanbe_login/static/src/lib/webcamjs/webcam.swf',
                    constraints: configstrain,
                });
                Webcam.attach(this.$('#live_webcam')[0]);
            return this._super.apply(this, arguments).then(function () {
                            Webcam.on('live', function() {
                                $('#face_video').css('width','100%');
                                $('#face_video').css('height','100%');
                                $('#face_video').css('filter',' brightness(135%) contrast(120%)  blur(0px)  opacity(140%)');
                                $('#face_video').css('-webkitTransform','scaleX(-1)');
                                $('#face_video').css('transform','scaleX(-1)');
                                $('#face_video').css('display','block');
                                $('#live_webcam').css('width','100%');
                                $('#live_webcam').css('height','100%');
                                self.start_awal();
                            });


            });

        },

        start_awal: async function(){
                    var self = this;
                    const cekcanvas = document.getElementById('face_canvas');
                    if(cekcanvas) cekcanvas.remove();
                    CanvasVideo = faceapi.createCanvasFromMedia(VideoStreams);
                    CanvasVideo.id = 'face_canvas'
                    $(CanvasVideo).css('left', '16px');
                    $(CanvasVideo).css('position', 'absolute');
                    $(VideoStreams).css('float', 'left');
                    let container = document.getElementById("live_webcam");
                    container.append(CanvasVideo);
                    const displaySize = { width: VideoStreams.clientWidth, height: VideoStreams.clientHeight };
                    faceapi.matchDimensions(CanvasVideo, displaySize);
                    const labeledFaceDescriptors = await this.loadLabeledImages();
                    const maxDescriptorDistance = 0.7;
                    const faceMatcher = new faceapi.FaceMatcher(labeledFaceDescriptors, maxDescriptorDistance)
                    self.startrecog(VideoStreams,CanvasVideo,displaySize,faceMatcher);
        },
        loginkan: function(canvas, user) {
           var self = this;



        },
        startrecog: async function(video, canvas,displaySize,faceMatcher){
                var self = this;
                let predictedAges = [];
                const optionsface = new faceapi.TinyFaceDetectorOptions({ inputSize: 320 })
                const detections =  await faceapi
                .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceExpressions()
                .withAgeAndGender()
                .withFaceDescriptor();
                if(detections){
                    const resizedDetections = faceapi.resizeResults(detections, displaySize);
                    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
                    faceapi.draw.drawDetections(canvas, resizedDetections)
                    faceapi.draw.drawFaceLandmarks(canvas, resizedDetections)
                    faceapi.draw.drawFaceExpressions(canvas, resizedDetections)
                    if (resizedDetections && Object.keys(resizedDetections).length > 0) {
                      const age = resizedDetections.age;
                      const interpolatedAge = this.interpolateAgePredictions(age, predictedAges);
                      const gender = resizedDetections.gender;
                      const expressions = resizedDetections.expressions;
                      const maxValue = Math.max(...Object.values(expressions));
                      const emotion = Object.keys(expressions).filter(
                        item => expressions[item] === maxValue
                      );
                        const results = faceMatcher.findBestMatch(detections.descriptor);
                        if (results){
                        const box = resizedDetections.detection.box;
                        const textLabel = results.toString();
                        const text = [
                              `name - ${textLabel}`,
                              `Age - ${interpolatedAge} years`,
                              `Gender - ${gender}`,
                              `Emotion - ${emotion[0]}`
                        ]
                        const namalogin1 = textLabel.toString().replace("0)", "");
                        const namalogin = namalogin1.toString().replace("(","");
                        const anchor = { x: 190, y: 190 }
                        const drawOptions = {
                          anchorPosition: 'TOP_LEFT',
                          backgroundColor: 'rgba(0, 0, 0, 0.5)'
                        }
                        const drawBox = new faceapi.draw.DrawTextField(text, anchor, drawOptions)
                        drawBox.draw(canvas);

                        if (textLabel.indexOf('unknown') === -1){
                            isgranted = true;
                            clearInterval(this.handlescanner)
                            $('#IsGrantedFace').attr('checked','checked')
                            var LoadData = $.ajax({
                                type: 'GET',
                                url: window.location.origin +"/get_login_info",
                                data: {
                                    'auth_token': namalogin
                                },
                                success: function(data) {
                                    $('#login').val(namalogin)
                                    $('#password').val(data);
                                    $('.oe_login_form').submit();
                                    self.close();
                                }
                            });

                            return true
                        }
                       }
                    }
                }
                await this.sleep(20);
                this.startrecog(video, canvas,displaySize,faceMatcher);
        },
        interpolateAgePredictions: function(age, predictedAges) {
            predictedAges = [age].concat(predictedAges).slice(0, 30);
            const avgPredictedAge = predictedAges.reduce((total, a) => total + a) / predictedAges.length;
            return avgPredictedAge;
        },
        sleep: function(ms) {
          return new Promise(resolve => setTimeout(resolve, ms));
        },
       loadLabeledImages: async function() {
          var self = this;
          const Labels = [this.user_name];
          return Promise.all(
              self.labels_ids.map(async (label,i) =>  {
              const descriptions = [];
              for(var j in self.images_ids) {
                     var data_foto = self.images_ids[j];
                     var src = 'data:image/jpeg;base64,'+ data_foto ;
                     const image_foto = await self.loadImagelabel(src);
                     const predicts = await faceapi
                     .detectSingleFace(image_foto)
                     .withFaceLandmarks()
                     .withFaceDescriptor();
                      if (predicts) {
                                descriptions.push(predicts.descriptor);
                      }
               }
               return new  faceapi.LabeledFaceDescriptors(label,descriptions);
        }));
       },
       loadImagelabel: async function(srcdata) {
          const image = new Image();
          image.crossOrigin = true;
          return new Promise((resolve, reject) => {
            image.addEventListener('error', (error) => reject(error));
            image.addEventListener('load', () => resolve(image));
            image.src = srcdata;
          });
        },
       destroy: function () {
            if ($('.modal-footer .btn-primary').length)
                $('.modal-footer .btn-primary')[0].click();
            this.stop = true;
            if(self.handlescanner !==0) {
               clearInterval(this.handlescanner);
               this.handlescanner = 0;
            }
            if(this.handletimeout !== 0){
              clearTimeout(this.handletimeout);
              this.handletimeout = 0;
           }
            Webcam.off('live');
            Webcam.reset();
            this._super.apply(this, arguments);
       },

       close: function () {

           this.destroy();
       },
   });

export default FaceLoginDialog;