"""Convert all DOCX files on Desktop to PDF using Microsoft Word."""
import win32com.client
import os

desktop = r"C:\Users\Kruz\Desktop"

files = [
    "Kruz_Holt_Resume_Deloitte_Finance_AI",
    "Kruz_Holt_Resume_Deloitte_AI_Solutions",
    "Kruz_Holt_Cover_Letter_Deloitte_Finance_AI",
    "Kruz_Holt_Cover_Letter_Deloitte_AI_Solutions",
]

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

for name in files:
    docx_path = os.path.join(desktop, name + ".docx")
    pdf_path = os.path.join(desktop, name + ".pdf")
    doc = word.Documents.Open(docx_path)
    doc.SaveAs(pdf_path, FileFormat=17)
    doc.Close()
    print(f"Saved: {name}.pdf")

word.Quit()
print("\nDone! All 4 crisp PDFs on your Desktop.")
