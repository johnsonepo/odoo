{
    'name': "Tabby payment",
    'category': 'Account',
    'summary': "Let your customers shop now and split their purchases into 4 interest-free payments while you get paid in full-upfront..",
    'version': '1.0',
    'author': 'Johnson Epo',
    'website': 'www.envoos.com',
    'support': 'johnsonepo@gmail.com',
    'sequence': '34',
    'depends': ['base', 'website_sale'],
    'data': [
        'views/payment_tabby_templates.xml',
        'views/payment_provider.xml',
        'views/tabby_sale_order_data.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'https://api.tabby.ai/api/v2/checkout'
        ],
    },
    'images': ['tabby_payment/description/icon.png'],
    'license': "OPL-1",
    'auto_install': False,
    'installable': True,
    'application': False,
}