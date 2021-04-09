{
    'name': 'Sales in custody method',
    'summary': 'You can sell your products to your clients and deliver the product without making the invoice on sales order and at the end of the month you will invoice what products you want.',
    'description': '',

    'author': 'Claudiu Hirsina',
    'website': '-',

    'category': 'Sales',
    'version': '13.0.0.1',
    'depends': ['base', 'stock', 'sale', 'account'],

    'data': [

        'data/res.groups.csv',
        'data/ir.rule.csv',
        'data/ir.model.access.csv',
        'views/sales_custody.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/res_partner.xml',
        'wizard/create_invoice_custody.xml',
        'wizard/create_picking_return.xml'
    ],

    'qweb': [

    ],

    'license': "OPL-1",

    'installable': True,

}
