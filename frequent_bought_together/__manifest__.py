
{
    'name': 'Frequently Bought Together',
    'version': '17.0.0.0.0',
    'category': 'eCommerce',
    'author': 'Johnson Epo',
    'website': 'https://envoos.com',
    'license': 'OPL-1',
    'summary': 'This module gets the requently bought together products',
    'images': ['static/description/icon.png'],
    'depends': ['product', 'website', 'base', 'website_sale'],
    'data': [
        'views/frequently_bought_together_snippet_template.xml',
        'views/frequently_bought_together.xml',
        #'data/data.xml',
        #'views/cron.xml',

    ],
'assets': {},
    'support': 'johnsonepo@gmail.com',
    'application': True,
    'installable': True,
    'auto_install': False,

}
