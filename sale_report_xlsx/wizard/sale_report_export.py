# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2018 darkknightapps@gmail.com
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleExcelExportHeader(models.TransientModel):
    _name = "sale.excel.export.header"
    _description = "Sale Excel Export Header"

    date_from = fields.Char(string='From Date')
    date_to = fields.Char(string='To Date')
    partner_ids = fields.Many2many('res.partner', string='Customers')
    order_state = fields.Char(string='Order Status')
    user = fields.Char(string='Salesperson')
    team = fields.Char(string='Sales Team')
    payment_term = fields.Char(string='Payment Term')
    product_ids = fields.Many2many('product.product', string='Products')
    line_ids = fields.Many2many('sale.order.line', string='Sale Order Lines')


class SaleExcelExport(models.TransientModel):
    _name = "sale.excel.export"
    _description = "Sale Excel Export Wizard"

    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    partner_ids = fields.Many2many('res.partner', string='Customers')
    order_state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Order Status')
    user_id = fields.Many2one('res.users', string='Salesperson')
    team_id = fields.Many2one('crm.team', string='Sales Team')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    product_ids = fields.Many2many('product.product', string='Products')

    @api.multi
    def action_print(self):
        for rec in self:
            domain = []
            order_line_domain = []
            header_vals = {}
            datas = {}
            if rec.date_from:
                domain.append(('date_order', '>=', rec.date_from))
                header_vals.update({'date_from': rec.date_from})
            if rec.date_to:
                domain.append(('date_order', '<=', rec.date_to))
                header_vals.update({'date_to': rec.date_to})
            if rec.order_state:
                domain.append(('state', '=', rec.order_state))
                header_vals.update({'order_state': rec.order_state.capitalize()})
            if rec.user_id:
                domain.append(('user_id', '=', rec.user_id.id))
                header_vals.update({'user': rec.user_id.name})
            if rec.team_id:
                domain.append(('team_id', '=', rec.team_id.id))
                header_vals.update({'team': rec.team_id.name})
            if rec.payment_term_id:
                domain.append(('payment_term_id', '=', rec.payment_term_id.id))
                header_vals.update({'payment_term': rec.payment_term_id.name})
            if rec.partner_ids:
                partner_ids = [partner.id for partner in rec.partner_ids]
                domain.append(('partner_id', 'in', partner_ids))
                header_vals.update({'partner_ids': [(6, 0, rec.partner_ids.ids)]})
            if rec.product_ids:
                product_ids = [product.id for product in rec.product_ids]
                order_line_domain.append(('product_id', 'in', product_ids))
                header_vals.update({'product_ids': [(6, 0, rec.product_ids.ids)]})
            orders = self.env['sale.order'].search(domain)
            if orders:
                order_line_domain.append(('order_id', 'in', orders.ids))
            if order_line_domain:
                lines = self.env['sale.order.line'].search(order_line_domain,
                                                              order='create_date')
                if not lines:
                    raise UserError(_('No data available!'))
                else:
                    header_vals.update({'line_ids': [(6, 0, lines.ids)]})
            header = self.env['sale.excel.export.header'].create(header_vals)
            datas = {'ids': [header.id]}
            datas['model'] = 'sale.excel.export.header'
            datas['form'] = self.read()[0]
            for field in datas['form'].keys():
                if isinstance(datas['form'][field], tuple):
                    datas['form'][field] = datas['form'][field][0]
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'sale_report_xlsx.sale_report_excel_export.xlsx',
                'datas': datas,
                'name': 'Sale Excel Report',
            }
