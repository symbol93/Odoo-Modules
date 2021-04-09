{
    'name': 'Website Shops',
    'description': 'Define shops for webiste and pos',

    'author': 'Claudiu Hirsina',
    'website': '-',

    'category': 'Website, eCommerce',
    'version': '1.0',
    'depends': ['base', 'website', 'pos_restaurant', 'product'],

    'data': [
        'data/ir.model.access.csv',
        'views/shop.xml',
        'views/pos_config.xml',
        'views/website.xml',

    ],

    'qweb': [

    ],

    'license': "OPL-1",

    'installable': True,

}
