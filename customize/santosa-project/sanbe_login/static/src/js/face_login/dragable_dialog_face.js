/** @odoo-module **/

import Dialog from "@web/legacy/js/core/dialog";

    Dialog.include({
        open: function () {
            this._super.apply(this, arguments);
            return this._opened.then(function(){
              var titlenya =   $(".modal-title").text();
              var databaru ='<span class="btn btn-warning fa-lg float-center o_form_binary_file_web_cam"'+
                      'title="'+ titlenya + '"'+
                      'aria-label="'+ titlenya + '"'+
                      'style="border-radius: 10px !important; top:0;left:0;'+
                         'display: inline-block;'+
                         'width: 300px;'+
                          'height: 47px;'+
                      '">' +
                    '<span>'+
                        '<i class="fa fa-camera"/>'+
                    '</span>'+
                     titlenya + ' loading...'+
                '</span>';
                if ($(".modal-title").length ){
                $(".modal-title")[0].remove();
                }
                if($(".modal-header").length){
               $(".modal-header").append(databaru);
               }
                 $('.btn-close').css({"display":"none"});
                       // if (muka_photo){
                       if( $(".o_form_binary_file_web_cam").length){
                            $(".o_form_binary_file_web_cam").removeClass('btn-warning');
                            $(".o_form_binary_file_web_cam").addClass('btn-success');
                            }
//                        }else{
//                            $(".o_form_binary_file_web_cam").removeClass('btn-warning');
//                            $(".o_form_binary_file_web_cam").addClass('btn-danger');

                       // }
                        $(".o_form_binary_file_web_cam").text(titlenya);
            });
            return this;
        },

    });