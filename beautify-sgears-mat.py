import argparse
import json
import os
import pandas as pd

from typing import Optional, Tuple, List, Dict


def parse_arguments() -> Tuple[str, str]:
    """
    Parse and return the input and output file paths from command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Beautify Silent Gear's Material Dump")

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        # default="./DELETELATER/material_export.tsv",
        required=True,
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


def filter_and_sort_df(
    df: pd.DataFrame, fields: List[str], parts: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Filter and sort DataFrame by excluding rows with 'Parent' values
    and ignoring 'silentgear:example' in 'ID'.
    Sort the resulting DataFrame by 'Type' and 'Tier'.
    """
    filtered_df = df[df["Parent"].isna() & (df["ID"] != "silentgear:example")]

    if parts:
        filtered_df = filtered_df[filtered_df["Type"].isin(parts)]

    return filtered_df[fields].sort_values(["Type", "Tier"]).reset_index(drop=True)


def insert_blank_rows(df: pd.DataFrame, group_by_column: str) -> pd.DataFrame:
    """
    Insert blank rows to visually separate categories whenever
    the value in `group_by_column` changes.
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
    Adjust column widths in the Excel sheet based on the length of the column values.
    """
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes(1, 1)  # Freeze header

    for idx, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4
        worksheet.set_column(idx, idx, max_len)


def style_index(series: pd.Series, field_color: Dict[str, str]) -> List[str]:
    """
    Style the header row based on the field_color dictionary.
    """
    return [
        f"background-color: {field_color.get(value, '')}; \
          border-bottom: 2px solid black; \
          {'border-right: 2px solid black;' if value == 'Name' else 'border-right: 1px dotted gray;'} \
          font-family: Arial; \
          font-weight: bold; \
          text-align: justify;"
        for value in series
    ]


def style_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a blank CSS table style for consistent formatting across the sheet.
    """
    return pd.DataFrame(
        "font-family: Arial; \
         text-align: justify;",
        index=df.index,
        columns=df.columns,
    )


def style_row(series: pd.Series, df: pd.DataFrame) -> List[str]:
    """
    Apply styles to rows, including background color and border adjustments.
    """
    css = "background-color: black;" if not series.get("Name") else ""

    change_mask = df["Tier"].ne(df["Tier"].shift(-1))

    css += (
        "border-bottom: 1px solid #0d151b;"
        if change_mask[series.name]
        else "border-bottom: 1px dotted gray;"
    )

    return [css] * len(series)


def style_column(series: pd.Series, field_color: Dict[str, str]) -> List[str]:
    """
    Apply background color to specific columns based on the field_color dictionary.
    """
    css = f"background-color: {field_color.get(series.name, '')};"

    css += (
        "border-right: 2px solid black;"
        if series.name == "Name"
        else "border-right: 1px dotted gray;"
    )

    return [css] * len(series)


def apply_styles(df: pd.DataFrame, general_headers: Dict[str, str]) -> pd.DataFrame:
    """
    Apply styling to the DataFrame, including index, column, and row styles.
    """
    return (
        df.style.apply(style_table, axis=None)
        .apply_index(style_index, field_color=general_headers, axis="columns")
        .apply(style_column, field_color=general_headers, axis="index")
        .apply(style_row, df=df, axis="columns")
    )


def generate_sheet(
    df: pd.DataFrame,
    writer: pd.ExcelWriter,
    sheet_name: str,
    general_headers: Dict[str, str],
) -> None:
    """
    Generate and style an Excel sheet for a given DataFrame.
    """
    df_with_blanks = insert_blank_rows(df, "Type")
    adjust_column_width(writer, df_with_blanks, sheet_name)

    styled_df = apply_styles(df_with_blanks, general_headers)
    styled_df.to_excel(writer, sheet_name=sheet_name, index=False)


def load_config(config_file: str = "config.json") -> Dict:
    """
    Load the configuration data from a JSON file.
    """
    try:
        with open(config_file, mode="r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Error loading configuration file: {e}")


def main() -> None:
    """
    Main function to orchestrate reading, processing, and exporting the data.
    """
    # Parse input and output file paths
    input_file, output_file = parse_arguments()

    # Read the TSV file into a DataFrame
    try:
        materials_df = pd.read_csv(input_file, sep="\t")
    except FileNotFoundError:
        raise RuntimeError(f"Input file '{input_file}' not found.")

    # Load configuration data
    config_data = load_config()

    # Extract headers and parts for different categories
    general_headers: Dict[str, str] = config_data["headers"]
    tool_headers, tool_parts = (
        config_data["tool"]["headers"],
        config_data["tool"]["parts"],
    )
    weapon_headers, weapon_parts = (
        config_data["weapon"]["headers"],
        config_data["weapon"]["parts"],
    )
    armor_headers, armor_parts = (
        config_data["armor"]["headers"],
        config_data["armor"]["parts"],
    )

    # Filter and sort data into separate categories
    general_df = filter_and_sort_df(materials_df, list(general_headers.keys()))
    tool_df = filter_and_sort_df(materials_df, tool_headers, parts=tool_parts)
    weapon_df = filter_and_sort_df(materials_df, weapon_headers, parts=weapon_parts)
    armor_df = filter_and_sort_df(materials_df, armor_headers, parts=armor_parts)

    # Write the data into an Excel file with styled sheets
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        generate_sheet(general_df, writer, "General", general_headers)
        generate_sheet(tool_df, writer, "Tools", general_headers)
        generate_sheet(weapon_df, writer, "Weapons", general_headers)
        generate_sheet(armor_df, writer, "Armor", general_headers)


if __name__ == "__main__":
    main()
