$(document).ready(function() {
    $('.oe_reset_password_form').each(function(ev) {
        var oe_website_login_container = this;
        $(oe_website_login_container).on('click', 'div.input-group-append button.btn.btn-secondary', function() {
            console.log('jalan ga sih ');
            var icon = $(this).find('i.fa.fa-eye').length
            if (icon == 1) {
                console.log('ini liat');
                $(this).find('i.fa.fa-eye').removeClass('fa-eye').addClass('fa-eye-slash');
                $(this).parent().prev('input[type="password"]').prop('type', 'text');
            } else {
             console.log('ini liat 2')
                $(this).find('i.fa.fa-eye-slash').removeClass('fa-eye-slash').addClass('fa-eye');
                $(this).parent().prev('input[type="text"]').prop('type', 'password');
            }
        });
        $(oe_website_login_container).on('click', 'div.input-group-append2 button.btn.btn-secondary', function() {
            var icon = $(this).find('i.fa.fa-eye').length
            if (icon == 1) {
                $(this).find('i.fa.fa-eye').removeClass('fa-eye').addClass('fa-eye-slash');
                $(this).parent().prev('input[type="password"]').prop('type', 'text');
            } else {
                $(this).find('i.fa.fa-eye-slash').removeClass('fa-eye-slash').addClass('fa-eye');
                $(this).parent().prev('input[type="text"]').prop('type', 'password');
            }
        });
    });

});
