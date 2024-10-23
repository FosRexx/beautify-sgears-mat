import argparse
import pandas as pd
import os

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


def auto_adjust_column_width(writer: pd.ExcelWriter, df: pd.DataFrame, sheet_name: str):
    # https://stackoverflow.com/a/40535454
    #
    # # Given a dict of dataframes, for example:
    # # dfs = {'gadgets': df_gadgets, 'widgets': df_widgets}
    #
    # writer = pd.ExcelWriter(filename, engine="xlsxwriter")
    # for sheetname, df in dfs.items():  # loop through `dict` of dataframes
    #     df.to_excel(writer, sheet_name=sheetname)  # send df to writer
    #     worksheet = writer.sheets[sheetname]  # pull worksheet object
    #     for idx, col in enumerate(df):  # loop through all columns
    #         series = df[col]
    #         max_len = (
    #             max(
    #                 (
    #                     series.astype(str).map(len).max(),  # len of largest item
    #                     len(str(series.name)),  # len of column name/header
    #                 )
    #             )
    #             + 1
    #         )  # adding a little extra space
    #         worksheet.set_column(idx, idx, max_len)  # set column width
    # writer.save()

    df.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)

    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes(1, 1)

    for idx, col in enumerate(df):
        series = df[col]
        max_len = max(series.astype(str).map(len).max(), len(str(series.name))) + 4
        worksheet.set_column(idx, idx, max_len)


def style_index(series: pd.Series, REQUIRED_FIELDS_DICT):
    return [
        f"background-color: {REQUIRED_FIELDS_DICT.get(value)}; \
          border-bottom-style: solid; \
          border-width: 2px; \
          border-color: black; \
          font-family: arial; \
          font-weight: bold; \
          text-align: justify; \
          "
        for value in series
    ]


def style_table(df: pd.DataFrame):
    return pd.DataFrame(
        "font-family: arial; \
         text-align: justify; \
        ",
        index=df.index,
        columns=df.columns,
    )


def style_row(series: pd.Series, df: pd.DataFrame):
    css: str = ""

    # Create a mask to identify where the tier value changes
    change_mask = df["Tier"].ne(df["Tier"].shift(-1))

    if not series.get("Name"):
        css += "background-color: black;"
    if change_mask[series.name]:
        css += "border-bottom-style: solid; \
                border-width: 1px; \
                border-color:#0d151b; \
                "

    return [css] * len(series)


def style_column(series: pd.Series, REQUIRED_FIELDS_DICT):
    """
    Apply background color to specific columns as defined in REQUIRED_FIELDS_DICT.
    """
    css: str = f"background-color: {REQUIRED_FIELDS_DICT.get(series.name)};"

    if series.name == "Name":
        css += "border-left-style: solid; \
                border-width: 1px; \
                border-color: black; \
                "

    return [css] * len(series)


def main():
    # Parse input and output file paths
    input_file, output_file = parse_arguments()

    # Read the TSV file into a DataFrame
    materials_df = pd.read_csv(input_file, sep="\t")

    # Filter and sort the DataFrame based on required fields
    materials_df = filter_and_sort_df(materials_df)

    # Add blank rows after each change in the 'Type' column
    materials_df = add_blank_rows(materials_df, "Type")

    writer = pd.ExcelWriter(output_file, engine="xlsxwriter")

    auto_adjust_column_width(writer, materials_df, "General")

    # materials_df.apply_index(lambda series: print(series), axis="index")

    # Apply styles and save the styled DataFrame
    styled_df = (
        materials_df.style.apply(style_table, axis=None)
        .apply_index(
            style_index, REQUIRED_FIELDS_DICT=REQUIRED_FIELDS_DICT, axis="columns"
        )
        .apply(style_column, REQUIRED_FIELDS_DICT=REQUIRED_FIELDS_DICT, axis="index")
        .apply(style_row, df=materials_df, axis="columns")
    )

    styled_df.to_excel(writer, sheet_name="General", index=False)

    writer.close()


if __name__ == "__main__":
    main()
