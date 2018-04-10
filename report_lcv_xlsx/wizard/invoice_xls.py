# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
import base64
import cStringIO
from datetime import datetime

class InvoiceXLSWizard(models.Model):

    _name = 'invoice.xls.popup'

    #fields to generate xls
    date_from = fields.Date('Fecha Inicial')
    date_to = fields.Date('Fecha Final')

    # fields for download xls
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    report = fields.Binary('Descargue el archivo XLS', filters='.xls', readonly=True)
    name =  fields.Char('File Name', size=32)

    @api.multi
    def generate_xls_report(self):

        self.ensure_one()

        wb1 = xlwt.Workbook(encoding='utf-8')
        ws1 = wb1.add_sheet('Reporte Pagos Cliente')
        fp = cStringIO.StringIO()


        #Content/Text style
        header_content_style = xlwt.easyxf("font: name Helvetica size 20 px, bold 1, height 170;")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170;")
        row = 1
        col = 0
        ws1.row(row).height = 500
        ws1.write_merge(row,row, 2, 6, "Reporte de Estado de Pagos", header_content_style)
        row += 2
        ws1.write(row, col+1, "From :", sub_header_style)
        ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_from,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 1
        ws1.write(row, col+1, "To :", sub_header_style)
        ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_to,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 1
        ws1.write(row,col+1,"ESPECIFICACION",sub_header_style)
        ws1.write(row,col+2,"No",sub_header_style)
        ws1.write(row,col+3,"FECHA",sub_header_style)
        ws1.write(row,col+4,"No DE FACTURA",sub_header_style)
        ws1.write(row,col+5,"No DE AUTORIZACION",sub_header_style)
        ws1.write(row,col+6,"ESTADO",sub_header_style)
        ws1.write(row,col+7,"NIT/CI CLIENTE",sub_header_style)
        ws1.write(row,col+8,"NOMBRE O RAZON SOCIAL",sub_header_style)
        ws1.write(row,col+9,"IMPORTE TOTAL",sub_header_style)
        ws1.write(row,col+10,"IMPORTE ICE",sub_header_style)
        ws1.write(row,col+11,"IMPORTE EXCENTO",sub_header_style)
        ws1.write(row,col+12,"VENTAS GRAVADAS A TASA CERO",sub_header_style)
        ws1.write(row,col+13,"SUBTOTAL",sub_header_style)
        ws1.write(row,col+14,"DESCUENTO",sub_header_style)
        ws1.write(row,col+15,"IMPORTE BASE PARA DEBITO FISCAL",sub_header_style)
        ws1.write(row,col+16,"DEBITO FISCAL",sub_header_style)
        ws1.write(row,col+17,"CODIGO DE CONTROL",sub_header_style)

        row += 1
        #Searching for customer invoices
        invoices = self.env['account.invoice'].search([('type','=','out_invoice')])
        all_inv_total = 0
        nro = 1
        for invoice in invoices:

            ws1.write(row,col+1,"3",line_content_style)
            ws1.write(row,col+2,"nro",line_content_style)
            ws1.write(row,col+3,invoice.date_invoice,line_content_style)
            ws1.write(row,col+4,invoice.number,line_content_style)
            ws1.write(row,col+5,invoice.autorizacion,line_content_style)
            ws1.write(row,col+6,invoice.estado_factura,line_content_style)
            ws1.write(row,col+7,invoice.partner_id.nit,line_content_style)
            ws1.write(row,col+8,invoice.partner_id.name,line_content_style)
            ws1.write(row,col+9,invoice.amount_total,line_content_style)
            ws1.write(row,col+10,"0",line_content_style)
            ws1.write(row,col+11,"0",line_content_style)
            ws1.write(row,col+12,"0",line_content_style)
            ws1.write(row,col+13,invoice.amount_total,line_content_style)
            ws1.write(row,col+14,"0",line_content_style)
            ws1.write(row,col+15,invoice.amount_untaxed,line_content_style)
            ws1.write(row,col+16,invoice.amount_tax,line_content_style)
            ws1.write(row,col+17,invoice.code,line_content_style)
            row +=1
            nro +=1
            all_inv_total += invoice.amount_total
        row +=1
        ws1.write(row,col+6,"Main total:",sub_header_style)
        ws1.write(row,col+7,all_inv_total,sub_header_style)
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name':'Libro_Ventas.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.xls.popup',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
