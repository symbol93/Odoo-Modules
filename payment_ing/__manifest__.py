# -*- coding: utf-8 -*-

{
    'name': 'Ing Payment Acquirer',
    'author': "Claudiu Hirsina",
    'website': "",
    'category': 'Accounting/Payment',
    'summary': 'Payment Acquirer: Ing',
    'version': '1.0',
    'description': """Ing Payment Acquirer""",
    'depends': [
        'payment',
    ],
    'data': [
        'views/payment_view.xml',
        'views/template.xml',
        'data/payment_acquirer_data.xml',
        'views/website_sale.xml'
    ],
    'installable': True,
    'images': ['static/description/icon.jpg'],

}
