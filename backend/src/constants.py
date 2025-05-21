import os
from pathlib import Path

RCPCH_GUIDELINES_URL = "https://www.rcpch.ac.uk/resources/clinical-guideline-directory"
DATA_DIR = Path(os.path.dirname(__file__)) / "data"
RCPCH_GUIDELINES_LINKS_FILE = DATA_DIR / "links" / "rcpch_guidelines_links.json"

# FOR EACH TYPE
NICE_PDF_JSON_FILE = DATA_DIR / "nice_pdfs.json"