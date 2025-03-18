/** @odoo-module **/
import { browser } from "@web/core/browser/browser";
$(document).ready(function() {
        const savelogin = browser.localStorage.getItem("sanbe.isSaveUser");
        let loginuser;
        let password;
        if ((savelogin !==null)  || (savelogin !== false)){
                loginuser = browser.localStorage.getItem("sanbe.login");
                password = browser.localStorage.getItem("sanbe.password");
                $('#flexCheckDefault').attr('checked', 'checked');
                $('#password').val(password);
                $('#login').val(loginuser);
        } else {
                $('#flexCheckDefault').removeAttr('checked');
                $('#password').val('');
                $('#login').val('');
        }
        loginuser = browser.localStorage.getItem("sanbe.login");
        password = browser.localStorage.getItem("sanbe.password");
        $('#flexCheckDefault').click(function () {

            if ($('#flexCheckDefault').is(':checked')) {
                 browser.localStorage.setItem('sanbe.isSaveUser', true);
                 $('#flexCheckDefault').attr('checked', 'checked');
                 $('#password').val(password);
                 $('#login').val(loginuser);
            } else {
                 browser.localStorage.setItem('sanbe.isSaveUser', false);
                 $('#password').val('');
                 $('#login').val('');
            }
        });
        $('form').submit(function(event) {
            if ($('#flexCheckDefault').is(':checked')) {
                browser.localStorage.setItem('sanbe.login', $('#login').val());
                 browser.localStorage.setItem('sanbe.password', $('#password').val());
                 browser.localStorage.setItem('sanbe.isSaveUser', true);
             } else {
                 browser.localStorage.setItem('sanbe.login', '');
                 browser.localStorage.setItem('sanbe.password', '');
                 browser.localStorage.setItem('sanbe.isSaveUser', false);

             }
        });
    });