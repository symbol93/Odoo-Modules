from lxml import etree
import datetime

import odoo
from odoo.http import route, content_disposition, request


class DownloadFile(odoo.http.Controller):

    @route('/web/xml/export_saga', type='http', auth='public')
    def export_saga(self, ids, **kw):
        filename = 'export_saga.xml'
        content = self.export_saga_xml(ids)
        invoice_obj = request.env['account.move']
        try:
            factura = invoice_obj.browse([int(x) for x in ids[1:-1].split(',')])[0]
            cod_fiscal = factura.type in ['out_invoice', 'out_refund'] and factura.company_id.vat or factura.partner_id.vat

            filename = 'F_%s_%s_%s.xml' % (cod_fiscal, factura.name, datetime.datetime.strptime(str(factura.invoice_date), '%Y-%m-%d').strftime('%d.%m.%Y'))
        except:
            pass
        headers = [
            ('Content-Type', 'application/xml'),
            ('Content-Disposition', content_disposition(filename)),
            ('charset', 'utf-8'),
        ]
        return request.make_response(content, headers=headers, cookies=None)

    def export_saga_xml(self, ids):
        invoice_obj = request.env['account.move']
        root = etree.Element('Facturi')
        for factura in invoice_obj.browse([int(x) for x in ids[1:-1].split(',')]):
            # add tag factura
            xml_factura = etree.Element('Factura')

            # add tag antent
            xml_antet = etree.Element('Antet')

            if factura.type in ['out_invoice', 'out_refund']:
                txt_furnizor_name = factura.company_id.name
                txt_client_name = factura.partner_id.name

                txt_furnizor_cif = factura.company_id.vat or ""
                txt_client_cif = factura.partner_id.vat or ""

                txt_furnizor_vat = factura.company_id.company_registry or ""
                txt_client_vat = factura.partner_id.nrc or ""

                txt_furnizor_tara = factura.company_id.country_id and factura.company_id.country_id.code or ''
                txt_client_tara = str(factura.partner_id.country_id and factura.partner_id.country_id.code or "")

                txt_furnizor_judet = factura.company_id.state_id and factura.company_id.state_id.code or ''

                txt_furnizor_adresa = factura.company_id.street or "" + " " + factura.company_id.city or ""
                txt_client_adresa = str(factura.partner_id.state_id and factura.partner_id.state_id.code or "") + " " + str(factura.partner_id.street or "") + " " + str(factura.partner_id.street2 or "") + " " + str(
                    factura.partner_id.city or "")

                txt_furnizor_info = "Telefon " + str(factura.company_id.phone) + "Email: " + str(factura.company_id.email)

                txt_client_telefon = factura.partner_id.phone or ""
                txt_client_mail = factura.partner_id.email or ""

                txt_numar_factura = factura.name or ''

            if factura.type in ['in_invoice', 'in_refund']:
                txt_furnizor_name = factura.partner_id.name
                txt_client_name = factura.company_id.name

                txt_furnizor_cif = factura.partner_id.vat or ""
                txt_client_cif = factura.company_id.vat or ""

                txt_furnizor_vat = factura.partner_id.nrc or ""
                txt_client_vat = factura.company_id.company_registry or ""

                txt_furnizor_tara = str(factura.partner_id.country_id and factura.partner_id.country_id.code or "")
                txt_client_tara = factura.company_id.country_id and factura.company_id.country_id.code or ''

                txt_furnizor_judet = str(factura.partner_id.state_id and factura.partner_id.state_id.code or "")

                txt_furnizor_adresa = str(factura.partner_id.state_id and factura.partner_id.state_id.code or "") + " " + str(factura.partner_id.street or "") + " " + str(factura.partner_id.street2 or "") + " " + str(
                    factura.partner_id.city or "")
                txt_client_adresa = factura.company_id.street or "" + " " + factura.company_id.city or "" + " " + str(ffactura.company_id.state_id and factura.company_id.state_id.code or '')

                txt_furnizor_info = "Telefon " + (factura.partner_id.phone or "") or "" + " Email " + str(factura.partner_id.email or "")

                txt_client_telefon = str(factura.company_id.phone)
                txt_client_mail = str(factura.company_id.email or "")

                txt_numar_factura = factura.ref or ''

            # FURNIZOR
            # add tag furnizor
            xml_furnizor_nume = etree.Element('FurnizorNume')
            xml_furnizor_nume.text = txt_furnizor_name
            # add tag FurnizorCIF
            xml_furnizor_cif = etree.Element('FurnizorCIF')
            xml_furnizor_cif.text = txt_furnizor_cif
            # add tag FurnizorNrRegCom
            xml_furnizor_nrreg = etree.Element('FurnizorNrRegCom')
            xml_furnizor_nrreg.text = txt_furnizor_vat

            # add tag FurnizorCapital
            xml_furnizor_capital = etree.Element('FurnizorCapital')
            xml_furnizor_capital.text = ""  # todo de adaugaut capital

            # add tag FurnizorTara
            xml_furnizor_tara = etree.Element('FurnizorTara')
            xml_furnizor_tara.text = txt_furnizor_tara

            # add tag FurnizorJudet
            xml_furnizor_judet = etree.Element('FurnizorJudet')
            xml_furnizor_judet.text = txt_furnizor_judet
            # add tag FurnizorAdresa
            xml_furnizor_adresa = etree.Element('FurnizorAdresa')
            xml_furnizor_adresa.text = txt_furnizor_adresa
            # add tag FurnizorBanca
            xml_furnizor_banca = etree.Element('FurnizorBanca')
            xml_furnizor_banca.text = ''  # todo de pus furnizor banca factura.company_id.banca_saga or ""
            # add tag FurnizorIBAN
            xml_furnizor_iban = etree.Element('FurnizorIBAN')
            xml_furnizor_iban.text = ''  # todo de pus furnizor iban factura.company_id.iban_saga or ""
            # add tag FurnizorInformatiiSuplimentare
            xml_furnizor_informatii = etree.Element('FurnizorInformatiiSuplimentare')
            xml_furnizor_informatii.text = txt_furnizor_info

            # CLIENT
            # add tag ClientNume
            xml_client_nume = etree.Element('ClientNume')
            xml_client_nume.text = txt_client_name
            # add tag ClientInformatiiSuplimentare
            xml_client_informatii = etree.Element('ClientInformatiiSuplimentare')
            xml_client_informatii.text = ""
            # add tag ClientCIF
            xml_client_cif = etree.Element('ClientCIF')
            xml_client_cif.text = txt_client_cif
            # add tag ClientNrRegCom
            xml_client_nrreg = etree.Element('ClientNrRegCom')
            xml_client_nrreg.text = txt_client_vat
            # add tag ClientTara
            xml_client_judet = etree.Element('ClientTara')
            xml_client_judet.text = txt_client_tara
            # add tag ClientAdresa
            xml_client_adresa = etree.Element('ClientAdresa')
            xml_client_adresa.text = txt_client_adresa
            # add tag ClientBanca
            xml_client_banca = etree.Element('ClientBanca')
            xml_client_banca.text = ""
            # add tag ClientIBAN
            xml_client_iban = etree.Element('ClientIBAN')
            xml_client_iban.text = ""

            # add tag <ClientTelefon>
            xml_client_telefon = etree.Element('ClientTelefon')
            xml_client_telefon.text = txt_client_telefon

            # add tag <ClientMail>
            xml_client_email = etree.Element('ClientMail')
            xml_client_email.text = txt_client_mail

            # add tag FacturaNumar
            xml_factura_numar = etree.Element('FacturaNumar')
            xml_factura_numar.text = txt_numar_factura
            # add tag FacturaData
            xml_factura_data = etree.Element('FacturaData')
            xml_factura_data.text = datetime.datetime.strptime(str(factura.invoice_date), '%Y-%m-%d').strftime('%d.%m.%Y')
            # add tag FacturaScadenta
            xml_factura_scadenta = etree.Element('FacturaScadenta')
            xml_factura_scadenta.text = datetime.datetime.strptime(str(factura.invoice_date_due), '%Y-%m-%d').strftime('%d.%m.%Y')
            # add tag FacturaTaxareInversa
            xml_factura_taxareinversa = etree.Element('FacturaTaxareInversa')
            xml_factura_taxareinversa.text = "NU"
            # add tag FacturaTVAIncasare
            xml_factura_tva_incasare = etree.Element('FacturaTVAIncasare')
            xml_factura_tva_incasare.text = ""
            # add tag FacturaInformatiiSuplimentare
            xml_factura_informatii = etree.Element('FacturaInformatiiSuplimentare')
            xml_factura_informatii.text = ""
            # add tag FacturaMoneda
            xml_factura_moneda = etree.Element('FacturaMoneda')
            xml_factura_moneda.text = factura.currency_id.name

            xml_factura_id = etree.Element('FacturaID')
            xml_factura_id.text = str(factura.id) or ""

            xml_antet.append(xml_furnizor_nume)
            xml_antet.append(xml_furnizor_cif)
            xml_antet.append(xml_furnizor_nrreg)
            xml_antet.append(xml_furnizor_capital)
            xml_antet.append(xml_furnizor_tara)
            xml_antet.append(xml_furnizor_judet)
            xml_antet.append(xml_furnizor_adresa)
            xml_antet.append(xml_furnizor_banca)
            xml_antet.append(xml_furnizor_iban)
            xml_antet.append(xml_furnizor_informatii)
            xml_antet.append(xml_client_nume)
            xml_antet.append(xml_client_informatii)
            xml_antet.append(xml_client_cif)
            xml_antet.append(xml_client_nrreg)
            xml_antet.append(xml_client_judet)
            xml_antet.append(xml_client_adresa)
            xml_antet.append(xml_client_banca)
            xml_antet.append(xml_client_iban)
            xml_antet.append(xml_client_telefon)
            xml_antet.append(xml_client_email)
            xml_antet.append(xml_factura_numar)
            xml_antet.append(xml_factura_data)
            xml_antet.append(xml_factura_scadenta)
            xml_antet.append(xml_factura_taxareinversa)
            xml_antet.append(xml_factura_tva_incasare)
            xml_antet.append(xml_factura_informatii)
            xml_antet.append(xml_factura_moneda)
            xml_antet.append(xml_factura_id)

            # add tag Detalii
            xml_detalii = etree.Element('Detalii')

            # add tag Continut
            xml_continut = etree.Element('Continut')
            xml_continut.text = ""
            i = 0
            for linie in factura.invoice_line_ids:
                i = i + 1
                # add tag Linie
                xml_linie = etree.Element('Linie')
                xml_linie.text = ""

                # add tag LinieNrCrt
                xml_linie_crt = etree.Element('LinieNrCrt')
                xml_linie_crt.text = str(i)

                # ADD TAG Gestiune
                xml_linie_gestiune = etree.Element('Gestiune')
                xml_linie_gestiune.text = ""  # todo de adaugat Gestiune COD

                # add tag Descriere
                xml_linie_desscriere = etree.Element('Descriere')
                xml_linie_desscriere.text = linie.product_id.name
                # add tag CodArticolFurnizor
                xml_linie_cod_furnizor = etree.Element('CodArticolFurnizor')
                xml_linie_cod_furnizor.text = ''  # linie.product_id.default_code or ""
                # add tag CodArticolClient
                xml_linie_cod_client = etree.Element('CodArticolClient')
                xml_linie_cod_client.text = ""
                # add tag CodBare
                xml_linie_cod_bare = etree.Element('CodBare')
                xml_linie_cod_bare.text = ""
                # add tag InformatiiSuplimentare
                xml_linie_informatii = etree.Element('InformatiiSuplimentare')
                xml_linie_informatii.text = ""
                # add tag UM
                xml_linie_um = etree.Element('UM')
                xml_linie_um.text = linie.product_uom_id.name or ""
                # add tag Cantitate
                xml_linie_cantitate = etree.Element('Cantitate')
                xml_linie_cantitate.text = str(linie.quantity * (factura.type in ['out_refund', 'in_refund'] and -1 or 1))
                # add tag Pret
                xml_linie_pret = etree.Element('Pret')  # todo de vazut cu TVA sau FARA
                xml_linie_pret.text = str(round(linie.price_unit, 4))
                # add tag Valoare
                xml_linie_valoare = etree.Element('Valoare')  # todo de vazut Cu TVA SAU FARA
                xml_linie_valoare.text = str(linie.price_subtotal * (factura.type in ['out_refund', 'in_refund'] and -1 or 1))
                # add tag ProcTVA
                xml_linie_tva = etree.Element('CotaTVA')
                xml_linie_tva.text = str(int(linie.tax_ids and linie.tax_ids[0].amount or 0))
                # add tag TVA
                xml_linie_tva_valoare = etree.Element('TVA')
                xml_linie_tva_valoare.text = str(round(linie.price_total - linie.price_subtotal, 2))
                # add tag Cont
                xml_linie_cont = etree.Element('Cont')
                xml_linie_cont.text = linie.account_id.code

                xml_linie.append(xml_linie_crt)
                if False:
                    xml_linie.append(xml_linie_gestiune)
                xml_linie.append(xml_linie_desscriere)
                xml_linie.append(xml_linie_cod_furnizor)
                xml_linie.append(xml_linie_cod_client)
                xml_linie.append(xml_linie_cod_bare)
                xml_linie.append(xml_linie_informatii)
                xml_linie.append(xml_linie_um)
                xml_linie.append(xml_linie_cantitate)
                xml_linie.append(xml_linie_pret)
                xml_linie.append(xml_linie_valoare)
                xml_linie.append(xml_linie_tva)
                xml_linie.append(xml_linie_tva_valoare)

                xml_linie.append(xml_linie_cont)
                xml_continut.append(xml_linie)



            xml_detalii.append(xml_continut)
            xml_factura.append(xml_antet)
            xml_factura.append(xml_detalii)
            root.append(xml_factura)
            factura.update({'expoerted_saga': True})
        s = etree.tostring(root, pretty_print=True)

        tree = etree.ElementTree(root)
        # tree.write('output.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")

        return s
