import argparse
import pandas as pd
import os
from styleframe import StyleFrame, Styler

# Required fields dict with keys as fields and their respective values as background color
REQUIRED_FIELDS_DICT: dict = {
    # General Fields
    "Name": "#00ffff",
    "Type": "#f4cccc",
    "Tier": "#b6d7a8",
    "Rarity": "#a4c2f4",
    "Enchantment Value": "#6fa8dc",
    "Charging Value": "#9d9cff",
    #
    # Durability and Repair
    "Durability": "#e6b8af",
    "Armor Durability": "#e6b8af",
    "Repair Efficiency": "#e6b8af",
    "Repair Bonus": "#e6b8af",
    #
    # Harvesting
    "Harvest Speed": "#ffe599",
    #
    # Reach and Range
    "Reach Distance": "#00d2ff",
    #
    # Attack Attributes
    "Attack Damage": "#e06666",
    "Attack Speed": "#e06666",
    "Attack Reach": "#e06666",
    "Magic Damage": "#e06666",
    #
    # Ranged and Projectile Attributes
    "Ranged Damage": "#93c47d",
    "Ranged Speed": "#93c47d",
    "Projectile Speed": "#93c47d",
    "Projectile Accuracy": "#93c47d",
    #
    # Armor Attributes
    "Armor": "#b7b7b7",
    "Armor Toughness": "#b7b7b7",
    "Knockback Resistance": "#b7b7b7",
    "Magic Armor": "#b7b7b7",
    #
    # Traits
    "Traits": "#c27ba0",
}

REQUIRED_FIELDS = list(REQUIRED_FIELDS_DICT.keys())


def parse_arguments() -> tuple[str, str]:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="Beautify Silent Gear's Material Dump")

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="./DELETELATER/material_export.tsv",
        help="Path to Silent Gear's Materials TSV dump",
    )

    parser.add_argument(
        "-o", "--output", type=str, default=".", help="Path to the output directory"
    )

    args = parser.parse_args()

    output_file = os.path.join(args.output, "materials_beautified.xlsx")
    return args.input, output_file


def filter_and_sort_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to exclude rows where 'Parent' is not null and 'ID'
    is not equal to 'silentgear:example'. Then, sort by 'Type' and 'Tier'.
    """
    filtered_df = df[df["Parent"].isna() & (df["ID"] != "silentgear:example")]
    return (
        filtered_df[REQUIRED_FIELDS]
        .sort_values(["Type", "Tier"])
        .reset_index(drop=True)
    )


def add_blank_rows(df: pd.DataFrame, group_by_column: str) -> pd.DataFrame:
    """
    Insert blank rows whenever the value in `group_by_column` changes.
    This is useful for visually separating different categories in the output.
    """
    # Create a mask to identify where the column value changes
    change_mask = df[group_by_column].ne(df[group_by_column].shift(-1))

    # Create an empty DataFrame to insert the blank rows
    empty_rows = pd.DataFrame(
        "", index=change_mask.index[change_mask] + 0.5, columns=df.columns
    )

    # Concatenate the original DataFrame with the empty rows
    expanded_df = (
        pd.concat([df, empty_rows]).sort_index().reset_index(drop=True).iloc[:-1]
    )

    return expanded_df


def style_columns(
    style_frame: StyleFrame, columns_to_style: list[str], background_color: str
):
    """Apply background color styling to specific columns."""
    styler = Styler(bg_color=background_color)
    style_frame.apply_column_style(
        cols_to_style=columns_to_style,
        styler_obj=styler,
        style_header=True,
        overwrite_default_style=False,
    )


def write_to_excel(
    style_frame: StyleFrame, output_path: str, sheet_name: str = "General"
):
    """Write the styled DataFrame to an Excel file."""
    with StyleFrame.ExcelWriter(output_path) as writer:
        StyleFrame.A_FACTOR = 8
        StyleFrame.P_FACTOR = 1.2
        style_frame.to_excel(
            excel_writer=writer,
            sheet_name=sheet_name,
            best_fit=REQUIRED_FIELDS,
        )


def main():
    # Parse input and output file paths
    input_file, output_file = parse_arguments()

    # Read the TSV file into a DataFrame
    materials_df = pd.read_csv(input_file, sep="\t")

    # Filter and sort the DataFrame based on required fields
    materials_df = filter_and_sort_df(materials_df)

    # Add blank rows after each change in the 'Type' column
    materials_df = add_blank_rows(materials_df, "Type")

    # Create a StyleFrame object for styling the DataFrame
    style_frame = StyleFrame(
        obj=materials_df,
        styler_obj=Styler(
            horizontal_alignment="justify",
            vertical_alignment="justify",
            wrap_text=False,
            shrink_to_fit=False,
        ),
    )

    # Apply color to the 'Name' column
    for key, value in REQUIRED_FIELDS_DICT.items():
        style_columns(
            style_frame=style_frame, columns_to_style=key, background_color=value
        )

    style_frame = style_frame.apply_style_by_indexes(
        style_frame[style_frame["Name"] == ""],
        styler_obj=Styler(bg_color="black", border_type="thick"),
    )

    style_frame = style_frame.apply_headers_style(
        styler_obj=Styler(bold=True, border_type="thick"),
    )

    # Write the styled DataFrame to an Excel file
    write_to_excel(style_frame, output_file)


if __name__ == "__main__":
    main()
