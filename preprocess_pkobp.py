#!/usr/bin/python3
import csv
import os
import sys

CSV_ENCODING = "ISO-8859-2"

def clean_and_extract_csv(file_path):
    extracted_rows = []

    with open(file_path, encoding=CSV_ENCODING, newline="") as infile:
        reader = csv.reader(infile)
        next(reader)  # Skip header

        for i, row in enumerate(reader, start=2):  # Start from line 2 (after header)
            if len(row) < 10:
                print(f"[Line {i}] Skipped: not enough columns: {row}")
                continue

            if "otwarcie lokaty" in row[6].lower():
                print(f"[Line {i}] Skipped: contains 'otwarcie lokaty'")
                continue

            amount = row[3]
            original_group = row[7]
            group = original_group

            if group.startswith("Numer telefonu: "):
                group = row[8]
                print(f"[Line {i}] Swapped column 8 -> 9 due to 'Numer telefonu:' | New group: '{group}'") # blik payment

            if "bankomat" in row[9].lower():
                group = "bankomat"
                print(f"[Line {i}] Overwritten group to 'bankomat' due to 'bankomat' in column 10")

            cleaned_group = group.replace("Lokalizacja: Adres: ", "").replace("Nazwa odbiorcy: ", "").replace("Nazwa nadawcy: ", "")

            # print(f"[Line {i}] Final row → Group: '{cleaned_group}', Amount: '{amount}'")

            extracted_rows.append([cleaned_group, amount])

    # Prepare output
    original_filename = os.path.basename(file_path)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(script_dir, "preprocessed")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, original_filename)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(extracted_rows)

    print(f"\nExtracted file written to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preprocess_pkobp.py <file1.csv> <file2.csv> ...")
    else:
        for file_path in sys.argv[1:]:
            clean_and_extract_csv(file_path)
