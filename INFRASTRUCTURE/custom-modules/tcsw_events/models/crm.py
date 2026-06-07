# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Enhanced sponsor/vendor tracking
    is_sponsor = fields.Boolean(
        string='Is Sponsor',
        help='Mark if this lead is a sponsor opportunity'
    )
    is_vendor = fields.Boolean(
        string='Is Vendor',
        help='Mark if this lead is a vendor opportunity'
    )
    sponsor_tier = fields.Selection([
        ('platinum', 'Platinum'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
        ('supporter', 'Supporter'),
    ], string='Sponsor Tier')
    sponsorship_amount = fields.Monetary(
        string='Sponsorship Amount',
        currency_field='currency_id'
    )
    deliverables_count = fields.Integer(
        string='Deliverables',
        compute='_compute_deliverables_count',
        store=True
    )

    @api.depends('order_ids')
    def _compute_deliverables_count(self):
        for lead in self:
            # Count deliverables from linked orders
            lead.deliverables_count = len(lead.order_ids)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Partner organization tracking
    is_organization = fields.Boolean(
        string='Is Organization',
        help='Mark if this partner is an organization (not an individual)'
    )
    event_partner_count = fields.Integer(
        string='Events Participated',
        compute='_compute_event_partner_count',
        store=True
    )

    @api.depends('event_registration_ids')
    def _compute_event_partner_count(self):
        for partner in self:
            partner.event_partner_count = len(partner.event_registration_ids)
