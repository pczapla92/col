#!/usr/bin/python3
import argparse
import csv
import os
import sys
from collections import defaultdict

CSV_ENCODING = "UTF-8"
script_dir = os.path.dirname(os.path.abspath(__file__))

ignored_records = []
mapping = []

try:
    ignored_path = os.path.join(script_dir, "ignored")
    with open(ignored_path, encoding='utf-8') as ignored_file:
        reader = csv.reader(ignored_file)
        ignored_records = [item for row in reader for item in row]
except FileNotFoundError:
    print(f"Ignored records file not found: {ignored_path}")
# Read 'mapping.csv' file that resides in the same directory as the script (if present).
# Each line in mapping.csv should contain two columns separated by a comma:
#   - First column: a keyword to match in the original group key (case-insensitive substring match)
#   - Second column: the target group name to replace the matched key with
# For each key in the provided dictionaries, if the key contains any keyword from the mapping (case-insensitive),
# it is replaced with the corresponding target group name before merging into the result.
# If no match is found, the original key is used.
try:
    mapping_path = os.path.join(script_dir, "mapping")
    with open(mapping_path, encoding='utf-8') as mapping_file:
        reader = csv.reader(mapping_file)
        mapping = [(k.lower(), v) for k, v in reader if k and v]
except FileNotFoundError:
    print(f"Mapping file not found: {mapping_path}")


def parse_csv_file(filepath, group_col_index, amount_col_index):
    sums = defaultdict(float)
    with open(filepath, encoding=CSV_ENCODING, newline='') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            try:
                group = row[group_col_index]
                if len(group) == 0:
                    print(f"Empty group in {row}")
                group_lower = group.lower()
                for pattern, replacement in mapping:
                    if pattern in group_lower:
                        print(f"Replacing record: {group} -> {replacement}")
                        group = replacement
                        break
                if group in ignored_records:
                    print(f"Ignoring record: {group}")
                    continue
                amount = float(row[amount_col_index].replace(",", "."))
                group_key = group.strip()
                sums[group_key] += amount
            except (IndexError, ValueError):
                print(f"Cannot parse: {row}")
                continue
    return sums


def merge_dicts(dicts):
    merged = defaultdict(float)
    for d in dicts:
        for k, v in d.items():
            if len(k) == 0:
                print(f"Ignoring empty group record value: {v}")
                continue
            merged[k] += v

    return merged


def main():
    parser = argparse.ArgumentParser(description="Sum and group expenses.")
    parser.add_argument('args', metavar='ARG', nargs='+',
                        help='CSV files (e.g. .preprocessed/may.csv).')
    parsed = parser.parse_args()

    file_and_columns_triple = [(parsed.args[i], 0, 1) for i in range(0, len(parsed.args))]
    all_sums = merge_dicts(
        [parse_csv_file(filename, group_col_index, amount_col_index) for filename, group_col_index, amount_col_index in
         file_and_columns_triple])

    max_key_len = max((len(key) for key in all_sums), default=15)
    header_fmt = f"\n{{:<{max_key_len}}} | {{:>15}}"
    row_fmt = f"{{:<{max_key_len}}} | {{:>15.2f}}"

    print(header_fmt.format("Group Key", "Amount"))
    print("-" * (max_key_len + 20))
    total = 0.0
    plus = 0.0
    minus = 0.0
    for key, amount in sorted(all_sums.items(), key=lambda x: x[1]):
        print(row_fmt.format(key, amount))
        if amount > 0:
            plus += amount
        else:
            minus += amount
        total += amount

    print("-" * (max_key_len + 20))
    print(row_fmt.format("     PLUS", plus))
    print(row_fmt.format("     MINUS", minus))
    print("-" * (max_key_len + 20))
    print(row_fmt.format("TOTAL", total))

if __name__ == "__main__":
    main()
