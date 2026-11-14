"""One-off content/navigation pass on Portfolio/index.html (recruiter-first rewrite).
Idempotent guard: refuses to run twice."""
import re, pathlib

P = pathlib.Path(__file__).resolve().parent.parent / "Portfolio" / "index.html"
h = P.read_text(encoding="utf-8")
assert "rohan-portfolio-custom" not in h, "already applied"

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f"expected {count} of {old[:60]!r}, found {n}"
    h = h.replace(old, new)

def rex(pat, new, count=1, flags=re.S):
    global h
    h, n = re.subn(pat, new, h, flags=flags)
    assert n == count, f"regex {pat[:50]!r}: expected {count}, got {n}"

# ---------- head: marker + description ----------
rep('<meta charset="UTF-8" />', '<meta charset="UTF-8" />\n    <meta name="site-source" content="rohan-portfolio-custom" />')
rex(r'<meta name="description" content="[^"]*" />',
    '<meta name="description" content="Rohan Dharlapally is a backend software engineer working with Python, Django REST Framework, PostgreSQL and Frappe. Projects: Hostel Hunt, NXdesk and Eskoolia." />')

# ---------- section ids + menu targets ----------
rep('<section class="banner-three-area">', '<section id="home" class="banner-three-area">')
rep('<li><a class="color-active" href="#">Home</a></li>', '<li><a class="color-active" href="#home">Home</a></li>')
rep('<li><a class="tw-text-lg text-white" href="#">Home,</a></li>', '<li><a class="tw-text-lg text-white" href="#home">Home,</a></li>')
rep('<li><a class="tw-text-lg text-white" href="#contact">Contact</a></li>', '<li><a class="tw-text-lg text-white" href="#experience">Experience,</a></li>\n                        <li><a class="tw-text-lg text-white" href="#contact">Contact</a></li>')
rep('<section id="stack" ', '<section id="skills" ')
rep('href="#stack" tabindex="-1"', 'href="#skills" tabindex="-1"', count=h.count('href="#stack" tabindex="-1"'))

# ---------- hero ----------
rex(r"Hello! I'm Rohan <br />\s*Dharlapally\. A backend software engineer from\s*Hyderabad\.",
    "Hi, I&rsquo;m Rohan Dharlapally. <br /> A backend software engineer from Hyderabad.")
rep("APIs, access control and booking logic that stay correct.", "Backend APIs, databases and access control, built with care.")
rep("Backend tests on the latest branch", "Backend test functions in Hostel Hunt, latest branch")

# ---------- about ----------
rex(r"I build the parts of software that have to stay correct: access control, booking concurrency, payments and background jobs\.",
    "I build backend systems for real applications, from a hostel booking platform to company ERP software.")
paras = [
    "I&rsquo;m a backend software engineer from Hyderabad, and I graduated in Computer Science in 2026. I mainly work with Python, Django REST Framework and PostgreSQL, building APIs, login and permissions, and the databases behind them.",
    "As an App Developer Intern at Sria Infotech, I built the Academics and Library modules of Eskoolia, a school ERP. I also worked on access control and architecture for NXdesk, a Frappe-based ERP and Helpdesk platform, and proposed growing it from a single Helpdesk customization into a set of connected company applications.",
    "Outside work I built Hostel Hunt, a hostel booking platform with a Django backend, an owner dashboard and a Flutter app. In college I guided a team of four in the Smart India Hackathon, which taught me how to plan, present and coordinate a project with other people.",
]
it = iter(paras)
rex(r'(<p class="tw-text-xl tw-mb-10">).*?(</p>)', lambda m: m.group(1) + "\n                        " + next(it) + "\n                      " + m.group(2), count=3)

# ---------- what I do ----------
for old, new in [("Data & Tenancy", "Databases & Data Modelling"), ("Enterprise Platforms", "Enterprise Applications"), ("Ops & Quality", "Testing & Delivery")]:
    rep(f">{old}</a", f">{new}</a")
for old, new in [("Tenant scoping", "Supabase"), ("Roles & permissions", "Roles & permissions"), ("CI", "Automated tests"), ("Sentry", "GitHub Actions"), ("Locust", "Git workflow")]:
    rex(rf'(<a\s+class="text-uppercase text-white tw-text-sm[^>]*href="#"\s*>){re.escape(old)}(</a)', rf"\g<1>{new}\g<2>", count=1)
h = h.replace('href="#works"\n                  ><img', 'href="#skills"\n                  ><img')  # service images -> skills
# service title links go to the skills section, not Works
rex(r'(<h2\s+class="service-three-title[^>]*>\s*<a )href="#works"', r'\g<1>href="#skills"', count=4)

# ---------- explainer wording ----------
rep("Hostel Hunt · booking locks", "Hostel Hunt · a technical challenge")
rep("No double-booking, step by step.", "How Hostel Hunt stops two students booking the same bed.")

# ---------- experience & leadership ----------
items = [
    ("01", "Sria Infotech", "Eskoolia (school ERP): built the Academics and Library modules", "2026", "feat-1.jpg"),
    ("02", "Sria Infotech", "NXdesk: proposed the app ecosystem and worked on access control", "2026", "feat-3.jpg"),
    ("03", "Hostel Hunt", "Solo developer: Django backend, owner dashboard and Flutter app", "2026", "feat-4.jpg"),
    ("04", "Smart India Hackathon", "Guided a team of four: planning, problem analysis and pitching", "College", "feat-2.jpg"),
    ("05", "Education", "B.Tech, Computer Science (AI &amp; ML), Malla Reddy College of Engineering", "2022 &ndash; 2026", "feat-2.jpg"),
]
rows = ""
for i, (n, who, what, yr, img) in enumerate(items):
    cur = " current" if i == 0 else ""
    rows += f'''                  <div class="feature-three-single{cur} hover__reveal-item" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="200">
                    <div class="feature-three-item d-flex justify-content-between align-items-center">
                      <div class="feature-three-left d-flex align-items-center">
                        <div><span class="feature-three-text tw-text-605 fw-medium text-white tw-transition-3 d-inline-block tw-w-20">{n}</span></div>
                        <div><span class="feature-three-text tw-text-605 fw-medium text-white tw-transition-3 d-inline-block rd-w-col">{who}</span></div>
                        <div><span class="feature-three-text tw-text-605 fw-medium text-white tw-transition-3 d-inline-block">{what}</span></div>
                      </div>
                      <div><span class="feature-three-text tw-text-605 fw-medium text-white tw-transition-3 d-inline-block rd-nowrap">{yr}</span></div>
                    </div>
                    <div class="hover__reveal-bg bg-img" data-background-image="assets/images/rd/{img}"></div>
                  </div>
'''
rex(r'(<div class="feature-three-wrapper hover__widget">\n).*?(                </div>\n              </div>\n            </div>\n          </div>\n        </div>\n        <section class="testimonial)',
    lambda m: m.group(1) + rows + m.group(2))
rep("Experience &amp; education", "Experience and leadership")
rep("An internship, described exactly.", "What I have worked on, and my role in it.")

# ---------- practices slider ----------
rep("Four habits, each tied to real code in a public repository.", "Engineering practices I follow in Hostel Hunt.")
rep("No double-booking</h2>", "Safe bed reservations</h2>")
rep("Tenant isolation</h2>", "Keeping each owner&rsquo;s data separate</h2>")
rep("Payments that can be replayed safely</h2>", "Reliable payment handling</h2>")
rep("Operable by default</h2>", "Monitoring and backups</h2>")

# ---------- skills ----------
rep("Skills sorted by evidence, not by bars", "Technical skills")
rep(">Built<", ">Used in my projects<")
rep("Used to ship Hostel Hunt or the Eskoolia modules", "Hostel Hunt and the Eskoolia modules")
rep(">Worked with<", ">Used in company codebases<")
rep("Day-to-day exposure inside real codebases", "Frappe platform work and the Eskoolia codebase")
rep(">Exposure<", ">Familiar with<")
rep("Seen or used lightly", "Used lightly or studied")

# ---------- architecture & system design (new section, before the footer) ----------
def ul(xs): return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
arch = f'''        <section id="architecture" class="rd-arch bg-black py-120 position-relative z-1">
          <div class="container tw-container-1800-px">
            <div class="row justify-content-center tw-mb-21">
              <div class="col-xl-9">
                <div class="text-center">
                  <p class="rd-eyebrow">Architecture and system design</p>
                  <h2 class="text-white tw-text-15 tw-itm-title tw-itm-anim">What I built, what I proposed, and what I studied.</h2>
                </div>
              </div>
            </div>
            <div class="rd-arch-grid">
              <div class="rd-arch-col" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="200">
                <span class="rd-badge rd-badge-built">Built</span>
                <h3 class="font-heading">Implemented in code</h3>
                {ul(["Row-level locking so two students cannot reserve the same bed (Hostel Hunt)",
                     "Owner-level data scoping in queries, lookups and serializers (Hostel Hunt)",
                     "Razorpay sandbox payments with signed, repeat-safe webhooks (Hostel Hunt)",
                     "A PostgreSQL outbox with cron workers for background jobs (Hostel Hunt)",
                     "Academics and Library modules inside a multi-tenant Django ERP (Eskoolia)"])}
              </div>
              <div class="rd-arch-col" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="300">
                <span class="rd-badge rd-badge-proposed">Proposed</span>
                <h3 class="font-heading">Designed, not built</h3>
                {ul(["A six-application NXdesk ecosystem behind one entry page and sign-in",
                     "Application-level access control with role-based authorization",
                     "A database per application, with a shared database only for selected data",
                     "API-based integration between applications",
                     "Event-driven synchronization and shared read models (CQRS)",
                     "A hybrid of these database approaches"])}
                <p class="rd-arch-note">These are design proposals. None of them is a deployed production system.</p>
              </div>
              <div class="rd-arch-col" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="400">
                <span class="rd-badge rd-badge-studied">Studied</span>
                <h3 class="font-heading">Explored while working</h3>
                {ul(["Celery and Redis task workflows, including worker discovery and scheduled jobs (Eskoolia)",
                     "Tenant context and data isolation patterns (Eskoolia)",
                     "RBAC and ABAC permission models",
                     "Docker, CI/CD and release workflows for company projects"])}
              </div>
            </div>
          </div>
        </section>
'''
rep("</main>", arch + "        </main>")

# ---------- progress bar + page marker ----------
rep('<a class="rd-skip" href="#main">Skip to content</a>', '<a class="rd-skip" href="#main">Skip to content</a>\n    <div class="rd-progress" aria-hidden="true"></div>')

P.write_text(h, encoding="utf-8")
print("index.html updated:", len(h), "chars")
