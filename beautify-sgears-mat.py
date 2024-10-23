import argparse
import pandas as pd
import os

# Background colors for required fields
REQUIRED_FIELDS_DICT: dict = {
    "Name": "#00ffff",
    "Type": "#f4cccc",
    "Tier": "#b6d7a8",
    "Rarity": "#a4c2f4",
    "Enchantment Value": "#6fa8dc",
    "Charging Value": "#9d9cff",
    "Durability": "#e6b8af",
    "Armor Durability": "#e6b8af",
    "Repair Efficiency": "#e6b8af",
    "Repair Bonus": "#e6b8af",
    "Harvest Speed": "#ffe599",
    "Reach Distance": "#00d2ff",
    "Attack Damage": "#e06666",
    "Attack Speed": "#e06666",
    "Attack Reach": "#e06666",
    "Magic Damage": "#e06666",
    "Ranged Damage": "#93c47d",
    "Ranged Speed": "#93c47d",
    "Projectile Speed": "#93c47d",
    "Projectile Accuracy": "#93c47d",
    "Armor": "#b7b7b7",
    "Armor Toughness": "#b7b7b7",
    "Knockback Resistance": "#b7b7b7",
    "Magic Armor": "#b7b7b7",
    "Traits": "#c27ba0",
}
REQUIRED_FIELDS = list(REQUIRED_FIELDS_DICT.keys())


def parse_arguments() -> tuple[str, str]:
    """Parse and return input and output file paths."""
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
    """Filter rows where 'Parent' is null and 'ID' is not 'silentgear:example', then sort by 'Type' and 'Tier'."""
    filtered_df = df[df["Parent"].isna() & (df["ID"] != "silentgear:example")]
    return (
        filtered_df[REQUIRED_FIELDS]
        .sort_values(["Type", "Tier"])
        .reset_index(drop=True)
    )


def add_blank_rows(df: pd.DataFrame, group_by_column: str) -> pd.DataFrame:
    """Insert blank rows whenever the value in `group_by_column` changes for better visual separation."""
    change_mask = df[group_by_column].ne(df[group_by_column].shift(-1))
    empty_rows = pd.DataFrame(
        "", index=change_mask.index[change_mask] + 0.5, columns=df.columns
    )
    return pd.concat([df, empty_rows]).sort_index().reset_index(drop=True).iloc[:-1]


def auto_adjust_column_width(writer: pd.ExcelWriter, df: pd.DataFrame, sheet_name: str):
    """Adjust column widths in Excel sheet based on the maximum content length."""
    df.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes(1, 1)

    for idx, col in enumerate(df):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4
        worksheet.set_column(idx, idx, max_len)


def style_index(series: pd.Series, field_colors: dict):
    """Apply style to the index (fields) of the table based on predefined colors."""
    return [
        f"background-color: {field_colors.get(value)}; border-bottom: 2px solid black; "
        "font-family: arial; font-weight: bold; text-align: justify;"
        for value in series
    ]


def style_table(df: pd.DataFrame):
    """Apply general styles to the entire DataFrame."""
    return pd.DataFrame(
        "font-family: arial; text-align: justify;", index=df.index, columns=df.columns
    )


def style_row(series: pd.Series, df: pd.DataFrame):
    """Apply row-specific styles, such as a black background for blank rows and border styles for category changes."""
    css = ""
    if not series.get("Name"):
        css += "background-color: black;"
    if df["Tier"].ne(df["Tier"].shift(-1))[series.name]:
        css += "border-bottom: 1px solid #0d151b;"
    return [css] * len(series)


def style_column(series: pd.Series, field_colors: dict):
    """Apply background color to specific columns based on predefined field colors."""
    css = f"background-color: {field_colors.get(series.name)};"
    if series.name == "Name":
        css += "border-left: 1px solid black;"
    return [css] * len(series)


def main():
    """Main function to read, process, style, and save the material dump to an Excel file."""
    # Parse input and output file paths
    input_file, output_file = parse_arguments()

    # Load TSV file into DataFrame
    materials_df = pd.read_csv(input_file, sep="\t")

    # Filter and sort data, then add blank rows for better visual separation
    materials_df = filter_and_sort_df(materials_df)
    materials_df = add_blank_rows(materials_df, "Type")

    # Create an Excel writer and adjust column widths
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        auto_adjust_column_width(writer, materials_df, "General")

        # Apply styling and save to Excel
        styled_df = (
            materials_df.style.apply(
                style_index, field_colors=REQUIRED_FIELDS_DICT, axis="columns"
            )
            .apply(style_table, axis=None)
            .apply(style_column, field_colors=REQUIRED_FIELDS_DICT, axis="index")
            .apply(style_row, df=materials_df, axis="columns")
        )
        styled_df.to_excel(writer, sheet_name="General", index=False)


if __name__ == "__main__":
    main()
