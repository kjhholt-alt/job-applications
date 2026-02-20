"""
Generate crisp PDF resumes and cover letters using HTML + WeasyPrint.
No blurriness — vector text rendering at full quality.
Usage: python generate_final_pdfs.py
"""

import weasyprint
import os

DESKTOP = r"C:\Users\Kruz\Desktop"

RESUME_CSS = """
@page {
    size: letter;
    margin: 0.6in 0.75in 0.5in 0.75in;
}
body {
    font-family: Calibri, 'Segoe UI', Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.4;
    color: #000;
    margin: 0;
}
h1 {
    text-align: center;
    font-size: 22pt;
    margin: 0 0 2pt 0;
    font-weight: bold;
}
.contact {
    text-align: center;
    font-size: 10.5pt;
    margin: 0 0 4pt 0;
}
.section-header {
    font-size: 12pt;
    font-weight: bold;
    text-transform: uppercase;
    border-bottom: 1.5pt solid #000;
    padding-bottom: 2pt;
    margin-top: 10pt;
    margin-bottom: 6pt;
}
.job-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-top: 6pt;
    margin-bottom: 0;
}
.job-title {
    font-weight: bold;
    font-size: 11pt;
}
.job-dates {
    font-style: italic;
    font-size: 11pt;
    white-space: nowrap;
}
.job-location {
    font-style: italic;
    font-size: 10pt;
    margin: 0 0 3pt 0;
}
ul {
    margin: 2pt 0 0 0;
    padding-left: 18pt;
}
li {
    margin-bottom: 2pt;
    font-size: 10.5pt;
}
.project-name {
    font-weight: bold;
}
.skills-label {
    font-weight: bold;
}
.italic-intro {
    font-style: italic;
    font-size: 10pt;
    margin-bottom: 6pt;
}
.subsection {
    font-weight: bold;
    font-size: 11pt;
    margin-top: 8pt;
    margin-bottom: 3pt;
}
.edu-line {
    font-size: 10.5pt;
    margin: 0;
}
.skills-block p {
    margin: 2pt 0;
}
"""

COVER_CSS = """
@page {
    size: letter;
    margin: 1in;
}
body {
    font-family: Calibri, 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #000;
    margin: 0;
}
h1 {
    text-align: center;
    font-size: 18pt;
    margin: 0 0 2pt 0;
    font-weight: bold;
}
.contact {
    text-align: center;
    font-size: 10.5pt;
    margin: 0;
}
.spacer { height: 16pt; }
.address-block p {
    margin: 2pt 0;
}
.body-para {
    margin-bottom: 10pt;
    text-align: left;
}
.closing {
    margin-top: 16pt;
}
.sig {
    font-weight: bold;
    margin-top: 6pt;
}
"""


def finance_ai_resume_html():
    return """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>

<h1>Kruz J. Holt</h1>
<p class="contact">23 S Jacob Drive, Parkview, Iowa 52748</p>
<p class="contact">563-343-1255 &nbsp;|&nbsp; kjh.holt@gmail.com</p>

<div class="section-header">Education</div>
<div class="job-row">
    <span class="job-title">University of Iowa, Iowa City, IA</span>
    <span class="job-dates">December 2020</span>
</div>
<p class="edu-line">B.A. Finance, Tippie College of Business (Direct Admit)</p>
<p class="edu-line">College of Tippie GPA: 3.5/4.0</p>

<div class="section-header">Professional Experience</div>

<div class="job-row">
    <span class="job-title">John Deere Seeding &ndash; Operations Accounting Analyst</span>
    <span class="job-dates">February 2025 &ndash; Present</span>
</div>
<p class="job-location">Davenport, Iowa</p>
<ul>
    <li>Own factory overhead budgets and lead monthly variance analysis reviews with plant leadership, translating operational changes into financial forecasts and actionable insights.</li>
    <li>Develop automated reporting solutions using Power BI and Advanced Excel, driving cross-functional process improvement and reducing manual reporting effort.</li>
    <li>Perform month-end close activities including expense classification, variance analysis, and standards alignment for accurate financial reporting.</li>
    <li>Track and model factory headcount changes, connecting workforce data to overhead forecasts and supporting labor-related financial planning.</li>
    <li>Support capital project tracking (AFE/AFL), validating requests and monitoring spend against approved budgets.</li>
</ul>

<div class="job-row">
    <span class="job-title">John Deere Harvester &ndash; New Product Cost Analyst</span>
    <span class="job-dates">2024 &ndash; 2025</span>
</div>
<p class="job-location">Davenport, Iowa</p>
<ul>
    <li>Designed and deployed a Power BI dashboard used by engineering and program management to analyze monthly cost trends across new product programs.</li>
    <li>Extracted and analyzed Bill of Materials (BoM) data from SAP for combines, front-end equipment, and seeding programs, providing cost estimates for new product development.</li>
    <li>Tracked capital expenditures across multiple programs, ensuring accurate financial management and budget compliance.</li>
</ul>

<div class="job-row">
    <span class="job-title">John Deere Financial &ndash; Accounts Receivable Analyst</span>
    <span class="job-dates">2023 &ndash; 2024</span>
</div>
<p class="job-location">Des Moines, Iowa</p>
<ul>
    <li>Pioneered automation of financial workflows using Power Automate and SQL, eliminating manual steps and delivering measurable efficiency gains across the AR function.</li>
    <li>Managed completion of 57 monthly financial tasks with zero errors, demonstrating precision in high-volume financial operations.</li>
    <li>Developed training programs for new team members, establishing standardized processes and fostering a knowledge-sharing culture.</li>
    <li>Performed reconciliations in SAP and uploaded certified data in Blackline; leveraged ESSBASE to analyze daily and monthly lease volumes.</li>
</ul>

<div class="job-row">
    <span class="job-title">John Deere Corporate &ndash; General Ledger / Fixed Asset Shared Services</span>
    <span class="job-dates">Summer 2022 &ndash; 2023</span>
</div>
<p class="job-location">Davenport, Iowa</p>
<ul>
    <li>Conducted reconciliations for all international units, ensuring accurate financial reporting across global operations.</li>
    <li>Analyzed leases and collaborated with international units on calculations and reconciliation; compiled data for annual 10-K report.</li>
</ul>

<div class="job-row">
    <span class="job-title">Principal Global Investors &ndash; Investment Operations Intern</span>
    <span class="job-dates">Summer 2018 &ndash; Winter 2019</span>
</div>
<p class="job-location">Des Moines, Iowa</p>
<ul>
    <li>Calculated performance of hundreds of composites with millions in AUM for GIPS compliance using Bloomberg, Excel, and Sylvan.</li>
    <li>Collaborated across Fixed Income, Equity, and Real Estate boutiques to produce verified performance data.</li>
</ul>

<div class="section-header">AI &amp; Technology Projects</div>
<p class="italic-intro">Independently designed, built, and deployed production applications using generative AI and modern web technologies.</p>
<ul>
    <li><span class="project-name">AI Finance Brief &mdash;</span> Next.js SaaS generating personalized financial briefings via Claude AI API, with authentication (NextAuth) and email delivery (Resend). Deployed on Vercel.</li>
    <li><span class="project-name">Trade Journal &mdash;</span> Full-stack trade analytics platform (Next.js + Python FastAPI) with AI-powered analysis, performance visualization, and automated insight generation.</li>
    <li><span class="project-name">Automated Trading System &mdash;</span> Python quantitative trading bot with real-time data pipeline, scoring engine (Kelly criterion, VWAP, momentum), risk management, and Supabase analytics. Deployed on Railway.</li>
    <li><span class="project-name">CRM Platforms &mdash;</span> React + Django full-stack CRMs for outdoor services and franchise management with dashboards, PDF generation, and offline-first mobile design.</li>
</ul>

<div class="section-header">Leadership &amp; AI Advocacy</div>
<div class="job-row">
    <span class="job-title">AI Lunch &amp; Learn Facilitator &ndash; John Deere Ag &amp; Turf Accounting</span>
    <span class="job-dates">2024 &ndash; Present</span>
</div>
<ul>
    <li>Lead quarterly AI sessions for the entire Ag &amp; Turf accounting function, covering generative AI developments, finance-specific use cases, and live tool demonstrations to drive enterprise AI adoption.</li>
</ul>
<p class="subsection">Development Committee Member &ndash; John Deere Accounting Organization</p>
<ul>
    <li>Contribute to talent development and organizational growth initiatives.</li>
</ul>

<div class="section-header">Technical Skills</div>
<div class="skills-block">
    <p><span class="skills-label">AI &amp; Analytics:</span> Generative AI (Claude API, prompt engineering), Power BI, Power Automate, Advanced Excel, SQL, Python (pandas), quantitative modeling</p>
    <p><span class="skills-label">Finance Systems:</span> SAP, Blackline, ESSBASE, Bloomberg</p>
    <p><span class="skills-label">Development:</span> Python, TypeScript/JavaScript, React, Next.js, Django, FastAPI, REST APIs, Supabase (PostgreSQL), Git</p>
    <p><span class="skills-label">Cloud &amp; DevOps:</span> Vercel, Railway, CI/CD, agile development practices</p>
</div>

</body></html>"""


def ai_solutions_resume_html():
    return """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>

<h1>Kruz J. Holt</h1>
<p class="contact">23 S Jacob Drive, Parkview, Iowa 52748</p>
<p class="contact">563-343-1255 &nbsp;|&nbsp; kjh.holt@gmail.com</p>

<div class="section-header">Education</div>
<div class="job-row">
    <span class="job-title">University of Iowa, Iowa City, IA</span>
    <span class="job-dates">December 2020</span>
</div>
<p class="edu-line">B.A. Finance, Tippie College of Business (Direct Admit)</p>
<p class="edu-line">College of Tippie GPA: 3.5/4.0</p>

<div class="section-header">AI &amp; Technology Portfolio</div>
<p class="italic-intro">Independently designed, architected, and deployed 10+ production applications using generative AI, full-stack web technologies, and cloud infrastructure. Hands-on across the entire lifecycle: requirements, architecture, engineering, deployment, and optimization.</p>

<p class="subsection">AI-Powered SaaS Applications (2024 &ndash; Present)</p>
<ul>
    <li><span class="project-name">AI Finance Brief &mdash;</span> Production SaaS: Next.js 14, Claude AI API, NextAuth, Resend. Personalized financial briefings via generative AI with structured output parsing. Deployed on Vercel with CI/CD.</li>
    <li><span class="project-name">AI Chess Coach &mdash;</span> Production app: Next.js 14, chess.js, Lichess API, Claude AI. Real-time game analysis with AI coaching. Custom prompt architecture for domain-specific reasoning.</li>
    <li><span class="project-name">Trade Journal &mdash;</span> Full-stack: Next.js 14 + Python FastAPI. AI-powered trade analysis, performance visualization (Recharts), automated insights. Vercel + Railway deployment.</li>
</ul>

<p class="subsection">Automated Trading System &mdash; &ldquo;MoneyPrinter&rdquo; (2025 &ndash; Present)</p>
<ul>
    <li>Architected and deployed a Python quantitative trading bot for prediction markets with real-time data pipelines, multi-strategy execution, and automated risk management.</li>
    <li>Built scoring engine incorporating momentum analysis, VWAP signals, and Kelly criterion position sizing with dynamic confidence thresholds per asset class.</li>
    <li>Engineered parallel strategy execution (4.1x speedup), batch order processing, and per-asset rate limiters &mdash; reduced cycle times from 17s to 2.6s.</li>
    <li>Implemented production monitoring: Supabase analytics backend, automated watchdog with health checks and self-healing deployment, Discord bot for remote management.</li>
</ul>

<p class="subsection">Full-Stack Platforms &amp; Infrastructure (2024 &ndash; Present)</p>
<ul>
    <li><span class="project-name">CRM Systems &mdash;</span> React 19 + Django full-stack CRMs with lead discovery engines, job scheduling, PDF invoicing, offline-first mobile (IndexedDB), and analytics dashboards.</li>
    <li><span class="project-name">Admin Dashboard &mdash;</span> Next.js 15 agent management system with Supabase backend, real-time monitoring, and Zustand state management.</li>
    <li><span class="project-name">Automation &mdash;</span> Browser automation (Puppeteer, Playwright), web scraping pipelines (Selenium, BeautifulSoup), Discord-integrated AI agent system with cron scheduling.</li>
</ul>

<div class="section-header">Professional Experience</div>

<div class="job-row">
    <span class="job-title">John Deere Seeding &ndash; Operations Accounting Analyst</span>
    <span class="job-dates">February 2025 &ndash; Present</span>
</div>
<p class="job-location">Davenport, Iowa</p>
<ul>
    <li>Own factory overhead budgets and deliver monthly variance analysis to plant leadership, translating operational data into financial forecasts and actionable insights.</li>
    <li>Build automated reporting dashboards using Power BI and Advanced Excel, supporting cross-functional process improvement and data-driven decision making.</li>
</ul>

<div class="job-row">
    <span class="job-title">John Deere Harvester &ndash; New Product Cost Analyst</span>
    <span class="job-dates">2024 &ndash; 2025</span>
</div>
<p class="job-location">Davenport, Iowa</p>
<ul>
    <li>Designed and deployed Power BI dashboard for engineering and program management, enabling self-service monthly cost analysis across new product programs.</li>
    <li>Extracted and analyzed SAP BoM data, providing cost estimates for new product development across combines, front-end equipment, and seeding.</li>
</ul>

<div class="job-row">
    <span class="job-title">John Deere Financial &ndash; Accounts Receivable Analyst</span>
    <span class="job-dates">2023 &ndash; 2024</span>
</div>
<p class="job-location">Des Moines, Iowa</p>
<ul>
    <li>Pioneered automation of financial workflows using Power Automate and SQL, delivering measurable efficiency gains. Managed 57 monthly tasks; SAP reconciliations and ESSBASE analysis.</li>
</ul>

<div class="job-row">
    <span class="job-title">John Deere Corporate &ndash; GL / Fixed Asset Shared Services</span>
    <span class="job-dates">Summer 2022 &ndash; 2023</span>
</div>
<p class="job-location">Davenport, Iowa</p>
<ul>
    <li>International unit reconciliations, lease analysis, and financial data compilation for annual 10-K SEC reporting.</li>
</ul>

<div class="job-row">
    <span class="job-title">Principal Global Investors &ndash; Investment Operations Intern</span>
    <span class="job-dates">Summer 2018 &ndash; Winter 2019</span>
</div>
<p class="job-location">Des Moines, Iowa</p>
<ul>
    <li>Performance analysis across hundreds of composites using Bloomberg, Excel, and Sylvan for GIPS compliance.</li>
</ul>

<div class="section-header">Leadership &amp; AI Advocacy</div>
<div class="job-row">
    <span class="job-title">AI Lunch &amp; Learn Facilitator &ndash; John Deere Ag &amp; Turf Accounting</span>
    <span class="job-dates">2024 &ndash; Present</span>
</div>
<ul>
    <li>Lead quarterly AI sessions for the Ag &amp; Turf accounting organization, demonstrating GenAI tools, use cases, and driving enterprise AI adoption.</li>
</ul>

<div class="section-header">Technical Skills</div>
<div class="skills-block">
    <p><span class="skills-label">AI/ML &amp; GenAI:</span> Claude AI API, prompt engineering &amp; architecture, quantitative modeling, AI workflow automation, generative AI application development</p>
    <p><span class="skills-label">Languages:</span> Python, TypeScript/JavaScript, SQL, HTML/CSS</p>
    <p><span class="skills-label">Frontend:</span> React, Next.js (14/15), Tailwind CSS, shadcn/ui, Framer Motion, Recharts</p>
    <p><span class="skills-label">Backend:</span> Django (DRF), FastAPI, Node.js, REST API design &amp; implementation</p>
    <p><span class="skills-label">Data &amp; Cloud:</span> Supabase (PostgreSQL), pandas, Vercel, Railway, Git/GitHub, CI/CD, Docker</p>
    <p><span class="skills-label">Finance Tools:</span> SAP, Blackline, ESSBASE, Bloomberg, Power BI, Power Automate, Advanced Excel</p>
</div>

</body></html>"""


def finance_ai_cover_html():
    return """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>

<h1>Kruz J. Holt</h1>
<p class="contact">23 S Jacob Drive, Parkview, Iowa 52748</p>
<p class="contact">563-343-1255 &nbsp;|&nbsp; kjh.holt@gmail.com</p>

<div class="spacer"></div>

<div class="address-block">
    <p>February 20, 2026</p>
    <div class="spacer"></div>
    <p>Deloitte Recruiting</p>
    <p>Finance Transformation &mdash; Finance Analytics &amp; AI Manager</p>
    <div class="spacer"></div>
    <p>Dear Hiring Team,</p>
</div>

<div class="spacer"></div>

<p class="body-para">I&rsquo;m applying for the Finance Analytics &amp; AI Manager position on Deloitte&rsquo;s Finance Transformation team. What drew me to this role is that it sits at the exact intersection of my career: I&rsquo;ve spent four years in core finance at John Deere &mdash; FP&amp;A, reporting, cost analysis, month-end close &mdash; and I&rsquo;ve independently built and deployed production AI applications that solve real business problems. I don&rsquo;t just talk about AI in finance. I build it.</p>

<p class="body-para">At John Deere, I&rsquo;ve worked across the finance function: overhead budgeting and variance analysis at the factory level, new product cost estimation using SAP BoM data, accounts receivable automation with Power Automate and SQL, and international reconciliations for 10-K reporting. I designed Power BI dashboards that replaced manual reporting cycles and are used daily by engineers and program managers. This gives me the finance process fluency your clients need &mdash; I understand the pain points because I&rsquo;ve lived them.</p>

<p class="body-para">Outside of my day job, I&rsquo;ve architected and deployed over 10 full-stack applications using generative AI. My AI Finance Brief app uses Claude&rsquo;s API to generate personalized financial briefings &mdash; the kind of AI-enabled finance insight your team delivers to CFOs. My automated trading system processes real-time market data through a quantitative scoring engine with dynamic risk management, deployed on cloud infrastructure with automated monitoring. These aren&rsquo;t side projects &mdash; they&rsquo;re production systems with real users and real money. I&rsquo;ve worked across the full AI solution lifecycle: identifying the use case, designing the architecture, building the solution, deploying to cloud, and iterating based on performance data.</p>

<p class="body-para">I lead quarterly AI Lunch &amp; Learn sessions for John Deere&rsquo;s entire Ag &amp; Turf accounting function, covering generative AI news, practical finance use cases, and live tool demonstrations. Helping others understand and adopt AI is something I genuinely enjoy &mdash; and it&rsquo;s directly relevant to the client-facing and mentorship aspects of this role.</p>

<p class="body-para">I recognize my background is non-traditional for this level. My finance degree isn&rsquo;t STEM-designated, and my years of experience are weighted toward the early side of your range. But a candidate who has both deep finance process knowledge AND the ability to personally build the AI solutions &mdash; not just manage their delivery &mdash; brings unusual value to a Finance Analytics &amp; AI team.</p>

<p class="body-para">I&rsquo;d welcome the opportunity to discuss how my combination of finance expertise and hands-on AI development can contribute to Deloitte&rsquo;s Finance Transformation practice.</p>

<p class="closing">Sincerely,</p>
<p class="sig">Kruz J. Holt</p>

</body></html>"""


def ai_solutions_cover_html():
    return """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>

<h1>Kruz J. Holt</h1>
<p class="contact">23 S Jacob Drive, Parkview, Iowa 52748</p>
<p class="contact">563-343-1255 &nbsp;|&nbsp; kjh.holt@gmail.com</p>

<div class="spacer"></div>

<div class="address-block">
    <p>February 20, 2026</p>
    <div class="spacer"></div>
    <p>Deloitte Recruiting</p>
    <p>Human Capital &mdash; AI Solutions Leader</p>
    <div class="spacer"></div>
    <p>Dear Hiring Team,</p>
</div>

<div class="spacer"></div>

<p class="body-para">I&rsquo;m applying for the AI Solutions Leader position within Deloitte&rsquo;s Human Capital practice. While my years of experience don&rsquo;t match a traditional senior hire, I want to make the case that what I bring is harder to find: I&rsquo;m a finance professional who independently architects, builds, and deploys production AI systems end-to-end &mdash; and I understand business problems well enough to know which ones AI should actually solve.</p>

<p class="body-para">Over the past two years, I&rsquo;ve designed, built, and deployed 10+ production applications spanning the complete technology stack. My AI-powered SaaS applications use generative AI APIs with custom prompt architecture, modern frontend frameworks (Next.js, React, TypeScript), Python backends (Django, FastAPI), and cloud deployment (Vercel, Railway, Supabase). My automated trading system is the most technically demanding: a Python quantitative engine with real-time data pipelines, parallel strategy execution (4.1x speedup), dynamic risk management using Kelly criterion, and production monitoring with automated health checks and self-healing deployment. I&rsquo;ve managed the full lifecycle on every project &mdash; requirements, architecture, engineering, deployment, and continuous optimization.</p>

<p class="body-para">Building production systems teaches you things that theoretical knowledge doesn&rsquo;t. I&rsquo;ve designed prompt architectures for domain-specific AI reasoning, built data pipelines that handle structured and unstructured sources, implemented rate limiting and caching for API-heavy applications, and made infrastructure decisions around cost, latency, and reliability. I&rsquo;ve also learned when NOT to use AI &mdash; my trading system removed a signal that was circular because I measured its actual impact. This kind of practical AI judgment is what your clients need.</p>

<p class="body-para">Four years at John Deere gave me deep understanding of enterprise finance: FP&amp;A, cost analysis, financial reporting, SEC compliance, and process automation. I&rsquo;ve automated workflows with Power Automate and SQL, built Power BI dashboards for cross-functional teams, and worked in SAP across multiple business units. When consulting with leaders on AI solutions, I can speak their language &mdash; I&rsquo;ve sat in their seat.</p>

<p class="body-para">I lead quarterly AI Lunch &amp; Learn sessions for John Deere&rsquo;s Ag &amp; Turf accounting organization, demonstrating generative AI tools and driving enterprise adoption. Making technical concepts accessible to non-technical stakeholders is something I do today and would bring to client engagements at Deloitte.</p>

<p class="body-para">I&rsquo;m transparent that my experience profile is earlier-career than your posting describes. But the AI landscape has shifted &mdash; practical building experience with generative AI matters more than years on a resume, and candidates who can both sell an AI vision and personally build the solution are rare. I&rsquo;m one of them.</p>

<p class="body-para">I&rsquo;d be excited to discuss how my hands-on AI development experience and finance domain knowledge can contribute to Deloitte&rsquo;s Human Capital AI practice.</p>

<p class="closing">Sincerely,</p>
<p class="sig">Kruz J. Holt</p>

</body></html>"""


if __name__ == "__main__":
    docs = [
        ("Kruz_Holt_Resume_Deloitte_Finance_AI.pdf", finance_ai_resume_html(), RESUME_CSS),
        ("Kruz_Holt_Resume_Deloitte_AI_Solutions.pdf", ai_solutions_resume_html(), RESUME_CSS),
        ("Kruz_Holt_Cover_Letter_Deloitte_Finance_AI.pdf", finance_ai_cover_html(), COVER_CSS),
        ("Kruz_Holt_Cover_Letter_Deloitte_AI_Solutions.pdf", ai_solutions_cover_html(), COVER_CSS),
    ]

    for filename, html, css in docs:
        path = os.path.join(DESKTOP, filename)
        wp = weasyprint.HTML(string=html)
        wp.write_pdf(path, stylesheets=[weasyprint.CSS(string=css)])
        print(f"Created: {filename}")

    print("\nDone! All 4 crisp PDFs on your Desktop.")
