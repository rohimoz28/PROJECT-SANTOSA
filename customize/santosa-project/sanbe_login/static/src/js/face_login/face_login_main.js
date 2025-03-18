/** @odoo-module **/

    import FaceLoginDialog  from "./face_login_dialog";
    import { debounce } from "@web/core/utils/timing";
    import LoginIDCard  from "../idcard/idcard";
    import dom from "@web/legacy/js/core/dom";
    let isgranted;
    let VideoStreams;
    let data;
    let state_read;
    let state_save;
    let state_render;
    let muka_photo;

    $(document).ready(function() {
            var stop;
            var voterId
            var face_recognition_enable;
            var face_recognition_store;
            var face_emotion;
            var face_gender;
            var face_age;
            var labels_ids;
            var images_ids = new Array;
            var user_name = new Array();
            var descriptions = new Array();
            var labeledFaceDescriptors;
            var timer_scan;
            var descriptor_ids;
            var loadingawal;


            const imgSize = 800; // maximum image size in pixels
            const minScore = 0.9; // minimum score
            const maxResults = 10; // maximum number of results to return
            const height = 560;
            const width = 720;

             $('#face_rec').on("click", function(){
               debounce(start_recognition(), 500);
            });
             $('#login-methode').on('change', function() {
                var nilai = $(this).find(":selected").val();
                if((nilai ==='face_login') ||(nilai ==='idcard_login')) {
                   $('.field-login').css('opacity','0');
                   $('.field-password').css('opacity','0');//.css('display','none');
                   $('#login').removeAttr('required');
//                   $('#login').attr('required','required');
                   $('#password').removeAttr('required');
//                   $('#password').attr('required','required');
                   $('#captcha').css('opacity','0');
                   $('#captcha').removeAttr('required');
//                   $('#captcha').attr('required','required');
                }else{
                   $('.field-login').css('opacity','1');//.show();//.css('display','none');
                   $('.field-password').css('opacity','1');
                   $('#login').prop('required',true);
                   $('#password').prop('required',true);
                   $('#captcha').css('opacity','1');
                   $('#captcha').prop('required',true);
                }
            });
            $('form').submit(function(event) {
                    var self = $(this);
                    state_read = $.Deferred();
                    state_save = $.Deferred();
                    state_render = $.Deferred();
                    var loginmethode = $("#login-methode").val();
                    if (loginmethode === "face_login") {
                         if ($('#IsGrantedFace').is(":checked")){
                           return true;
                         } else{
                             event.stopPropagation();
                             event.preventDefault();
                             stop = false;
                             loadingawal = load_models();
                             $("#face_rec").click();
                             return false;
                         }
                    } else if (loginmethode === "idcard_login") {
                             event.stopPropagation();
                             event.preventDefault();
                             start_idcard()
                    }
                    else{
                        var recaptcha = $("#g-recaptcha-response").val();
                        if (recaptcha !== undefined) {
                             event.stopPropagation();
                             event.preventDefault();
                             if (recaptcha === ""){
                                document.getElementById('err').innerHTML="Please verify Captcha";

                             } else{
                                return true;
                             }
//                            document.getElementById('err').innerHTML="Please verify Captcha";
                        }
                        else{
                            return true;
                        }
                    }
             });
           function start_idcard(){
                const Loaddata = new LoginIDCard().open_scan_dialog();
           }
           function start_recognition(){
                var self = $(this);
                var LoadData = $.ajax({
                    type: 'POST',
                    url: window.location.origin +"/init_login",
                    dataType: 'json',
                    beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                    data: JSON.stringify({jsonrpc: '2.0'}),
                    success: function(data) {
                        var result = data.result;
                        face_recognition_enable = result['face_recognition_enable'];
                        face_recognition_store = result['face_recognition_store'];
                        face_emotion = result['face_emotion'];
                        face_gender = result['face_gender'];
                        face_age = result['face_age'];
                        labels_ids = result['labels_ids'];
                        images_ids =result['images_ids'];
                        user_name.push(result['user_name']) ;
                        var age_map =  {
                            '20':'0-20',
                            '30': '20-30',
                            '40': '30-40',
                            '50': '40-50',
                            '60': '50-60',
                            '70': '60-any',
                            'any': 'any-any'}
                        if (data.face_age === 'any')
                            face_age = 'any-any';
                        else
                            face_age = age_map[Math.ceil(result.face_age).toString()];
                         if (labels_ids === undefined){
                            muka_photo = false;
                         } else {
                             muka_photo = true;
                         }

                         state_save.resolve();
                    }
                });
                return $.when(LoadData).then(
                result =>{
                    loadingawal.then(
                    result =>{
                    state_save.then(
                        result =>{
                            if (muka_photo === true)
                                new FaceLoginDialog(self,  {
                                    labels_ids: labels_ids,
                                    face_age: face_age,
                                    images_ids:images_ids,
                                    user_name:user_name,
                                    muka_photo: muka_photo,
                                    face_recognition_mode: 'login',
                                }).open({shouldFocusButtons:true});

//                            else
//                                Swal({
//                                title: 'No one images/photos uploaded',
//                                  text: "Please go to your profile and upload 1 photo",
//                                  icon: 'error',
//                                  confirmButtonColor: '#3085d6',
//                                  confirmButtonText: 'Ok'
//                                });
                    })
                    })
                })
           }
           async  function load_models(){
                let models_path = '/sanbe_login/static/src/models'
                /****Loading the model ****/
                return Promise.all([
                  await faceapi.nets.tinyFaceDetector.loadFromUri(models_path),
                  await faceapi.nets.faceLandmark68Net.loadFromUri(models_path),
                  await faceapi.nets.faceRecognitionNet.loadFromUri(models_path),
                  await faceapi.nets.faceExpressionNet.loadFromUri(models_path),
                  await faceapi.nets.ageGenderNet.loadFromUri(models_path),
                  await faceapi.nets.ssdMobilenetv1.loadFromUri(models_path)
                ])
               .then((val) => {
                    console.log('loading model' + val)
                }).catch((err) => {
                    console.log('Error Loading Model'+ err)
                })
            }
    });