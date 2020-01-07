# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Company(models.Model):
    _inherit = 'res.company'

    # report_background_image1 = fields.Binary('Background Image for Report Frontpage',
    #         help='Set Background Image for Report Frontpage')

    report_header_image = fields.Binary('Default Header Image for Report', help='Set Background Image for Report Header')
    report_footer_image = fields.Binary('Default Footer Image for Report', help='Set Background Image for Report Footer')