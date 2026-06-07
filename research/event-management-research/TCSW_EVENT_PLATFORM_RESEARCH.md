# TCSW Event Platform Research
## Open-Source Software for a Multi-Day, Multi-Venue Startup Week

**Event profile:** 7-day festival, 10–20 partner venues across Twin Cities, 50+ partner organizations hosting sessions, thousands of attendees, 20+ sponsors at multiple tiers, dozens of vendors, 50–100 volunteers, small internal coordination team.

**Research question:** What open-source platforms are actually built to manage the full operational complexity of putting on this kind of event?

---

## Operational Requirements Map

These are the real workflows TCSW runs every cycle. Every platform below is evaluated against all of them.

| # | Workflow | Complexity |
|---|---|---|
| 1 | Partner orgs submit sessions through a public portal | High — multi-org, custom fields, review needed |
| 2 | Staff reviews, approves, and schedules sessions | High — track assignment, conflict detection, multi-day |
| 3 | Multi-track schedule published across 10+ venues | High — multi-location, multi-day, public-facing |
| 4 | Speaker/presenter management (bios, AV, comms) | Medium |
| 5 | Attendee registration with custom questions | Medium |
| 6 | Public ticket sales for sessions/passes | Medium |
| 7 | QR check-in at venue doors | Medium |
| 8 | Volunteer shifts across all venues for all 7 days | High — 50–100 people, 10+ locations |
| 9 | Sponsor tracking: tiers, deliverables, payment status | High — custom per tier, multiple contacts |
| 10 | Vendor coordination: contracts, setup windows, payments | Medium-High |
| 11 | Internal task management and team assignments | Medium |
| 12 | Budget tracking: expenses vs. actuals | Medium |
| 13 | Day-of staff communications across venues | Medium |
| 14 | Post-event reporting and analytics | Medium |

---

## Platform Evaluations

---

### 1. Odoo Community
**GitHub:** https://github.com/odoo/odoo
**Stars:** ⭐ 52,200 · **Forks:** 32,700 · **License:** LGPL-3.0 (Community Edition)
**Tech:** Python / PostgreSQL / JavaScript
**Scale:** 12+ million users worldwide, used by companies from 5 to 300,000 employees

#### Why it belongs at the top of this list

Odoo is the only open-source platform that addresses the majority of TCSW's workflows in a single, integrated system. Unlike generic project management tools, Odoo has a dedicated **Events module** purpose-built for event operations — and every other module it ships (CRM, Accounting, HR, Project, Purchase, Website) is natively integrated with it.

#### Events Module (Core to TCSW)

**Session & Program Management**
- Talk proposal management: allow partner organizations to submit session proposals through your event website
- Tracks management: manage the full call-for-speakers workflow from submission through content curation
- Multi-location support: manage events across multiple venues and organizers simultaneously
- Back-end to front-end: speaker bios and session descriptions auto-publish to your public event website

**Attendee Management**
- Custom registration questions per attendee or per subscription group
- Capacity management: min/max per session, group registrations
- Badge generation: customize badge templates, print in bulk
- Mobile check-in: scan QR-code badges from any smartphone

**Ticketing & Sales**
- Multi-ticket types (free, paid, early bird, member pricing, group)
- Online payment (credit card) and offline (invoice)
- Automated invoicing and cancellation policies
- Early bird and conditional pricing rules

**Event Website**
- Drag-and-drop page builder for each event
- Pre-built blocks for agenda, speaker bios, schedule, sponsors, location
- Full SEO configuration and Google Analytics integration
- SMS and email marketing for attendee communications

**Budget Management**
- Event budget and resource allocation directly within the event record
- Automated purchase orders from event resource requests
- Real-time event cost dashboard

#### CRM Module → Sponsor & Vendor Management

This is the gap that no other event-specific platform fills. Odoo's CRM handles it:

- Contact records for every sponsor, vendor, and partner organization
- Pipeline stages: prospecting → proposal sent → contract signed → deliverables due → invoiced → closed
- Sponsor tier custom fields (Gold, Silver, Bronze, etc.)
- Deliverable checklists linked to each contact
- Full communication history: every email, call, and meeting logged
- Automated follow-up activities and reminders
- Revenue forecasting by sponsor pipeline stage

#### Purchase Module → Vendor Operations

- Purchase orders for every vendor (AV company, caterer, setup crew, signage, etc.)
- Approval workflows before a PO is sent
- Vendor quotes and comparison
- Delivery scheduling and status tracking
- Three-way match: PO → receipt → invoice

#### Accounting Module → Full Financial Visibility

- Budget lines per event
- Vendor invoices linked to purchase orders
- Expense reports from staff
- Real-time P&L per event
- Multi-currency if needed

#### Project Module → Internal Task Coordination

- Projects per workstream (Sponsor Outreach, Venue Setup, Volunteer Coordination, etc.)
- Tasks with assignees, due dates, subtasks, time tracking
- Gantt view for timeline planning
- Kanban for day-to-day task management

#### HR Module → Team & Volunteer Management

- Employee/volunteer profiles and roles
- Shift scheduling (basic — not as granular as Engelsystem)
- Leave and attendance tracking

#### What Odoo Does NOT Do Well

- **No dedicated volunteer shift sign-up portal** — volunteers can't self-select shifts like Engelsystem allows. HR module is for employees, not external volunteers signing themselves up.
- **No purpose-built CFP review workflow** — Talk proposals can be submitted but the review/scoring/team workflow is simpler than Pretalx.
- **No room-by-room AV inventory tracking** — Indico has a dedicated room booking module; Odoo does not.
- **Enterprise modules are proprietary** — some advanced features (e.g., advanced website customizations, certain HR features) require Odoo Enterprise (paid). The Community Edition is fully functional but has a ceiling.
- **Steep learning curve** — Odoo is a full ERP. Non-technical users need training. Initial configuration takes real time.

#### License Note
The Community Edition is **LGPL-3.0** — fully free and open source. The Enterprise version adds proprietary modules on top. Self-hosting Community Edition has no per-user fees and no usage restrictions.

#### TCSW Coverage Score
| Workflow | Covered? |
|---|---|
| Session submission portal | ✅ Talk proposals |
| Review & approval workflow | ⚠️ Basic |
| Multi-track schedule builder | ✅ Tracks + multi-location |
| Public schedule page | ✅ Website builder |
| Speaker management | ✅ |
| Attendee registration | ✅ With custom questions |
| Ticket sales | ✅ Multi-type + payments |
| QR check-in | ✅ Mobile badge scan |
| Volunteer shift management | ⚠️ Basic (not self-sign-up) |
| Sponsor tracking + tiers | ✅ CRM module |
| Vendor contracts + POs | ✅ Purchase module |
| Internal task management | ✅ Project module |
| Budget tracking | ✅ Accounting module |
| Email/SMS communications | ✅ Built-in |
| Post-event analytics | ✅ Dashboards |

**13 of 14 workflows covered to some degree. 10 covered well.**

---

### 2. Pretalx
**GitHub:** https://github.com/pretalx/pretalx
**Stars:** ⭐ 914 · **License:** Apache 2.0
**Tech:** Python/Django + PostgreSQL
**Used by:** PyCon US, EuroPython, DjangoCon, FOSDEM — the standard for major open source conferences
**Note on star count:** This is a specialized professional tool. PyCon draws 2,500+ attendees and uses it. Star count reflects a niche audience, not quality.

#### What it does better than anything else

Pretalx owns one specific slice of the problem — getting from "we're opening a call for sessions" to "the public schedule is published" — and does it with a level of depth no other open-source tool matches.

**Call for Participation**
- Configurable public submission form with custom questions
- Multiple submission types (talk, workshop, panel, keynote) each with their own deadlines, questions, and rules
- Custom domain support — submitters see `sessions.yourevent.com`
- Multi-language submissions
- Partner orgs submit sessions → pretalx tracks each submission through its lifecycle

**Review & Curation Workflow**
- Assemble a review team (co-organizers, track leads, committee members)
- Reviewers score and comment independently before seeing others' scores (blind review option)
- Reviewer-specific questions ("Is this appropriate for a business audience?")
- Team discussion and vote on each submission
- Bulk accept/reject/request-revision actions

**Schedule Builder**
- Visual multi-track, multi-room, multi-day drag-and-drop editor
- Conflict detection: warns when a speaker is double-booked, or scheduled outside their availability window
- Speakers submit their own availability upfront — pretalx enforces it
- Schedule versioning: publish new versions as changes happen; attendees see a changelog
- Public schedule with RSS feed so attendees are notified of changes

**Speaker Communication**
- Email template system with variable substitution
- All emails go to an outbox for review before sending — no accidental mass emails
- Speaker profile pages with their bio, photo, session details, and resource downloads

**Integrations**
- Full REST API
- Exports: iCal, JSON, Frab/Pentabarf XML, static HTML
- **Engelsystem import**: volunteer coordinators can import the schedule directly to generate volunteer shifts
- Plugin system for custom extensions

#### What it does NOT do
- No attendee registration or ticketing (use Pretix alongside it)
- No sponsor or vendor management
- No volunteer coordination beyond schedule export
- No budget tracking

#### TCSW Fit
Pretalx is the right tool **specifically for the session submission and scheduling problem** — which is the hardest, most TCSW-specific workflow. It does not try to do everything. If Odoo's talk proposal management feels too lightweight for a multi-partner submission workflow with a real curation process, Pretalx runs alongside Odoo and handles that piece exclusively.

---

### 3. Engelsystem
**GitHub:** https://github.com/engelsystem/engelsystem
**Stars:** ⭐ 544 · **License:** GPL-2.0
**Tech:** PHP / MySQL
**Used by:** Chaos Communication Congress (10,000–20,000 attendees, every year since 2012), MozFest 2017, FrOSCon, 20+ European events
**Note on star count:** CCC is one of the largest hacker conferences in the world. Engelsystem has been tested at that scale annually for 13 years.

#### What it does

Engelsystem is the definitive open-source volunteer coordination system for large events. No other tool in this list handles the "50–100 volunteers spread across 10+ venues over 7 days" problem.

- **Teams/Departments:** Organize volunteers into functional teams (Registration Desk, Venue A Doors, AV Support, Info Booth, etc.) mapped to specific locations
- **Shift scheduling:** Define every shift across every venue for every day. Volunteers self-select the shifts they want.
- **Self-service portal:** Volunteers log in, see available shifts, sign up for what fits their schedule — no coordinator manually assigning everyone
- **Conflict detection:** System prevents a volunteer from signing up for overlapping shifts
- **iCal export:** Volunteers sync their personal shift schedule to their phone calendar
- **Pretalx import:** Directly imports session schedule from Pretalx — volunteer shifts automatically align with sessions
- **Day-of presence tracking:** Mark volunteers as arrived/departed per shift
- **Communications:** Built-in news/announcement system, Q&A system between volunteers and staff
- **Reward system:** Track volunteer hours, recognize contributors
- **Scales to thousands:** Per its own documentation, handles thousands of volunteers and tens of thousands of shift hours

#### TCSW Fit
If TCSW has 50–100 volunteers and uses Pretalx for scheduling, Engelsystem is the clean answer for volunteer coordination. The Pretalx import means no manual data re-entry. Volunteers self-manage their sign-ups, reducing coordinator workload significantly.

---

### 4. Indico (CERN)
**GitHub:** https://github.com/indico/indico
**Stars:** ⭐ 2,100 · **License:** MIT ✅
**Tech:** Python/Flask + PostgreSQL
**Used by:** CERN (900,000+ events logged), United Nations, World Health Organization, IEEE, 300+ institutions globally

#### The specific value: room and venue management

Indico's distinguishing feature is its **Room Booking module** — something no other open-source platform has at this depth:

- Define every room across every venue with capacity, AV equipment, floor plan, photos
- Book rooms with approval workflows (venue owner approves)
- Recurring bookings for weekly or daily setup sessions
- AV equipment inventory: who has the projector, when, at which location
- Room usage reporting

Beyond rooms, Indico handles full conference lifecycle:
- Registration with complex conditional form logic
- Drag-and-drop timetable editor (multi-track, multi-room, multi-day)
- Abstract/session submission and review
- Badge generation
- Built-in Zoom integration for hybrid sessions
- Full export/import compatibility (Frab XML, iCal, PDF)
- MIT license — the cleanest legal story of any platform here

#### TCSW Fit
Indico is the right tool if TCSW needs to track AV equipment across 15 venues, manage room bookings with partner venue approvals, and coordinate physical setup logistics. If those workflows are manual today, Indico solves them. If ticketing and sponsor management matter more, Odoo or the Pretalx/Pretix combination is the better primary tool.

---

### 5. Pretix
**GitHub:** https://github.com/pretix/pretix
**Stars:** ⭐ 2,400 · **License:** AGPL-3.0 + additional terms
**Used by:** FOSDEM (80,000 attendees), PyCon Europe, EuroPython, DjangoCon

Pretix is included as the best available ticketing layer, not a full platform. It handles the public-facing ticket shop and on-site check-in better than any other open-source option:

- Complex ticket types, capacity, add-ons, discounts, waitlists
- Native iOS + Android scanning apps for door check-in (offline-capable)
- **Exhibitor plugin:** assign vendor/sponsor booths, issue vouchers, enable lead scanning from booths
- 50+ payment method integrations
- Multi-event, multi-organizer (one installation, many events)

**TCSW Fit:** If Odoo's ticketing coverage is insufficient, or if TCSW needs the exhibitor/booth management features, Pretix runs as the standalone ticket shop while Odoo handles the operations backbone.

---

## Summary Comparison

| Workflow | Odoo | Pretalx | Engelsystem | Indico | Pretix |
|---|---|---|---|---|---|
| Session submission portal | ✅ | ✅ Best | ❌ | ✅ | ❌ |
| Review & curation workflow | ⚠️ | ✅ Best | ❌ | ✅ | ❌ |
| Multi-track schedule builder | ✅ | ✅ | ❌ | ✅ Best | ❌ |
| Public schedule page | ✅ | ✅ | ❌ | ✅ | ❌ |
| Speaker management | ✅ | ✅ | ❌ | ✅ | ❌ |
| Attendee registration | ✅ | ❌ | ❌ | ✅ | ✅ |
| Ticket sales | ✅ | ❌ | ❌ | ❌ | ✅ Best |
| QR check-in | ✅ | ❌ | ❌ | ❌ | ✅ Best |
| Volunteer shifts (self-signup) | ⚠️ | ❌ | ✅ Best | ❌ | ❌ |
| Sponsor tracking + tiers | ✅ Best | ❌ | ❌ | ❌ | ❌ |
| Vendor contracts + POs | ✅ Best | ❌ | ❌ | ❌ | ❌ |
| Internal task management | ✅ | ❌ | ❌ | ❌ | ❌ |
| Budget tracking | ✅ Best | ❌ | ❌ | ❌ | ❌ |
| Room/AV inventory | ❌ | ❌ | ❌ | ✅ Best | ❌ |
| Email/SMS to attendees | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| Native mobile apps | ⚠️ | ❌ | ❌ | ❌ | ✅ Scan only |

---

## Recommended Paths

### Path A: Odoo-Centered (Best Single Platform)
**Best for:** Teams who want one login, one database, and maximum operational coverage

```
Odoo Community (52k stars, LGPL)
├── Events module → session submissions, scheduling, ticketing, website
├── CRM module → sponsor pipeline, vendor contacts, deliverable tracking
├── Purchase module → vendor POs, contracts, approvals
├── Accounting → budget, invoices, expense tracking
├── Project → internal tasks and team assignments
└── HR → team and volunteer records

+ Engelsystem (for volunteer self-signup shifts, imports Odoo/Pretalx data)
+ Pretix (optional, only if Odoo ticketing is insufficient)
```

**Setup effort:** 3–5 weeks to configure properly. Odoo requires real configuration.
**Coverage:** 13/14 workflows addressed.

---

### Path B: Best-of-Breed Conference Stack
**Best for:** Teams who want purpose-built tools for each function, and are comfortable managing multiple systems

```
Pretalx (914 stars, Apache 2.0)
└── Session submissions → review → schedule → speaker comms → public agenda

Engelsystem (544 stars, GPL-2.0)
└── Imports from Pretalx → volunteer shifts, self-signup, iCal, day-of tracking

Pretix (2.4k stars, AGPL)
└── Public ticket sales → QR check-in (native iOS/Android apps)

Indico (2.1k stars, MIT) — optional
└── Room booking and AV inventory across venues

[Sponsor & Vendor Management]
└── CRM gap: Odoo, or externally in Airtable/Notion
```

**Setup effort:** 1–2 weeks per tool, less configuration per tool but more to coordinate.
**Coverage:** 12/14 workflows with better depth per function.

---

## The Real Benchmark: What Techstars Uses

Techstars, the organization that created the Startup Week format, built their own proprietary internal tool called **Preflight** for organizing startup weeks. This tells you something important: the problem is complex enough that even the creators of this event format built custom software.

No off-the-shelf open-source tool was good enough for them. The recommendation above is the closest you can get with genuinely open-source software.

---

## Decision

| If your biggest pain point is... | Use |
|---|---|
| Managing 100+ sessions from 50+ partner orgs | **Pretalx** as the primary tool |
| Sponsor/vendor tracking and budget visibility | **Odoo** as the primary tool |
| Volunteer coordination across venues | **Engelsystem** (non-negotiable for this) |
| Venue and AV resource management | **Indico** |
| You want one platform for everything | **Odoo** (covers the most ground) |
| You want the cleanest license (MIT) | **Indico** for primary, add others |

---

## Verified Sources

| Platform | URL | Stars | License |
|---|---|---|---|
| Odoo | https://github.com/odoo/odoo | ⭐ 52.2k | LGPL-3.0 |
| Pretix | https://github.com/pretix/pretix | ⭐ 2.4k | AGPL + terms |
| Indico | https://github.com/indico/indico | ⭐ 2.1k | MIT |
| Pretalx | https://github.com/pretalx/pretalx | ⭐ 914 | Apache 2.0 |
| Engelsystem | https://github.com/engelsystem/engelsystem | ⭐ 544 | GPL-2.0 |

*All star counts verified June 2026.*
