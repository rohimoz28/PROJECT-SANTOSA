/*
*     Author   => Albertus Restiyanto Pramayudha
*     email    => xabre0010@gmail.com
*     linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
*     youtube  => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*/
odoo.define('yudha_face_login.dragdropimage', function (require) {
    "use strict";
    var FieldsImages = require('web.basic_fields').FieldBinaryImage;
    var FieldBin = require('web.basic_fields').AbstractFieldBinary;
//    Field.Bin.set_filename('testing');
     var FieldImageDragnDrop = FieldBin.include({
        events: _.extend({}, FieldBin.prototype.events, {
            'click .o_form_binary_file_web_cam': '_tampilWebcam',
        }),
        _tampilWebcam: function (ev) {
            ev.preventDefault();
            console.log('jalanlah ');
        }
    });
});

