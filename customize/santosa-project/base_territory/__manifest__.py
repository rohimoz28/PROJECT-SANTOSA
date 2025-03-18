# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Territory",
    "summary": "This module allows you to define territories, branches,"
    " districts and regions to be used for Field Service operations or Sales.",
    "version": "17.0.1.0.0",
    "category": "Hidden",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["base",'hr','sale_management','stock','purchase'],
    "data": [
        "security/ir.model.access.csv",
        "security/branch_security.xml",
        "security/multi_branch.xml",
        "views/res_territory.xml",
        "views/res_branch.xml",
        "views/res_district.xml",
        "views/res_region.xml",
        "views/res_country.xml",
        "views/menu.xml",
        "views/res_users.xml",
        "views/inherited_sale_order.xml",
        "views/inherited_stock_picking.xml",
        "views/inherited_stock_move.xml",
        "views/inherited_account_invoice.xml",
        "views/inherited_purchase_order.xml",
        "views/inherited_stock_warehouse.xml",
        "views/inherited_stock_location.xml",
    ],
    "demo": ["demo/base_territory_demo.xml"],
    "application": True,
    'assets': {
        'web.assets_backend': [
            'base_territory/static/src/js/branch_service.js',
            'base_territory/static/src/js/session.js',
            'base_territory/static/src/xml/branch.xml',
        ]
    },
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["max3903", "brian10048"],
}
