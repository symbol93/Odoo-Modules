{
    'name': 'Bart Export Saga',
    'description': 'Accounting',

    'author': 'Claudiu Hirsina',
    'website': '-',

    'category': 'Generic Modules/Others',
    'version': '1.0',
    'depends': ['account'],

    'data': [
        'wizard/account_move_export_saga.xml',
        'views/product_category.xml',
        'report/account_move_nir.xml',
        'views/report.xml',
        'views/account_move.xml'
    ],

    'qweb': [

    ],

    'license': "OPL-1",

    'installable': True,

}
