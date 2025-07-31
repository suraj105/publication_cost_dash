import urllib.request
from pathlib import Path
from tqdm import tqdm

# Parameters pubmed
BASE_URL = "ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/"
START = 1215
END = 1273

# Resolve path to project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "pubmed_raw"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Download .xml.gz
file_range = range(START, END + 1)

for i in tqdm(file_range, desc="Downloading PubMed XML.gz files", unit="file"):
    filename = f"pubmed25n{i:04}.xml.gz"
    url = BASE_URL + filename
    out_path = OUTPUT_DIR / filename

    if not out_path.exists():
        try:
            urllib.request.urlretrieve(url, out_path)
        except Exception as e:
            print(f"\nFailed to download {filename}: {e}")

print("\n All .xml.gz files downloaded to:", OUTPUT_DIR.resolve())
