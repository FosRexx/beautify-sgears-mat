import argparse
import pandas as pd


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Beautify Silent Gear's Material Dump"
    )
    parser.add_argument(
        "-i",
        "--input",
        required=False,
        type=str,
        help="Path to Silent Gear's Materials TSV dump",
    )
    args: argparse.Namespace = parser.parse_args()

    # Remove later
    if not args.input:
        args.input = "./DELETELATER/material_export.tsv"

    output_file: str = "./materials_beautified.csv"

    required_fieldnames: list[str] = [
        # Random
        "Name",  # df4343
        "Type",  # ee3f72
        "Tier",  # f04ca3
        "Rarity",  # e464d1
        "Enchantment Value",  # c87ff9
        "Charging Value",  # 9d9cff
        # Durability and Repair #72b3ff
        "Durability",
        "Armor Durability",
        "Repair Efficiency",
        "Repair Bonus",
        # Toothpick #3dc3ff
        "Harvest Speed",
        # Long Hands #00d2ff
        "Reach Distance",
        # Attack #00def8
        "Attack Damage",
        "Attack Speed",
        "Attack Reach",
        "Magic Damage",
        # Ranged and Projectile #00eae3
        "Ranged Damage",
        "Ranged Speed",
        "Projectile Speed",
        "Projectile Accuracy",
        # Armor#00f5c5
        "Armor",
        "Armor Toughness",
        "Knockback Resistance",
        "Magic Armor",
        # Traits #70faa7
        "Traits",
    ]

    with open(args.input, newline="") as material_export_file:
        materials: pd.DataFrame = pd.read_csv(material_export_file, sep="\t")

        print(type(materials))

        materials = materials[
            materials["Parent"].isna() & (materials["ID"] != "silentgear:example")
        ]

        materials = materials[required_fieldnames]

        print(materials.columns)

        # materials.to_csv(output_file, sep="\t", index=False)

        # materials = csv.reader


if __name__ == "__main__":
    main()
