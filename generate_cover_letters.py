"""
Cover Letter PDF Generator
Usage: python generate_cover_letters.py
"""

import os
from fpdf import FPDF

FONT_DIR = "C:/Windows/Fonts"


class CoverLetterPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)
        self.add_font("Cal", "", os.path.join(FONT_DIR, "calibri.ttf"))
        self.add_font("Cal", "B", os.path.join(FONT_DIR, "calibrib.ttf"))
        self.add_font("Cal", "I", os.path.join(FONT_DIR, "calibrii.ttf"))
        self.F = "Cal"


def generate_finance_ai_cover():
    pdf = CoverLetterPDF()
    pdf.add_page()
    pdf.set_margins(28, 22, 28)
    pdf.set_y(22)

    pdf.set_font(pdf.F, "B", 20)
    pdf.cell(0, 10, "Kruz J. Holt", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font(pdf.F, "", 11)
    pdf.cell(0, 6, "23 S Jacob Drive, Parkview, Iowa 52748", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, "563-343-1255  |  kjh.holt@gmail.com", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    pdf.set_font(pdf.F, "", 11.5)
    pdf.cell(0, 7, "February 20, 2026", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(0, 7, "Deloitte Recruiting", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Finance Transformation \u2014 Finance Analytics & AI Manager", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(7)

    pdf.cell(0, 7, "Dear Hiring Team,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    w = pdf.w - pdf.l_margin - pdf.r_margin

    paras = [
        "I'm applying for the Finance Analytics & AI Manager position on Deloitte's Finance Transformation team. What drew me to this role is that it sits at the exact intersection of my career: I've spent four years in core finance at John Deere \u2014 FP&A, reporting, cost analysis, month-end close \u2014 and I've independently built and deployed production AI applications that solve real business problems. I don't just talk about AI in finance. I build it.",

        "At John Deere, I've worked across the finance function: overhead budgeting and variance analysis at the factory level, new product cost estimation using SAP BoM data, accounts receivable automation with Power Automate and SQL, and international reconciliations for 10-K reporting. I designed Power BI dashboards that replaced manual reporting cycles and are used daily by engineers and program managers. This gives me the finance process fluency your clients need \u2014 I understand the pain points because I've lived them.",

        "Outside of my day job, I've architected and deployed over 10 full-stack applications using generative AI. My AI Finance Brief app uses Claude's API to generate personalized financial briefings \u2014 the kind of AI-enabled finance insight your team delivers to CFOs. My automated trading system processes real-time market data through a quantitative scoring engine with dynamic risk management, deployed on cloud infrastructure with automated monitoring. These aren't side projects \u2014 they're production systems with real users and real money. I've worked across the full AI solution lifecycle: identifying the use case, designing the architecture, building the solution, deploying to cloud, and iterating based on performance data.",

        "I lead quarterly AI Lunch & Learn sessions for John Deere's entire Ag & Turf accounting function, covering generative AI news, practical finance use cases, and live tool demonstrations. Helping others understand and adopt AI is something I genuinely enjoy \u2014 and it's directly relevant to the client-facing and mentorship aspects of this role.",

        "I recognize my background is non-traditional for this level. My finance degree isn't STEM-designated, and my years of experience are weighted toward the early side of your range. But a candidate who has both deep finance process knowledge AND the ability to personally build the AI solutions \u2014 not just manage their delivery \u2014 brings unusual value to a Finance Analytics & AI team.",

        "I'd welcome the opportunity to discuss how my combination of finance expertise and hands-on AI development can contribute to Deloitte's Finance Transformation practice.",
    ]

    pdf.set_font(pdf.F, "", 11.5)
    for para in paras:
        pdf.multi_cell(w, 6.5, para, align="L")
        pdf.ln(4)

    pdf.ln(3)
    pdf.cell(0, 7, "Sincerely,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font(pdf.F, "B", 11.5)
    pdf.cell(0, 7, "Kruz J. Holt", new_x="LMARGIN", new_y="NEXT")

    out = "C:/Users/Kruz/Desktop/Projects/job-applications/applications/deloitte-finance-ai-manager/Kruz_Holt_Cover_Letter_Deloitte_Finance_AI.pdf"
    pdf.output(out)
    print(f"Created: {out}")


def generate_ai_solutions_cover():
    pdf = CoverLetterPDF()
    pdf.add_page()
    pdf.set_margins(28, 22, 28)
    pdf.set_y(22)

    pdf.set_font(pdf.F, "B", 20)
    pdf.cell(0, 10, "Kruz J. Holt", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font(pdf.F, "", 11)
    pdf.cell(0, 6, "23 S Jacob Drive, Parkview, Iowa 52748", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, "563-343-1255  |  kjh.holt@gmail.com", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    pdf.set_font(pdf.F, "", 11.5)
    pdf.cell(0, 7, "February 20, 2026", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(0, 7, "Deloitte Recruiting", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Human Capital \u2014 AI Solutions Leader", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(7)

    pdf.cell(0, 7, "Dear Hiring Team,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    w = pdf.w - pdf.l_margin - pdf.r_margin

    paras = [
        "I'm applying for the AI Solutions Leader position within Deloitte's Human Capital practice. While my years of experience don't match a traditional senior hire, I want to make the case that what I bring is harder to find: I'm a finance professional who independently architects, builds, and deploys production AI systems end-to-end \u2014 and I understand business problems well enough to know which ones AI should actually solve.",

        "Over the past two years, I've designed, built, and deployed 10+ production applications spanning the complete technology stack. My AI-powered SaaS applications use generative AI APIs with custom prompt architecture, modern frontend frameworks (Next.js, React, TypeScript), Python backends (Django, FastAPI), and cloud deployment (Vercel, Railway, Supabase). My automated trading system is the most technically demanding: a Python quantitative engine with real-time data pipelines, parallel strategy execution (4.1x speedup), dynamic risk management using Kelly criterion, and production monitoring with automated health checks and self-healing deployment. I've managed the full lifecycle on every project \u2014 requirements, architecture, engineering, deployment, and continuous optimization.",

        "Building production systems teaches you things that theoretical knowledge doesn't. I've designed prompt architectures for domain-specific AI reasoning, built data pipelines that handle structured and unstructured sources, implemented rate limiting and caching for API-heavy applications, and made infrastructure decisions around cost, latency, and reliability. I've also learned when NOT to use AI \u2014 my trading system removed a signal that was circular because I measured its actual impact. This kind of practical AI judgment is what your clients need.",

        "Four years at John Deere gave me deep understanding of enterprise finance: FP&A, cost analysis, financial reporting, SEC compliance, and process automation. I've automated workflows with Power Automate and SQL, built Power BI dashboards for cross-functional teams, and worked in SAP across multiple business units. When consulting with leaders on AI solutions, I can speak their language \u2014 I've sat in their seat.",

        "I lead quarterly AI Lunch & Learn sessions for John Deere's Ag & Turf accounting organization, demonstrating generative AI tools and driving enterprise adoption. Making technical concepts accessible to non-technical stakeholders is something I do today and would bring to client engagements at Deloitte.",

        "I'm transparent that my experience profile is earlier-career than your posting describes. But the AI landscape has shifted \u2014 practical building experience with generative AI matters more than years on a resume, and candidates who can both sell an AI vision and personally build the solution are rare. I'm one of them.",

        "I'd be excited to discuss how my hands-on AI development experience and finance domain knowledge can contribute to Deloitte's Human Capital AI practice.",
    ]

    pdf.set_font(pdf.F, "", 11.5)
    for para in paras:
        pdf.multi_cell(w, 6.5, para, align="L")
        pdf.ln(4)

    pdf.ln(3)
    pdf.cell(0, 7, "Sincerely,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font(pdf.F, "B", 11.5)
    pdf.cell(0, 7, "Kruz J. Holt", new_x="LMARGIN", new_y="NEXT")

    out = "C:/Users/Kruz/Desktop/Projects/job-applications/applications/deloitte-ai-solutions-leader/Kruz_Holt_Cover_Letter_Deloitte_AI_Solutions.pdf"
    pdf.output(out)
    print(f"Created: {out}")


if __name__ == "__main__":
    generate_finance_ai_cover()
    generate_ai_solutions_cover()
    print("\nDone! Both cover letter PDFs generated.")
