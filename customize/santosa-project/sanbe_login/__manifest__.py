# -*- coding: utf-8 -*-
{
    'name': "Sanbe Customize Login Page",

    'summary': "Sanbe Customize Login Page",

    'description': """
    This module offers users the ability to personalize their login experience by uploading background images or selecting background color schemes. This feature enhances visual appeal, fosters brand consistency, and creates a user-friendly authentication environment. Users can preview 
    real-time changes and align the login page with their aesthetic preferences or organizational branding.
    """,

    'author': "Albertus Restiyanto Pramayudha",
    'website': "http://www.yourcompany.com",
    "support": "xabre0010@gmail.com",
    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'USD',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup', 'web', 'auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/login_image.xml',
        'views/left_login_template.xml',
        'views/right_login_template.xml',
        'views/middle_login_template.xml',
        'reports/reports_qrcodes.xml',
        'reports/report_id_cards.xml',
        'views/res_users.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/sanbe_login/static/src/js/webcam_widget/webcam_component.js',
            '/sanbe_login/static/src/js/webcam_widget/image_webcam.js',
            '/sanbe_login/static/lib/webcamjs/webcamjs.js',
            '/sanbe_login/static/src/xml/image_webcam.xml',
            '/sanbe_login/static/src/xml/face_dialog.xml',
            '/sanbe_login/static/src/css/model_dialog.css',
        ],
        'web.assets_frontend': [
            '/sanbe_login/static/src/css/model_dialog.css',
            "/sanbe_login/static/src/js/remember_me.js",
            "/sanbe_login/static/src/js/show_password.js",
            "/sanbe_login/static/lib/face_api/face_apis.js",
            "/sanbe_login/static/src/js/face_login/face_login_main.js",
            "/sanbe_login/static/lib/webcamjs/webcamjs.js",
            "/sanbe_login/static/src/js/face_login/face_login_dialog.js",
            "/sanbe_login/static/src/xml/face_login_dialog.xml",
            "/sanbe_login/static/src/js/face_login/dragable_dialog_face.js",
            "/sanbe_login/static/src/js/auth_signup_show_password.js",
            "/sanbe_login/static/src/js/check_confirm_password.js",
            "/sanbe_login/static/src/css/login_button.css",
            "/sanbe_login/static/src/css/overlay_panel.css",
            "/sanbe_login/static/lib/animate/animate.css",
            "/sanbe_login/static/src/scss/show_password.scss",
            "/sanbe_login/static/src/scss/dropdownlogin.scss",
            "/sanbe_login/static/lib/zXing/ZXing.js",
            "/sanbe_login/static/src/js/idcard/idcard.js",
            "/sanbe_login/static/src/xml/barcode_dialog.xml",
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/banner.png"],
}

