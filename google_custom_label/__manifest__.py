
{
    'name': 'Google Custom Label',
    'version': '17.0.0.0.1',
    'category': 'eCpmmerce',
    'author': 'Johnson Epo',
    'website': 'https://envoos.com',
    'license': 'OPL-1',
    'summary': 'This module add a google cutom label which you can include in you feed',
    'images': ['static/description/icon.png'],
    'depends': [
        'base', 'product', 'product_data_feed', 'product_google_category'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/google_custom_label.xml',
    ],
    'support': 'johnsonepo@gmail.com',
    'application': True,
    'installable': True,
    'auto_install': False,
}
