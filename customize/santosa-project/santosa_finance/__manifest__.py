# -*- coding: utf-8 -*-
{
    'name': "Santosa Finance",

    'summary': """
        Module Santosa Finance""",

    'description': """
        Manajemen Finance Santosa
    """,

    'author': "Febry Ramadhan",
    'website': "https::/sanbe.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','mail', 'report_xlsx', 'account','base_accounting_kit','base_account_budget','purchase','contacts','stock'],

		# Include ALL XML Code in Here be mindful of order
    'data': [
        # 'security/access_groups.xml',
        # 'security/record_rules.xml',
        'security/ir.model.access.csv',
        'security/access_group.xml',
        'views/menuitems.views.xml',
        'wizards/export_honor_dokter.xml',
        'report/report_xls.xml',
        'views/matrix_posting/matrix_posting_master.views.xml',
        'views/offset/offset_transaction_master.views.xml',
        'views/matrix_posting/matrix_posting_key.views.xml',
        'views/matrix_posting/matrix_posting_key_details.views.xml',
        'views/offset/offset_transaction.views.xml',
        'views/offset/offset_transaction_details.views.xml',
        'views/account_move/custom_invoice.views.xml',
        'views/account_move/filter.views.xml',
        'views/account_move/account_move_line/custom_invoice_line.views.xml',
        'views/contact/dokter_mitra.views.xml',
        'views/contact/filter_dokter_mitra.views.xml',
        'views/contact/custom_partner.views.xml',
        'views/contact/partner_menu.views.xml',
        'views/accounting/accounting_setup_details.views.xml',
        'views/accounting/accounting_setup.views.xml',
        'views/recurring/master_menu_recurring.views.xml',
        'views/recurring/recurring_setup.views.xml',
        'views/recurring/recurring_setup_details.views.xml',
        'views/recurring/recurring_setup_detail_details.views.xml',
        'views/tagihan/tagihan_master.views.xml',
        'views/tagihan/tagihan_headers.views.xml',
        'views/tagihan/tagihan_line.views.xml',
        'views/alokasi_beban/alokasi_beban.views.xml',
        'views/alokasi_beban/report.views.xml',
        'views/product/product_template.views.xml',
        'views/product/product_type.views.xml',
        'views/penampung_invoice/stg_invoice.views.xml',
        'views/penampung_invoice/stg_invoice_headers.views.xml',
        'views/penampung_invoice/stg_invoice_lines.views.xml',
        'views/penampung_invoice/stg_invoice_alloc.views.xml',
        'views/penampung_invoice/store_procedure.views.xml',
        'views/akun_kategori/akun_kategori_master.views.xml',
        'views/akun_kategori/akun_kategori.action.views.xml',
        'views/sales_point_coa_config/spcc_master.views.xml',
        'views/sales_point_coa_config/spcc.action.views.xml',
        'views/master_data/menuitem_master.views.xml',
        'views/transaction/menu_transaction.views.xml',
        'views/penampung_invoice/stg_claim_headers_views.xml',
        'views/penampung_invoice/stg_claim_lines_views.xml',
        'views/penampung_invoice/akun_kontrol_honor_dokter.xml',
        'data/sequence.xml',
        # 'views/master.views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # 'inventory_laptop/static/src/css/custom_style.css',
            # 'sidb/static/src/scss/profildesa.scss',
            'hr_holidays/static/src/**/*',
            # 'sanbe_hr_tms/static/src/**/*',
            'santosa_finance/static/src/js/report_esm.js',
            'santosa_finance/static/src/js/report_action.js',
            'santosa_finance/static/src/js/export_button.js',
            'santosa_finance/static/src/xml/export_button.xml',
            'santosa_finance/static/src/css/feature1.css',
        ],
    },
    

    'installable': True,
    'application': True,
    'auto_install': False

}