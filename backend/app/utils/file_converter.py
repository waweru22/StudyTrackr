import subprocess
import os


def convert_to_pdf(input_path: str, output_dir: str) -> str:
    """Convert PPTX, DOCX, or other office formats to PDF using LibreOffice headless."""
    subprocess.run([
        'soffice', '--headless', '--convert-to', 'pdf',
        '--outdir', output_dir, input_path
    ], check=True, timeout=60)
    
    base = os.path.splitext(os.path.basename(input_path))[0]
    pdf_path = os.path.join(output_dir, f"{base}.pdf")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Conversion produced no output file at {pdf_path}")
    
    return pdf_path