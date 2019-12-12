# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Company(models.Model):
    _inherit = 'res.company'

    report_background_image1 = fields.Binary('Background Image for Report Frontpage',
            help='Set Background Image for Report Frontpage')

    # header_image = fields.Binary('Header Image')
    # footer_image = fields.Binary('Footer Image')