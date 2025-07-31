import os
import gzip
import xml.etree.ElementTree as ET
import csv
from tqdm import tqdm

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "data", "pubmed_raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "pubmed_raw_to_csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

start = 1215
end = 1273

# Progress bar for files
for index, file_number in enumerate(tqdm(range(start, end + 1), desc="📦 Parsing PubMed files", unit="file")):
    input_filename = f"pubmed25n{file_number:04}.xml.gz"
    input_path = os.path.join(INPUT_DIR, input_filename)

    # Corrected output file naming logic
    output_number = end - file_number  # 58 to 0
    if output_number == 0:
        output_filename = "pubmed_output.csv"
    else:
        output_filename = f"pubmed_output{output_number}.csv"

    output_path = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(input_path):
        print(f"File not found: {input_filename}")
        continue

    try:
        with gzip.open(input_path, 'rb') as f:
            tree = ET.parse(f)
            root = tree.getroot()
    except Exception as e:
        print(f"\nFailed to parse {input_filename}: {e}")
        continue

    article_count = 0
    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['pmid', 'title', 'doi', 'issn', 'year', 'journal', 'authors', 'affiliations', 'country'])

        for article in root.findall('PubmedArticle'):
            medline = article.find('MedlineCitation')
            if medline is None:
                continue

            article_info = medline.find('Article')
            pubmed_data = article.find('PubmedData')
            if article_info is None or pubmed_data is None:
                continue

            pmid = medline.findtext('PMID', default='')
            title = article_info.findtext('ArticleTitle', default='')

            # DOI
            doi = ''
            aid_list = pubmed_data.find('ArticleIdList')
            if aid_list is not None:
                for aid in aid_list.findall('ArticleId'):
                    if aid.attrib.get('IdType') == 'doi':
                        doi = aid.text
                        break

            # Journal info
            journal_info = article_info.find('Journal')
            issn = journal_info.findtext('ISSN', default='') if journal_info is not None else ''
            pub_date = journal_info.find('JournalIssue').find('PubDate') if journal_info is not None and journal_info.find('JournalIssue') is not None else None
            year = pub_date.findtext('Year', default='') if pub_date is not None else ''
            journal = journal_info.findtext('Title', default='') if journal_info is not None else ''

            # Authors and affiliations
            authors, affiliations = [], []
            author_list = article_info.find('AuthorList')
            if author_list is not None:
                for author in author_list.findall('Author'):
                    last = author.findtext('LastName') or ''
                    fore = author.findtext('ForeName') or ''
                    authors.append(f"{fore} {last}".strip())

                    aff_info = author.find('AffiliationInfo')
                    if aff_info is not None:
                        aff = aff_info.findtext('Affiliation')
                        if aff:
                            affiliations.append(aff)

            authors_str = '; '.join(authors)
            affiliations_str = '; '.join(affiliations)

            # Country info
            countries = set()
            grants = article_info.find('GrantList')
            if grants is not None:
                for grant in grants.findall('Grant'):
                    country = grant.findtext('Country')
                    if country:
                        countries.add(country)

            fallback_country = medline.findtext('MedlineJournalInfo/Country')
            if not countries and fallback_country:
                countries.add(fallback_country)

            country_str = '; '.join(sorted(countries))

            writer.writerow([
                pmid, title, doi, issn, year, journal,
                authors_str, affiliations_str, country_str
            ])
            article_count += 1

    tqdm.write(f"{input_filename} → {output_filename} ({article_count} articles)")
