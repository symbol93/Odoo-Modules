{
    'name': 'POS Cash Register',
    'description': 'Connect cash register on pos on local newtwork',

    'author': 'Claudiu Hirsina',
    'website': '-',

    'category': 'Generic Modules/Others',
    'version': '1.0',
    'depends': ['base', 'point_of_sale', 'pos_restaurant','diginesis_point_of_sale'],

    'data': [
        'template/import.xml',
        'views/pos_config.xml'
    ],

    'qweb': [
        'static/src/xml/*.xml'
    ],

    'license': "OPL-1",

    'installable': True,

}
