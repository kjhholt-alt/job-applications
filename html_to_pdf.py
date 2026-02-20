"""Convert HTML resume/cover letter files to crisp PDFs via headless Chrome."""
import os
import asyncio
from playwright.async_api import async_playwright

DESKTOP = r"C:\Users\Kruz\Desktop"
HTML_DIR = r"C:\Users\Kruz\Desktop\Projects\job-applications\html"


async def convert_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        files = [
            "Kruz_Holt_Resume_Deloitte_Finance_AI",
            "Kruz_Holt_Resume_Deloitte_AI_Solutions",
            "Kruz_Holt_Cover_Letter_Deloitte_Finance_AI",
            "Kruz_Holt_Cover_Letter_Deloitte_AI_Solutions",
        ]

        for name in files:
            html_path = os.path.join(HTML_DIR, name + ".html")
            pdf_path = os.path.join(DESKTOP, name + ".pdf")

            await page.goto(f"file:///{html_path.replace(os.sep, '/')}")
            await page.pdf(
                path=pdf_path,
                format="Letter",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            print(f"Created: {name}.pdf")

        await browser.close()

asyncio.run(convert_all())
print("\nDone! All 4 crisp PDFs on your Desktop.")
