import argparse
import csv
import openpyxl


def main():
    parser = argparse.ArgumentParser(description="Beautify Silent Gear's Material Dump")
    parser.add_argument(
        "-i",
        "--input",
        required=False,
        type=str,
        help="Path to Silent Gear's Materials TSV dump",
    )
    args = parser.parse_args()

    # Remove later
    if not args.input:
        args.input = "./DELETELATER/material_export.tsv"

    with open(args.input, newline="") as material_export_file:
        materials = csv.DictReader(material_export_file, delimiter="\t")

        for row in materials:
            print(type(row))
            pass


if __name__ == "__main__":
    main()
