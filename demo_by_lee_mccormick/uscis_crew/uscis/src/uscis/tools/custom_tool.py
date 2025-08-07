from crewai.tools import BaseTool
import tempfile
import requests
import fitz

class PDFReaderTool(BaseTool):
    name: str = "PDF Reader"
    description: str = "Extracts text content from a local PDF file or URL."

    def _run(self, file_path_or_url: str) -> str:
        try:
            if file_path_or_url.startswith("http"):
                # Download to temp file
                with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                    r = requests.get(file_path_or_url)
                    r.raise_for_status()
                    tmp.write(r.content)
                    tmp.flush()
                    doc = fitz.open(tmp.name)
                    text = ""
                    for page in doc:
                        text += page.get_text()
            else:
                doc = fitz.open(file_path_or_url)
                text = ""
                for page in doc:
                    text += page.get_text()
            return text or "No text found in PDF."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
