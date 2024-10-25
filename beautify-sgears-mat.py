import argparse
import os
import pandas as pd
import json


def parse_arguments() -> tuple[str, str]:
    """Parse and return the input and output file paths from command-line arguments."""
    parser = argparse.ArgumentParser(description="Beautify Silent Gear's Material Dump")

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="./DELETELATER/material_export.tsv",
        help="Path to Silent Gear's Materials TSV dump",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Directory to save the beautified output",
    )

    args = parser.parse_args()

    output_file = os.path.join(args.output, "materials_beautified.xlsx")
    return args.input, output_file


def filter_and_sort_df(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    """
    Filter and sort DataFrame based on specific conditions and fields.
    Rows with 'Parent' values are excluded, and 'ID' of 'silentgear:example' is ignored.
    The DataFrame is then sorted by 'Type' and 'Tier'.
    """
    filtered_df = df[df["Parent"].isna() & (df["ID"] != "silentgear:example")]
    return filtered_df[fields].sort_values(["Type", "Tier"]).reset_index(drop=True)


def insert_blank_rows(df: pd.DataFrame, group_by_column: str) -> pd.DataFrame:
    """
    Insert blank rows whenever the value in `group_by_column` changes.
    This visually separates different categories in the output.
    """
    change_mask = df[group_by_column].ne(df[group_by_column].shift(-1))
    empty_rows = pd.DataFrame(
        "", index=change_mask.index[change_mask] + 0.5, columns=df.columns
    )
    return pd.concat([df, empty_rows]).sort_index().reset_index(drop=True)


def adjust_column_width(
    writer: pd.ExcelWriter, df: pd.DataFrame, sheet_name: str
) -> None:
    """
    Automatically adjust column widths in the Excel sheet based on the length of the column values.
    """
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes(1, 1)  # Freeze header

    for idx, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4
        worksheet.set_column(idx, idx, max_len)


def apply_styles(df: pd.DataFrame, general_headers: dict):
    """
    Apply styling to the DataFrame, including index, column, and row styles.
    """
    return (
        df.style.apply(style_table, axis=None)
        .apply_index(style_index, field_color=general_headers, axis="columns")
        .apply(style_column, field_color=general_headers, axis="index")
        .apply(style_row, df=df, axis="columns")
    )


def style_index(series: pd.Series, field_color: dict) -> list[str]:
    """
    Style the header (index) row based on the field_color dictionary.
    """
    return [
        f"background-color: {field_color.get(value, '')}; \
          border-bottom: 2px solid black; \
          {'border-right: 2px solid black;' if value == 'Name' else ''} \
          font-family: arial; \
          font-weight: bold; \
          text-align: justify;"
        for value in series
    ]


def style_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a blank CSS table style for consistent formatting across the sheet.
    """
    return pd.DataFrame(
        "font-family: arial; border: 1px thin black; text-align: justify;",
        index=df.index,
        columns=df.columns,
    )


def style_row(series: pd.Series, df: pd.DataFrame) -> list[str]:
    """
    Apply styles to rows, including background color and border adjustments.
    """
    css = ""
    change_mask = df["Tier"].ne(df["Tier"].shift(-1))

    if not series.get("Name"):
        css += "background-color: black;"

    css += (
        "border-bottom: 1px solid #0d151b;"
        if change_mask[series.name]
        else "border-bottom: 1px dotted gray;"
    )
    return [css] * len(series)


def style_column(series: pd.Series, field_color: dict) -> list[str]:
    """
    Apply background color to specific columns based on the field_color dictionary.
    """
    css = f"background-color: {field_color.get(series.name, '')};"
    if series.name == "Name":
        css += "border-right: 2px solid black;"
    return [css] * len(series)


def generate_sheet(
    df: pd.DataFrame, writer: pd.ExcelWriter, sheet_name: str, general_headers: dict
) -> None:
    """
    Generate and style an Excel sheet for a given DataFrame.
    """
    df_with_blanks = insert_blank_rows(df, "Type")
    adjust_column_width(writer, df_with_blanks, sheet_name)

    styled_df = apply_styles(df_with_blanks, general_headers)
    styled_df.to_excel(writer, sheet_name=sheet_name, index=False)


def main() -> None:
    """
    Main function to orchestrate reading, processing, and exporting the data.
    """
    # Parse input and output file paths
    input_file, output_file = parse_arguments()

    # Read the TSV file into a DataFrame
    materials_df = pd.read_csv(input_file, sep="\t")

    # Load configuration data
    with open("config.json", mode="r", encoding="utf-8") as config_json:
        config_data = json.load(config_json)

    general_headers: dict = config_data["headers"]
    tool_headers: list = config_data["tool"]["headers"]
    weapon_headers: list = config_data["weapon"]["headers"]
    armor_headers: list = config_data["armor"]["headers"]

    # Filter and sort data into separate categories
    general_df = filter_and_sort_df(materials_df, list(general_headers.keys()))
    tool_df = filter_and_sort_df(materials_df, tool_headers)
    weapon_df = filter_and_sort_df(materials_df, weapon_headers)
    armor_df = filter_and_sort_df(materials_df, armor_headers)

    # Write the data into an Excel file with styled sheets
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        generate_sheet(general_df, writer, "General", general_headers)
        generate_sheet(tool_df, writer, "Tools", general_headers)
        generate_sheet(weapon_df, writer, "Weapons", general_headers)
        generate_sheet(armor_df, writer, "Armor", general_headers)


if __name__ == "__main__":
    main()
