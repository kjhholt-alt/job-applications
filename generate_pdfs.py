"""
Resume PDF Generator
Generates professional, ATS-friendly PDF resumes from structured data.
Usage: python generate_pdfs.py
"""

import os
from fpdf import FPDF

FONT_DIR = "C:/Windows/Fonts"


class ResumePDF(FPDF):
    """Professional resume PDF with clean formatting."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=18)
        self.add_font("Cal", "", os.path.join(FONT_DIR, "calibri.ttf"))
        self.add_font("Cal", "B", os.path.join(FONT_DIR, "calibrib.ttf"))
        self.add_font("Cal", "I", os.path.join(FONT_DIR, "calibrii.ttf"))
        self.add_font("Cal", "BI", os.path.join(FONT_DIR, "calibriz.ttf"))
        self.F = "Cal"

    def header_section(self, name, address, phone, email):
        self.set_font(self.F, "B", 24)
        self.cell(0, 10, name, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font(self.F, "", 11)
        self.cell(0, 6, address, new_x="LMARGIN", new_y="NEXT", align="C")
        self.cell(0, 6, f"{phone}  |  {email}", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(3)

    def section_header(self, title):
        self.set_font(self.F, "B", 13)
        self.cell(0, 8, title.upper(), new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)

    def job_header(self, company_title, dates):
        self.set_font(self.F, "B", 11)
        title_w = self.w - self.l_margin - self.r_margin - 60
        self.cell(title_w, 6, company_title, new_x="RIGHT")
        self.set_font(self.F, "I", 11)
        self.cell(60, 6, dates, new_x="LMARGIN", new_y="NEXT", align="R")

    def job_location(self, location):
        self.set_font(self.F, "I", 10.5)
        self.cell(0, 5, location, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet(self, text):
        self.set_font(self.F, "", 10.5)
        x = self.l_margin
        bullet_indent = 5
        text_indent = 10
        self.set_x(x + bullet_indent)
        self.cell(text_indent - bullet_indent, 5.5, chr(8226), new_x="RIGHT")
        self.set_x(x + text_indent)
        available_w = self.w - self.r_margin - x - text_indent
        self.multi_cell(available_w, 5.5, text, align="L")
        self.ln(1)

    def project_entry(self, name, description):
        self.set_font(self.F, "", 10.5)
        x = self.l_margin
        bullet_indent = 5
        text_indent = 10
        self.set_x(x + bullet_indent)
        self.cell(text_indent - bullet_indent, 5.5, chr(8226), new_x="RIGHT")
        self.set_x(x + text_indent)
        available_w = self.w - self.r_margin - x - text_indent
        # Bold project name
        self.set_font(self.F, "B", 10.5)
        name_w = self.get_string_width(name + " ") + 1
        if name_w > available_w * 0.35:
            name_w = available_w * 0.35
        self.cell(name_w, 5.5, name + " ")
        # Regular description
        self.set_font(self.F, "", 10.5)
        remaining = available_w - name_w
        self.multi_cell(remaining, 5.5, description, align="L")
        self.ln(1)

    def skills_line(self, label, text):
        self.set_font(self.F, "B", 10.5)
        label_part = f"{label}: "
        label_w = self.get_string_width(label_part) + 1
        self.cell(label_w, 5.5, label_part)
        self.set_font(self.F, "", 10.5)
        available = self.w - self.r_margin - self.l_margin - label_w
        self.multi_cell(available, 5.5, text, align="L")
        self.ln(1)

    def gap(self):
        self.ln(2)

    def small_gap(self):
        self.ln(1)


def generate_finance_ai_manager():
    pdf = ResumePDF()
    pdf.add_page()
    pdf.set_margins(20, 15, 20)
    pdf.set_y(15)

    pdf.header_section(
        "Kruz J. Holt",
        "23 S Jacob Drive, Parkview, Iowa 52748",
        "563-343-1255",
        "kjh.holt@gmail.com",
    )

    # Education
    pdf.section_header("Education")
    pdf.job_header("University of Iowa, Iowa City, IA", "December 2020")
    pdf.set_font(pdf.F, "", 10.5)
    pdf.cell(0, 5.5, "B.A. Finance, Tippie College of Business (Direct Admit)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5.5, "College of Tippie GPA: 3.5/4.0", new_x="LMARGIN", new_y="NEXT")
    pdf.gap()

    # Professional Experience
    pdf.section_header("Professional Experience")

    pdf.job_header("John Deere Seeding \u2013 Operations Accounting Analyst", "February 2025 \u2013 Present")
    pdf.job_location("Davenport, Iowa")
    pdf.bullet("Own factory overhead budgets and lead monthly variance analysis reviews with plant leadership, translating operational changes into financial forecasts and actionable insights.")
    pdf.bullet("Develop automated reporting solutions using Power BI and Advanced Excel, driving cross-functional process improvement and reducing manual reporting effort.")
    pdf.bullet("Perform month-end close activities including expense classification, variance analysis, and standards alignment for accurate financial reporting.")
    pdf.bullet("Track and model factory headcount changes, connecting workforce data to overhead forecasts and supporting labor-related financial planning.")
    pdf.bullet("Support capital project tracking (AFE/AFL), validating requests and monitoring spend against approved budgets.")
    pdf.gap()

    pdf.job_header("John Deere Harvester \u2013 New Product Cost Analyst", "2024 \u2013 2025")
    pdf.job_location("Davenport, Iowa")
    pdf.bullet("Designed and deployed a Power BI dashboard used by engineering and program management to analyze monthly cost trends across new product programs.")
    pdf.bullet("Extracted and analyzed Bill of Materials (BoM) data from SAP for combines, front-end equipment, and seeding programs, providing cost estimates for new product development.")
    pdf.bullet("Tracked capital expenditures across multiple programs, ensuring accurate financial management and budget compliance.")
    pdf.gap()

    pdf.job_header("John Deere Financial \u2013 Accounts Receivable Analyst", "2023 \u2013 2024")
    pdf.job_location("Des Moines, Iowa")
    pdf.bullet("Pioneered automation of financial workflows using Power Automate and SQL, eliminating manual steps and delivering measurable efficiency gains across the AR function.")
    pdf.bullet("Managed completion of 57 monthly financial tasks with zero errors, demonstrating precision in high-volume financial operations.")
    pdf.bullet("Developed training programs for new team members, establishing standardized processes and fostering a knowledge-sharing culture.")
    pdf.bullet("Performed reconciliations in SAP and uploaded certified data in Blackline; leveraged ESSBASE to analyze daily and monthly lease volumes.")
    pdf.gap()

    pdf.job_header("John Deere Corporate \u2013 General Ledger / Fixed Asset Shared Services", "Summer 2022 \u2013 2023")
    pdf.job_location("Davenport, Iowa")
    pdf.bullet("Conducted reconciliations for all international units, ensuring accurate financial reporting across global operations.")
    pdf.bullet("Analyzed leases and collaborated with international units on calculations and reconciliation; compiled data for annual 10-K report.")
    pdf.gap()

    pdf.job_header("Principal Global Investors \u2013 Investment Operations Intern", "Summer 2018 \u2013 Winter 2019")
    pdf.job_location("Des Moines, Iowa")
    pdf.bullet("Calculated performance of hundreds of composites with millions in AUM for GIPS compliance using Bloomberg, Excel, and Sylvan.")
    pdf.bullet("Collaborated across Fixed Income, Equity, and Real Estate boutiques to produce verified performance data.")
    pdf.gap()

    # AI & Technology Projects
    pdf.section_header("AI & Technology Projects")
    pdf.set_font(pdf.F, "I", 10)
    pdf.multi_cell(0, 5.5, "Independently designed, built, and deployed production applications using generative AI and modern web technologies.", align="L")
    pdf.ln(3)
    pdf.project_entry("AI Finance Brief \u2014", "Next.js SaaS generating personalized financial briefings via Claude AI API, with authentication (NextAuth) and email delivery (Resend). Deployed on Vercel.")
    pdf.project_entry("Trade Journal \u2014", "Full-stack trade analytics platform (Next.js + Python FastAPI) with AI-powered analysis, performance visualization, and automated insight generation.")
    pdf.project_entry("Automated Trading System \u2014", "Python quantitative trading bot with real-time data pipeline, scoring engine (Kelly criterion, VWAP, momentum), risk management, and Supabase analytics. Deployed on Railway.")
    pdf.project_entry("CRM Platforms \u2014", "React + Django full-stack CRMs for outdoor services and franchise management with dashboards, PDF generation, and offline-first mobile design.")
    pdf.gap()

    # Leadership
    pdf.section_header("Leadership & AI Advocacy")
    pdf.job_header("AI Lunch & Learn Facilitator \u2013 John Deere Ag & Turf Accounting", "2024 \u2013 Present")
    pdf.bullet("Lead quarterly AI sessions for the entire Ag & Turf accounting function, covering generative AI developments, finance-specific use cases, and live tool demonstrations to drive enterprise AI adoption.")
    pdf.small_gap()
    pdf.set_font(pdf.F, "B", 11)
    pdf.cell(0, 6, "Development Committee Member \u2013 John Deere Accounting Organization", new_x="LMARGIN", new_y="NEXT")
    pdf.bullet("Contribute to talent development and organizational growth initiatives.")
    pdf.gap()

    # Skills
    pdf.section_header("Technical Skills")
    pdf.skills_line("AI & Analytics", "Generative AI (Claude API, prompt engineering), Power BI, Power Automate, Advanced Excel, SQL, Python (pandas), quantitative modeling")
    pdf.skills_line("Finance Systems", "SAP, Blackline, ESSBASE, Bloomberg")
    pdf.skills_line("Development", "Python, TypeScript/JavaScript, React, Next.js, Django, FastAPI, REST APIs, Supabase (PostgreSQL), Git")
    pdf.skills_line("Cloud & DevOps", "Vercel, Railway, CI/CD, agile development practices")

    out = "C:/Users/Kruz/Desktop/Projects/job-applications/applications/deloitte-finance-ai-manager/Kruz_Holt_Resume_Deloitte_Finance_AI.pdf"
    pdf.output(out)
    print(f"Created: {out}")


def generate_ai_solutions_leader():
    pdf = ResumePDF()
    pdf.add_page()
    pdf.set_margins(20, 15, 20)
    pdf.set_y(15)

    pdf.header_section(
        "Kruz J. Holt",
        "23 S Jacob Drive, Parkview, Iowa 52748",
        "563-343-1255",
        "kjh.holt@gmail.com",
    )

    # Education
    pdf.section_header("Education")
    pdf.job_header("University of Iowa, Iowa City, IA", "December 2020")
    pdf.set_font(pdf.F, "", 10.5)
    pdf.cell(0, 5.5, "B.A. Finance, Tippie College of Business (Direct Admit)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5.5, "College of Tippie GPA: 3.5/4.0", new_x="LMARGIN", new_y="NEXT")
    pdf.gap()

    # AI & Technology Portfolio
    pdf.section_header("AI & Technology Portfolio")
    pdf.set_font(pdf.F, "I", 10)
    pdf.multi_cell(0, 5.5, "Independently designed, architected, and deployed 10+ production applications using generative AI, full-stack web technologies, and cloud infrastructure. Hands-on across the entire lifecycle: requirements, architecture, engineering, deployment, and optimization.", align="L")
    pdf.ln(3)

    pdf.set_font(pdf.F, "B", 11)
    pdf.cell(0, 6, "AI-Powered SaaS Applications (2024 \u2013 Present)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.project_entry("AI Finance Brief \u2014", "Production SaaS: Next.js 14, Claude AI API, NextAuth, Resend. Personalized financial briefings via generative AI with structured output parsing. Deployed on Vercel with CI/CD.")
    pdf.project_entry("AI Chess Coach \u2014", "Production app: Next.js 14, chess.js, Lichess API, Claude AI. Real-time game analysis with AI coaching. Custom prompt architecture for domain-specific reasoning.")
    pdf.project_entry("Trade Journal \u2014", "Full-stack: Next.js 14 + Python FastAPI. AI-powered trade analysis, performance visualization (Recharts), automated insights. Vercel + Railway deployment.")
    pdf.gap()

    pdf.set_font(pdf.F, "B", 11)
    pdf.cell(0, 6, "Automated Trading System \u2014 \"MoneyPrinter\" (2025 \u2013 Present)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.bullet("Architected and deployed a Python quantitative trading bot for prediction markets with real-time data pipelines, multi-strategy execution, and automated risk management.")
    pdf.bullet("Built scoring engine incorporating momentum analysis, VWAP signals, and Kelly criterion position sizing with dynamic confidence thresholds per asset class.")
    pdf.bullet("Engineered parallel strategy execution (4.1x speedup), batch order processing, and per-asset rate limiters \u2014 reduced cycle times from 17s to 2.6s.")
    pdf.bullet("Implemented production monitoring: Supabase analytics backend, automated watchdog with health checks and self-healing deployment, Discord bot for remote management.")
    pdf.gap()

    pdf.set_font(pdf.F, "B", 11)
    pdf.cell(0, 6, "Full-Stack Platforms & Infrastructure (2024 \u2013 Present)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.project_entry("CRM Systems \u2014", "React 19 + Django full-stack CRMs with lead discovery engines, job scheduling, PDF invoicing, offline-first mobile (IndexedDB), and analytics dashboards.")
    pdf.project_entry("Admin Dashboard \u2014", "Next.js 15 agent management system with Supabase backend, real-time monitoring, and Zustand state management.")
    pdf.project_entry("Automation \u2014", "Browser automation (Puppeteer, Playwright), web scraping pipelines (Selenium, BeautifulSoup), Discord-integrated AI agent system with cron scheduling.")
    pdf.gap()

    # Professional Experience
    pdf.section_header("Professional Experience")

    pdf.job_header("John Deere Seeding \u2013 Operations Accounting Analyst", "February 2025 \u2013 Present")
    pdf.job_location("Davenport, Iowa")
    pdf.bullet("Own factory overhead budgets and deliver monthly variance analysis to plant leadership, translating operational data into financial forecasts and actionable insights.")
    pdf.bullet("Build automated reporting dashboards using Power BI and Advanced Excel, supporting cross-functional process improvement and data-driven decision making.")
    pdf.gap()

    pdf.job_header("John Deere Harvester \u2013 New Product Cost Analyst", "2024 \u2013 2025")
    pdf.job_location("Davenport, Iowa")
    pdf.bullet("Designed and deployed Power BI dashboard for engineering and program management, enabling self-service monthly cost analysis across new product programs.")
    pdf.bullet("Extracted and analyzed SAP BoM data, providing cost estimates for new product development across combines, front-end equipment, and seeding.")
    pdf.gap()

    pdf.job_header("John Deere Financial \u2013 Accounts Receivable Analyst", "2023 \u2013 2024")
    pdf.job_location("Des Moines, Iowa")
    pdf.bullet("Pioneered automation of financial workflows using Power Automate and SQL, delivering measurable efficiency gains. Managed 57 monthly tasks; SAP reconciliations and ESSBASE analysis.")
    pdf.gap()

    pdf.job_header("John Deere Corporate \u2013 GL / Fixed Asset Shared Services", "Summer 2022 \u2013 2023")
    pdf.job_location("Davenport, Iowa")
    pdf.bullet("International unit reconciliations, lease analysis, and financial data compilation for annual 10-K SEC reporting.")
    pdf.gap()

    pdf.job_header("Principal Global Investors \u2013 Investment Operations Intern", "Summer 2018 \u2013 Winter 2019")
    pdf.job_location("Des Moines, Iowa")
    pdf.bullet("Performance analysis across hundreds of composites using Bloomberg, Excel, and Sylvan for GIPS compliance.")
    pdf.gap()

    # Leadership
    pdf.section_header("Leadership & AI Advocacy")
    pdf.job_header("AI Lunch & Learn Facilitator \u2013 John Deere Ag & Turf Accounting", "2024 \u2013 Present")
    pdf.bullet("Lead quarterly AI sessions for the Ag & Turf accounting organization, demonstrating GenAI tools, use cases, and driving enterprise AI adoption.")
    pdf.gap()

    # Skills
    pdf.section_header("Technical Skills")
    pdf.skills_line("AI/ML & GenAI", "Claude AI API, prompt engineering & architecture, quantitative modeling, AI workflow automation, generative AI application development")
    pdf.skills_line("Languages", "Python, TypeScript/JavaScript, SQL, HTML/CSS")
    pdf.skills_line("Frontend", "React, Next.js (14/15), Tailwind CSS, shadcn/ui, Framer Motion, Recharts")
    pdf.skills_line("Backend", "Django (DRF), FastAPI, Node.js, REST API design & implementation")
    pdf.skills_line("Data & Cloud", "Supabase (PostgreSQL), pandas, Vercel, Railway, Git/GitHub, CI/CD, Docker")
    pdf.skills_line("Finance Tools", "SAP, Blackline, ESSBASE, Bloomberg, Power BI, Power Automate, Advanced Excel")

    out = "C:/Users/Kruz/Desktop/Projects/job-applications/applications/deloitte-ai-solutions-leader/Kruz_Holt_Resume_Deloitte_AI_Solutions.pdf"
    pdf.output(out)
    print(f"Created: {out}")


if __name__ == "__main__":
    generate_finance_ai_manager()
    generate_ai_solutions_leader()
    print("\nDone! Both PDFs generated.")
