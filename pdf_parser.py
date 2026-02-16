import sys
import re
import json
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def parse_character_sheet(text):
    """Parses the extracted text to find character attributes."""
    data = {"name": "Não encontrado", "race": "Não encontrado", "class": "Não encontrado", "attributes": {}}
    
    # Normalize text a bit
    text = text.replace("\n", " ").replace("  ", " ")

    # This is highly experimental and depends on the PDF layout.
    # We will try to find patterns.
    
    # Try to find attributes (FOR, DES, etc.) and a number nearby
    attributes = ["Força", "Destreza", "Constituição", "Inteligência", "Sabedoria", "Carisma"]
    # Garbled versions
    attributes_garbled = ["Fora", "Destreza", "Constituio", "Inteligncia", "Sabedoria", "Carisma"]

    for i, attr in enumerate(attributes):
        try:
            # Look for the attribute name (or its garbled version) and then the first number after it.
            # This regex looks for the attribute name, then any characters, then a number.
            pattern = re.compile(f"({attributes[i]}|{attributes_garbled[i]}).*?(\d+)", re.IGNORECASE)
            match = pattern.search(text)
            if match:
                # The second group is the number
                data["attributes"][attr[:3].upper()] = match.group(2)
        except re.error as e:
            # Ignore regex errors for now
            pass

    # A simple way to get some info, might not work well.
    # Look for a line that might contain Race/Class
    # Example: "Elfo Patrulheiro"
    class_race_match = re.search(r"([A-Z][a-z]+(?: [A-Z][a-z]+)?) ([A-Z][a-z]+(?: [A-Z][a-z]+)?)", text)
    if class_race_match:
        # This is a wild guess
        data["race"] = class_race_match.group(1)
        data["class"] = class_race_match.group(2)


    return data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        extracted_text = extract_text_from_pdf(pdf_file)
        if "Error" in extracted_text:
            print(json.dumps({"error": extracted_text}))
        else:
            parsed_data = parse_character_sheet(extracted_text)
            print(json.dumps(parsed_data, indent=4, ensure_ascii=False))
    else:
        print("Usage: python pdf_parser.py <path_to_pdf>", file=sys.stderr)