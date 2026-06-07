# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    # Custom fields for TCSW-style events
    is_startup_week = fields.Boolean(
        string='Is Startup Week Event',
        help='Mark if this is a multi-day startup week event'
    )
    partner_org_count = fields.Integer(
        string='Partner Organizations',
        compute='_compute_partner_org_count',
        store=True
    )
    venue_count = fields.Integer(
        string='Venues',
        compute='_compute_venue_count',
        store=True
    )

    @api.depends('registration_ids')
    def _compute_partner_org_count(self):
        for event in self:
            # Count unique partner organizations submitting sessions
            partner_orgs = self.env['event.registration'].search([
                ('event_id', '=', event.id),
                ('partner_id.is_organization', '=', True)
            ]).mapped('partner_id')
            event.partner_org_count = len(partner_orgs)

    @api.depends('event_ticket_ids')
    def _compute_venue_count(self):
        for event in self:
            # Count unique venues from tickets
            venues = self.env['event.event.ticket'].search([
                ('event_id', '=', event.id)
            ]).mapped('venue_id')
            event.venue_count = len(venues)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    # Enhanced attendee fields
    is_volunteer = fields.Boolean(
        string='Is Volunteer',
        help='Mark if this attendee is a volunteer'
    )
    volunteer_role = fields.Selection([
        ('registration', 'Registration Desk'),
        ('venue_support', 'Venue Support'),
        ('av_tech', 'AV Technician'),
        ('info_desk', 'Info Desk'),
        ('setup_crew', 'Setup Crew'),
        ('other', 'Other'),
    ], string='Volunteer Role')
    volunteer_shifts = fields.Text(
        string='Assigned Shifts',
        help='Text field for shift assignments (will be replaced with proper scheduling)'
    )
    sponsor_tier = fields.Selection([
        ('platinum', 'Platinum'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
        ('supporter', 'Supporter'),
    ], string='Sponsor Tier')
