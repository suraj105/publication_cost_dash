from db.openapc import main as load_openapc
from db.doaj import main as load_doaj
from db.pubmed import main as load_pubmed
from db.pubmed_enricher import main as run_enrichment
from dash_main import run_dash

#für ja/nein on the console/terminal
def yes_no_input(prompt):
    while True:
        response = input(f"{prompt} [y/n]: ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        else:
            print("Bitte eingeben 'y' oder 'n'.")

#controls the pipeline, according the the users need
def main():
    print("Datenpipeline zur Analyse Publikationskosten")

    if not yes_no_input("Sind alle Daten (OpenAPC, DOAJ, PubMed) bereits in die Datenbank geladen worden?"):
        print("\n lädt OpenAPC...")
        load_openapc()
        print("\n lädt DOAJ...")
        load_doaj()
        print("\n lädt PubMed...")
        load_pubmed()
    else:
        print("Datenladen übersprungen.")

    if not yes_no_input("\nWurde die Daten Enrichment bereits durchgeführt und gespeichert?"):
        print("\nläuft enrichment...")
        run_enrichment()
    else:
        print("Datenladen übersprungen.")

    print("\n startet Dash app...")
    run_dash()

if __name__ == "__main__":
    main()
