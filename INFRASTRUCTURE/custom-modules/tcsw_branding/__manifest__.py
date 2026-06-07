{
    'name': 'TCSW Branding',
    'version': '17.0.1.0.0',
    'summary': 'Twin Cities Startup Week custom branding — removes Odoo identity, applies TCSW theme',
    'description': 'Replaces Odoo branding with TCSW brand identity: colors, logo, favicon, login page, and removes all Powered by Odoo references.',
    'category': 'Theme',
    'author': 'Ever Just',
    'website': 'https://tcsw.everjust.app',
    'license': 'LGPL-3',
    'depends': ['web', 'base_setup'],
    'data': [
        'data/res_company_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tcsw_branding/static/src/scss/tcsw_theme.scss',
        ],
        'web.assets_frontend': [
            'tcsw_branding/static/src/scss/tcsw_frontend.scss',
        ],
        'web.assets_web': [
            'tcsw_branding/static/src/scss/tcsw_login.scss',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
