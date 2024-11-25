import json

def struttura_directory(item, indent=0):

    # Stampa ripetutamente il contenuto della directory
    prefisso = "|-- " if indent > 0 else ""
    print(" " * (indent * 4) + prefisso + item["name"])
    
    # Se l'oggetto è una directory e ha contenuto, la stampa ripetutamente
    if "contents" in item:
        for content in sorted(item["contents"], key=lambda x: x["name"]):
            struttura_directory(content, indent + 1)

def main():
    # Carica il file json
    file_name = "structure.json"
    try:
        with open(file_name, "r") as f:
            directory_structure = json.load(f)
        
        # Stampa la struttura
        struttura_directory(directory_structure)
    except FileNotFoundError:
        print(f"Errore: File '{file_name}' non trovato.")
    except json.JSONDecodeError as e:
        print(f"Errore: Impossibile analizzare il file JSON. {e}")

if __name__ == "__main__":
    main()
