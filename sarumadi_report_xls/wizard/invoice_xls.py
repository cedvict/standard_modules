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
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
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
        ws1.write(row, col+1, "Fecha Inicial :", sub_header_style)
        ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_from,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 1
        ws1.write(row, col+1, "Fecha Final :", sub_header_style)
        ws1.write(row, col+2, datetime.strftime(datetime.strptime(self.date_to,DEFAULT_SERVER_DATE_FORMAT),"%d/%m/%Y"), sub_header_content_style)
        row += 1
        ws1.write(row,col+1,"Cliente",sub_header_style)
        ws1.write(row,col+2,"Ciudad",sub_header_style)
        ws1.write(row,col+3,"Dias",sub_header_style)
        ws1.write(row,col+4,"Fecha Factura",sub_header_style)
        ws1.write(row,col+5,"Referencia",sub_header_style)
        ws1.write(row,col+6,"Numero Factura",sub_header_style)
        ws1.write(row,col+7,"Total",sub_header_style)
        ws1.write(row,col+8,"Monto Adeudado",sub_header_style)
        ws1.write(row,col+9,"Asesor",sub_header_style)
        ws1.write(row,col+10,"Fecha Vencimiento",sub_header_style)
        ws1.write(row,col+11,"Estado",sub_header_style)

        row += 1
        #Searching for customer invoices
        invoices = self.env['account.invoice'].search([('type','=','out_invoice')])
        all_inv_total = 0
        for invoice in invoices:

            ws1.write(row,col+1,invoice.partner_id.name,line_content_style)
            ws1.write(row,col+2,invoice.partner_id.city,line_content_style)
            ws1.write(row,col+3,invoice.partner_id.x_tipo_client_bo,line_content_style)
            ws1.write(row,col+4,invoice.date_invoice,line_content_style)
            ws1.write(row,col+5,invoice.name,line_content_style)
            ws1.write(row,col+6,invoice.number,line_content_style)
            ws1.write(row,col+7,invoice.amount_total,line_content_style)
            ws1.write(row,col+8,invoice.residual,line_content_style)
            ws1.write(row,col+9,invoice.user_id.name,line_content_style)
            ws1.write(row,col+10,invoice.date_due,line_content_style)
            ws1.write(row,col+11,invoice.state.title(),line_content_style)
            row +=1
            all_inv_total += invoice.amount_total
        row +=1
        ws1.write(row,col+6,"Total Facturado:",sub_header_style)
        ws1.write(row,col+7,all_inv_total,sub_header_style)
        wb1.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name':'Estado_Pagos.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.xls.popup',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
