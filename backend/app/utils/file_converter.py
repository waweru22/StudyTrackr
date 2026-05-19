import os
import pypandoc


def convert_document(input_path: str, output_dir: str) -> tuple[str, str]:
    """
    Convert uploaded documents to a web-viewable format using Pandoc.

    Supported conversions:
        .docx, .doc, .txt, .md  →  HTML
        .pdf                    →  returned as-is (no conversion)

    Returns:
        (output_path, file_type) where file_type is 'pdf' or 'html'
    """
    ext = os.path.splitext(input_path)[1].lower()
    base = os.path.splitext(os.path.basename(input_path))[0]

    if ext == '.pdf':
        return input_path, 'pdf'

    # All other supported types are converted to HTML
    output_filename = f"{base}.html"
    output_path = os.path.join(output_dir, output_filename)

    pypandoc.convert_file(
        input_path,
        'html',
        outputfile=output_path,
        extra_args=['--standalone']
    )

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Conversion produced no output file at {output_path}")

    return output_path, 'html'