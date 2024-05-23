
{
    'name': 'Copy Cat',
    'version': '17.0.1.1.0',
    'category': 'Hidden',
    'author': 'Johnson Epo',
    'website': 'https://envoos.com',
    'license': 'OPL-1',
    'summary': 'Product Data Feed Copy Cat',
    'images': ['static/description/icon.png'],
    'depends': [
        'base', 'product', 'product_data_feed', 'product_google_category'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/settings.xml',
    ],
    'support': 'johnsonepo@gmail.com',
    'application': True,
    'installable': True,
    'auto_install': False,
}
