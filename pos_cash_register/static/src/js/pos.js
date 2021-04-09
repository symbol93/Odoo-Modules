odoo.define('pos_cash_register.pos', function (require) {
    var screens = require('point_of_sale.screens');
    var session = require('web.session');
    var gui = require('point_of_sale.gui');


    screens.ReceiptScreenWidget.include({
        download_receipt: function (contents, filename) {
            let final_contents = this.charmap_receipt_contents(contents);
            var use_cash_register = this.pos.config && this.pos.config.use_cash_register || false;
            if (use_cash_register) {

                var params = {
                    'ip': this.pos.config.cash_register_ip,
                    'filename': filename,
                    'content': contents,
                    'key': 'QDGKVO9Q1T'
                };
                var gui = this.gui;
                $.ajax({
                    url: this.pos.config.cash_register_ip,
                    type: "POST",
                    data: {'filename': filename, 'content': contents, 'key': 'QDGKVO9Q1T'},
                    success: function (result) {
                        var title = 'Succes';
                        var message = 'Bon tiparit cu succes!';
                        if (result != '1') {
                            title = 'Eroare';
                            message = 'Programul a returnat eroare!'
                        }
                        gui.show_popup('alert', {
                            'title': title,
                            'body': message,
                        });
                    },
                    error: function (error) {

                        gui.show_popup('alert', {
                            'title': 'Eroare',
                            'body': 'Nu s-a realizat conexiunea cu serverul pt casa de marcat!',
                        });
                    },
                    timeout: 1000

                })
                /*

                 session.rpc("/pos/send_cashregister", params).then(function (result) {
                 var title = 'Succes';
                 if (result.code != '200') {
                 title = 'Eroare'
                 }
                 this.gui.show_popup('confirm', {
                 'title': title,
                 'body': ( result.response),
                 });
                 })
                 */


            }
            else {
                var downloadLink = document.createElement("a");
                downloadLink.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(final_contents);
                downloadLink.download = filename || "sale_filename.bon";
                downloadLink.click();
            }
        },
    });



});