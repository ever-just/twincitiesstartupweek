# -*- coding: utf-8 -*-
{
    'name': 'TCSW Event Configuration',
    'version': '1.0.0',
    'category': 'Events',
    'summary': 'Custom event configuration for Twin Cities Startup Week and SaaS event management',
    'description': """
TCSW Event Configuration
=========================

This module provides custom configurations and enhancements for Odoo's Events module,
specifically tailored for:
- Multi-day, multi-venue startup week events
- Partner organization session submissions
- Sponsor tier management
- Volunteer coordination
- SaaS multi-tenant event management

Features:
- Custom event types for startup week sessions
- Sponsor tier field on event partners
- Enhanced attendee registration fields
- Volunteer role and shift tracking
    """,
    'author': 'Everjust',
    'website': 'https://everjust.app',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'event',
        'crm',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/event_views.xml',
        'views/crm_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tcsw_events/static/src/js/tcsw_events.js',
        ],
    },
    'installable': True,
    'application': True,
}
