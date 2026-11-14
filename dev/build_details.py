"""Builds the three project pages from Portfolio/index.html (same header, preloader, footer).
Usage: python dev/build_details.py     (reads and writes ../Portfolio)"""
import re, pathlib

site = pathlib.Path(__file__).resolve().parent.parent / "Portfolio"
idx = (site / "index.html").read_text(encoding="utf-8")
assert "rohan-portfolio-custom" in idx

a = idx.index('<div id="smooth-wrapper">')
b = idx.index('<section id="contact" role="contentinfo"')
prefix = idx[:a] + '<div id="smooth-wrapper">\n      <div id="smooth-content">\n'
footer = idx[b:]

def fix_links(s):
    for h in ("home", "about", "services", "works", "experience", "skills", "architecture"):
        s = s.replace(f'href="#{h}"', f'href="index.html#{h}"')
    return s
# the footer's own contact section stays on-page
prefix, footer = fix_links(prefix), fix_links(footer)
prefix = prefix.replace('<a class="rd-skip" href="index.html#main">', '<a class="rd-skip" href="#main">')
IMG = "assets/images/rd/"

def tags(items): return '<ul class="rd-tags">' + "".join(f"<li>{t}</li>" for t in items) + "</ul>"
def meta(items): return '<dl class="rd-meta">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in items) + "</dl>"
def bullets(items): return '<ul class="rd-list">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"
def glance(rows): return '<dl class="rd-glance">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows) + "</dl>"
def cards(items):
    out = '<div class="rd-grid2">'
    for t, body, note in items:
        out += f'<div class="rd-card"><h3>{t}</h3><p>{body}</p>' + (f"<small>{note}</small>" if note else "") + "</div>"
    return out + "</div>"
def block(eyebrow, title, inner, dark=False, id_=""):
    i = f' id="{id_}"' if id_ else ""
    return f'''<section class="rd-block{' rd-dark' if dark else ''}"{i}><div class="container tw-container-1800-px"><p class="rd-eyebrow">{eyebrow}</p><h2>{title}</h2>{inner}</div></section>'''
def shots(kind, items):
    return f'<div class="rd-shots {kind}">' + "".join(f'<figure><img src="{IMG}{f}" alt="{alt}" loading="lazy" /><figcaption>{cap}</figcaption></figure>' for f, alt, cap in items) + "</div>"
def hero(title, kind, tag_list, lead, meta_items, badge=""):
    return f'''<section class="rd-detail"><div class="container tw-container-1800-px">
<a class="rd-backlink" href="index.html#works">&larr; Back to all work</a>
{badge}
<h1 class="rd-title">{title}</h1>
<p class="rd-kind">{kind}</p>
{tags(tag_list)}
<p class="rd-lead">{lead}</p>
{meta(meta_items)}
</div></section>'''
def nxt(current):
    pages = [("hostel-hunt", "Hostel Hunt", "Hostel and PG booking platform"),
             ("eskoolia", "Eskoolia", "School ERP, Academics and Library modules"),
             ("nxdesk", "NXdesk", "Frappe-based enterprise application ecosystem")]
    links = "".join(f'<a href="{s}.html"><h3>{t}</h3><p>{k}</p></a>' for s, t, k in pages if s != current)
    return f'<section class="rd-block"><div class="container tw-container-1800-px"><p class="rd-eyebrow">More work</p><div class="rd-next">{links}</div></div></section>'
def h3(t): return f'<h3 style="font-size:clamp(24px,2.4vw,34px);margin:0 0 18px;font-family:var(--heading-font),sans-serif">{t}</h3>'

GH_BACK = "https://github.com/rohanaarup/hostel-hunt-admin-pannel"
GH_APP = "https://github.com/rohanaarup/Hostel-hunt-app"

explainer = '''<div class="rd-ex">
  <div class="rd-ex-stage">
    <div class="rd-ex-lane" id="ex-a"><span class="rd-ex-who">Student A</span><strong class="rd-ex-state"></strong></div>
    <div class="rd-ex-arrow" aria-hidden="true">&rarr;</div>
    <div class="rd-ex-bed" id="ex-bed"><span class="rd-ex-who">Room 204 &middot; Bed B</span><strong class="rd-ex-state"></strong></div>
    <div class="rd-ex-arrow" aria-hidden="true">&larr;</div>
    <div class="rd-ex-lane" id="ex-b"><span class="rd-ex-who">Student B</span><strong class="rd-ex-state"></strong></div>
  </div>
  <p class="rd-ex-cap" id="ex-cap" aria-live="polite"></p>
  <div class="rd-ex-ctl">
    <button type="button" class="rd-btn" data-act="back">Back</button>
    <button type="button" class="rd-btn rd-btn-main" data-act="next">Next step</button>
    <button type="button" class="rd-btn rd-btn-ghost" data-act="reset">Restart</button>
    <span class="rd-ex-note">An illustration of the pattern (select_for_update with SKIP LOCKED), not live data.</span>
  </div></div>'''

# ============================ Hostel Hunt ============================
hh = hero(
    "Hostel Hunt", "A hostel and PG booking platform for Hyderabad", ["Pre-launch, on staging", "Solo project"],
    "Students find a bed, reserve it and pay rent in one app. Owners manage rooms, bookings and dues in a web dashboard. I designed and built the backend, the dashboard and the mobile app myself.",
    [("My role", "Solo developer"), ("Status", "Pre-launch. Runs on a staging server. Not on the Play Store yet."),
     ("Main technologies", "Django REST Framework &middot; PostgreSQL (Supabase) &middot; Flutter &middot; Next.js"),
     ("Source code", f'<a href="{GH_BACK}" target="_blank" rel="noopener">Backend and admin &nearr;</a> &nbsp; <a href="{GH_APP}" target="_blank" rel="noopener">Flutter app &nearr;</a>')],
    badge=f'<div class="rd-brandbadge"><img src="{IMG}hh-logo.png" alt="Hostel Hunt logo" /></div>')
hh += block("Project summary", "Problem, solution and my contribution", glance([
    ("Problem", "Finding a bed in a hostel or PG, reserving it and paying rent usually takes several separate steps, and owners have to keep track of who has booked and who has paid."),
    ("Solution", "One platform with three connected parts: a Flutter app for students, a Next.js dashboard for owners, and a Django REST API with a PostgreSQL database behind both."),
    ("My contribution", "I built all three parts: the API and data model, login with email OTP and JWT, bed booking, sandbox payments with Razorpay, background jobs, the admin dashboard, the mobile app, automated tests and the deployment pipeline."),
    ("Technology", "Python 3.13, Django 5.2, Django REST Framework, PostgreSQL on Supabase, SimpleJWT, Razorpay (sandbox), Cloudinary, Next.js 16, React 19, TypeScript, Tailwind CSS, Flutter, Dart, Riverpod, GitHub Actions, Render, Sentry."),
    ("Current status", "Running on staging and installed on test devices. Payments work in sandbox mode only. The newest rent and stay features are on separate branches that are not merged into main yet."),
]))
hh += block("Technical challenges", "Problems I had to solve, and how", cards([
    ("Reserving a bed safely", "Two students must never get the same bed. Booking uses database row locks (select_for_update with SKIP LOCKED) and holds that expire if the student does not pay. Tests cover two students competing for one bed.", ""),
    ("Login and OTP", "Students sign in with an email one-time code, and the API issues JWT tokens that can be refreshed and revoked. Requests are rate limited, and tests check that the code is never exposed in a response.", ""),
    ("Payments that can be repeated safely", "Razorpay sends the same webhook more than once. The API verifies the signature, confirms each payment only once, reconciles mismatches and includes a replay tool for testing.", "Sandbox mode only. No live payments."),
    ("Keeping owners&rsquo; data separate", "Each owner may only see their own hostels. Scoping is applied in queries, in object lookups and when validating input, and a Django check flags any model that is not scoped.", ""),
    ("Background jobs without a message broker", "Reminders and cleanup run from a PostgreSQL outbox processed by cron workers, with retries, backoff and duplicate protection. The job is saved in the same transaction as the change that caused it.", ""),
    ("API contracts and database changes", "The API is versioned under /api/v1 with generated OpenAPI documentation and contract tests. The database uses UUID keys, constraints, indexes and about 40 migrations on the latest branch.", ""),
]))
hh += block("Interactive example", "How a bed is reserved without double-booking", explainer, dark=True, id_="booking")
hh += block("The product", "Student app and owner dashboard",
    '<p>Screens from the rent and stay features, shown with sample data. These features are on branches that are not merged into main yet.</p>' + shots("phones", [
        ("hh-my-stay.png", "My stay screen showing room, rent and next due date", "My stay"),
        ("hh-pay-rent.png", "Pay rent screen with UPI and card options", "Pay rent"),
        ("hh-rent-paid.png", "Rent paid confirmation", "Payment confirmation"),
        ("hh-receipt.png", "Rent receipt", "Receipt"),
        ("hh-reminders.png", "Lock-screen rent reminders at 7, 3 and 1 days before and on the due date", "Rent reminders"),
        ("hh-calendar.png", "Payment calendar for October", "Payment calendar"),
        ("hh-history.png", "Payment history list", "Payment history"),
        ("hh-analytics.png", "Stay analytics with paid-by-month bars", "Stay analytics")]) +
    '<div id="owner" style="height:60px"></div>' + h3("Owner dashboard") + shots("wide", [
        ("hh-admin-dues.png", "Admin panel: stays and dues with overdue, payable, scheduled and paid statuses", "Stays and dues: who has paid, who is due soon and who is overdue."),
        ("hh-admin-offline.png", "Record offline payment dialog", "Recording a cash payment. The student sees it as recorded by the owner.")]))
hh += block("Testing and quality assurance", "How the code is checked",
    bullets(["GitHub Actions runs the backend checks on every change, using PostgreSQL 16 and Redis 7 service containers.",
             "Staging-only Locust load tests with pass and fail thresholds.",
             "Sentry monitors errors in the backend and the Flutter app, and the API has a /healthz endpoint.",
             "Daily database backups, encrypted with age and kept for 30 days."]) +
    '<h3 style="margin:40px 0 14px;font-size:24px;font-family:var(--heading-font),sans-serif">Automated tests in the repository</h3>'
    '<p>Counted by reading the code on 2026-11-12. These are the numbers of test functions and files that exist, not a record of passing runs. I did not execute the test suite for this page.</p>'
    '<div class="rd-tablewrap"><table class="rd-table"><thead><tr><th>Measure</th><th>main branch</th><th>phase-9-admin-panel branch</th></tr></thead><tbody>'
    '<tr><td>Backend test functions</td><td>392</td><td>1,070</td></tr><tr><td>Backend test files</td><td>44</td><td>62</td></tr>'
    '<tr><td>Database migrations</td><td>35</td><td>40</td></tr><tr><td>Django app directories</td><td>11</td><td>13 (including core)</td></tr>'
    '<tr><td>Admin dashboard test files</td><td>8</td><td>12</td></tr></tbody></table></div><p style="margin-top:14px;opacity:.7">The Flutter app has 35 test files on main.</p>')
hh += block("Status and lessons learned", "Where the project stands",
    '<div class="rd-grid2"><div>' + h3("What debugging taught me") + bullets([
        "A missing booking ID in an API response broke the payment flow. Fixing it showed me why API contracts need tests.",
        "A Django secret key appeared in server logs. I rotated it and changed how environment variables are handled.",
        "Login state was lost in some app flows, which I fixed and covered with tests."]) +
    '</div><div>' + h3("What is still to do") + bullets([
        "Launch the app on the Play Store.",
        "Test payments end to end on staging before using live mode.",
        "Merge the rent and stay branches into main.",
        "Host the owner dashboard. The mobile app is the priority."]) + "</div></div>")
hh += nxt("hostel-hunt")

# ============================ Eskoolia ============================
esk = hero(
    "Eskoolia", "School ERP: Academics and Library modules", ["Company project", "Two modules built"],
    "Eskoolia is an established school management platform with about 15 modules. As an intern at Sria Infotech I built its Academics and Library modules and contributed to the project&rsquo;s knowledge-transfer documents.",
    [("My role", "Developer on the team, responsible for two modules"), ("Employer", "Sria Infotech, App Developer Intern"),
     ("Time spent", "About one and a half months"), ("Technologies", "Django &middot; Django REST Framework &middot; PostgreSQL &middot; Celery &middot; Redis")])
esk += block("Project summary", "What Eskoolia is and what I did", glance([
    ("The product", "A multi-tenant school ERP. One deployment serves many schools, and each school has its own data, roles and permissions."),
    ("My contribution", "I built the Academics module and the Library module, and contributed to the knowledge-transfer (KT) material that helps other developers learn the codebase."),
    ("What I did not do", "Eskoolia is a large product that I joined, not one I own. The other modules, such as admissions, fees and examinations, were not my work."),
    ("Technology", "Django and Django REST Framework on PostgreSQL, with Celery and Redis for background tasks."),
    ("Status", "An existing product that the team continues to develop."),
]) + '<div style="height:36px"></div>' + shots("wide", [("eskoolia-dashboard.png", "Eskoolia dashboard listing its modules, with sample data", "The Eskoolia dashboard. Screens on this page use sample data and are shown with the employer&rsquo;s permission.")]))
esk += block("My contribution", "The two modules I built", cards([
    ("Academics", "Foundation setup, staff assignment, a class timetable, a planning studio for chapters, lessons, homework and syllabus, and reports.", "Section names as shown in the product navigation."),
    ("Library", "Console, catalogue, acquisitions, periods and occupancy, issue desk, lost and damaged items, members, transactions and logs, reports and stock check.", "Section names as shown in the product navigation.")]) +
    '<div style="height:30px"></div>' + shots("wide", [
        ("eskoolia-timetable.png", "Class timetable with clash-safe teacher assignment", "Class timetable. Teacher clashes are blocked before an assignment is made, and there is an auto-generate option."),
        ("eskoolia-planning.png", "Planning Studio showing sections with chapters, lessons and homework", "Planning Studio: chapters, lessons, homework and syllabus for every class and subject.")]))
esk += block("What I learned", "Knowledge transfer and enterprise concepts",
    '<div class="rd-grid2"><div>' + h3("Knowledge-transfer material") + bullets([
        "Helped write the material that lets other developers understand the codebase.",
        "Traced how models map to database tables and how the roughly 15 modules relate to each other."]) +
    '</div><div>' + h3("Concepts I studied while working") + bullets([
        "Multi-tenancy: how a request gets its school context and how data stays separate.",
        "Role-based and attribute-based access control (RBAC and ABAC).",
        "Celery and Redis background tasks, including scheduled jobs.",
        "Database performance in an existing schema."]) + "</div></div>")
esk += nxt("eskoolia")

# ============================ NXdesk ============================
nx = hero(
    "NXdesk", "A Frappe-based ecosystem of company applications", ["In development", "Team project", "Architecture proposal"],
    "NXdesk began as a plan to adapt Frappe Helpdesk for internal use. I proposed turning it into a wider set of connected applications behind one entry page, with access control at the application level.",
    [("My role", "Proposed the ecosystem direction; worked on access control and architecture"), ("Employer", "Sria Infotech, App Developer Intern"),
     ("Status", "In development. The screen shown is an early draft."), ("Platform", "Frappe Framework &middot; ERPNext &middot; Frappe Helpdesk")])
nx += block("Project summary", "From one Helpdesk to an application ecosystem", glance([
    ("Where it started", "The company wanted to take the existing Frappe Helpdesk repository and adapt it for internal use, with fairly small customizations."),
    ("What I proposed", "Treat Helpdesk as the first of several applications instead of a one-off customization: one entry page and sign-in, shared platform services, clear boundaries between applications, and access that follows each person&rsquo;s role."),
    ("My contribution", "The ecosystem proposal, plus analysis and design work on Frappe&rsquo;s multi-app, single-site setup, roles and permissions, and how people should be routed after they sign in."),
    ("Technology", "Frappe Framework, ERPNext and Frappe Helpdesk (Python, Vue)."),
    ("Current status", "A team product in development. The entry page below is an early draft, and the multi-application architecture is a proposal, not a finished system."),
]) + '<div style="height:36px"></div>' + shots("wide", [("nx-entry.png", "NXdesk entry page with NXERP and Sria Helpdesk product cards", "The NXdesk entry page: one sign-in to the company&rsquo;s applications. An early draft of a product still being built.")]))
nx += block("My work areas", "What I worked on in the Frappe platform",
    '<p>These are the areas I worked on. The implementation lives in the company&rsquo;s repository, which is private, so no code or internal details are shown here.</p>' + bullets([
        "Frappe Framework and Frappe Helpdesk integration.",
        "Multi-app, single-site architecture.",
        "Role and DocType permissions, user permissions and module visibility.",
        "Server-side access enforcement for direct URLs and APIs.",
        "Routing people to the right application after sign-in.",
        "Keeping customer-portal data separate from internal data.",
        "Frontend customization and shared platform navigation.",
        "Helpdesk workflow requirements: unseen-ticket indicators, Team-based Assignee selection, and comment and @mention notifications (written as specifications)."]))
nx += block("Architecture proposal", "The proposed six-application ecosystem",
    '<span class="rd-chip-proposal">Proposal only</span><p>The ideas below are system designs I explored and proposed. None of them is built or running in production.</p>' + cards([
        ("One entry page, many applications", "A single place to sign in, showing only the applications a person is allowed to use.", ""),
        ("Database per application", "Each application owns its data, with a shared database only for information that really is common.", ""),
        ("API-based integration", "Applications read each other&rsquo;s data through APIs instead of reaching into each other&rsquo;s tables.", ""),
        ("Event-driven synchronization", "Changes are published as events so other applications can keep a copy up to date.", ""),
        ("Shared read models (CQRS)", "Read-optimized views that combine data from several applications for dashboards and search.", ""),
        ("Hybrid approach", "A mix of the options above, chosen per application, based on how much data must be shared.", "")]))
nx += block("Delivery planning", "How the team would ship it safely", bullets([
    "A phased implementation plan and architecture decision records.",
    "A Git workflow with main, develop and feature branches and pull requests.",
    "CI/CD and Docker considerations, role and endpoint testing, and regression checks.",
    "Release and rollback runbooks."]))
nx += nxt("nxdesk")

pages = {"hostel-hunt": ("Hostel Hunt · Rohan Dharlapally", hh), "eskoolia": ("Eskoolia · Rohan Dharlapally", esk), "nxdesk": ("NXdesk · Rohan Dharlapally", nx)}
for slug, (title, content) in pages.items():
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", prefix, flags=re.S)
    (site / f"{slug}.html").write_text(head + '<main id="main">' + content + "</main>\n" + footer, encoding="utf-8")
    print("wrote", slug + ".html")

