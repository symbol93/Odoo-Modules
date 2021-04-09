{
    'name': 'Website Shop Schedule',
    'description': 'Set a weekly schedule for your online sales',

    'author': 'Claudiu Hirsina',
    'website': '-',

    'category': 'Website, eCommerce',
    'version': '1.0',
    'depends': ['base','website_sale','website'],

    'data': [
        'data/ir.model.access.csv',
        'views/website_day_schedule.xml',
        'views/templates.xml',
        'wizard/shop_schedule_wizard.xml'
    ],

    'qweb': [

    ],

    'license': "OPL-1",

    'installable': True,

}
