/*
*     Author   => Albertus Restiyanto Pramayudha
*     email    => xabre0010@gmail.com
*     linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
*     youtube  => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*/
    var isgranted;
    var VideoStreams;
    var CanvasVideo;
    var canvascontext;
    var data;
    var state_read;
    var state_save;
    var state_render;
    //const FaceDialog = require('yudha_face_login.my_dialog').YudhaLoginFace;
    const ajax = require('web.ajax');
    var core = require('web.core');
    var dom = require('web.dom');

    $(document).ready(function() {


    //        const loginselect = $('#login-methode')[0];//document.getElementById('login-methode');
    //        const buttonface = $('#face_rec')[0];
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
    //        buttonface.addEventListener('click', _.debounce(function() {
    //                        start_recognition();
    //         }, 250, true));

             $('#face_rec').on("click", _.debounce(function() {
                            start_recognition();
             }, 250, true));
    //console.log('login select '+loginselect)
    //        loginselect.addEventListener('change', function() {
             $('#login-methode').on('change', function() {
                var nilai = $(this).find(":selected").val();
                if(nilai ==='face_login') {
                   $('.field-login').css('opacity','0');
                   $('.field-password').css('opacity','0');//.css('display','none');
                   $('#login').attr('required','required');
                   $('#password').attr('required','required');
                }else{
                   $('.field-login').css('opacity','1');//.show();//.css('display','none');
                   $('.field-password').css('opacity','1');
                   $('#login').removeAttr("required");
                   $('#password').removeAttr("required");
                }
            });
            $('form').submit(function(event) {
                    var self = $(this);
                    state_read = $.Deferred();
                    state_save = $.Deferred();
                    state_render = $.Deferred();
                    var loginmethode = $("#login-methode").val();
                    alert('login methode '+ loginmethode)
                    if (loginmethode === "face_login") {
                         stop = false;
                         event.preventDefault();
                         loadingawal = load_models();
                         $("#face_rec").click();
//                         start_recognition();
                         return false;
                    }
                    else{
                        var recaptcha = $("#g-recaptcha-response").val();
                        if (recaptcha === "" || recaptcha === undefined) {
                            event.preventDefault();
                            document.getElementById('err').innerHTML="Please verify Captcha";
                        } else{
                            return true;
                        }
                    }
             });

           function start_recognition(){
                var self = $(this);
                var LoadData = ajax.jsonRpc("/init_login", 'call', {}, {
                    'async': false
                 }).then(function (data) {
                    var result = data;
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
                     muka_photo = true;
                     state_save.resolve();
                 });

                //parse_data_face_recognition();
                return $.when(LoadData).then(
                result =>{
                    loadingawal.then(
                    result =>{
                    state_save.then(
                        result =>{
                            console.log("models success loaded "+ muka_photo);
                            if (muka_photo)
                                new FaceDialog(self, {
                                    labels_ids: labels_ids,
                                    face_age: face_age,
                                    images_ids:images_ids,
                                    user_name:user_name,
                                    muka_photo: muka_photo,
                                    face_recognition_mode: 'login',
                                }).open();

                            else
                                Swal.fire({
                                title: 'No one images/photos uploaded',
                                  text: "Please go to your profile and upload 1 photo",
                                  icon: 'error',
                                  confirmButtonColor: '#3085d6',
                                  confirmButtonText: 'Ok'
                                });
                    })
                    })
                })
           }
           async  function load_models(){
                let models_path = '/yudha_face_login/static/src/models'
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