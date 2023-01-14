import pandas as pd

from DataReparationAuxFunctions import (
    clean_and_reconstruct_fundamentals,
    fundamentalCalculator,
)


def process_sheet(sheet, max_length_letter):
    # Create a dataframe from the range of cells specified on the sheet
    raw_df = pd.DataFrame(sheet["A1:" + max_length_letter + "104"].value)
    raw_df.columns = raw_df.iloc[0]
    raw_df = raw_df.drop(0)
    raw_df.set_index(raw_df.columns[0], drop=True, inplace=True)

    # From the "DumpQ" sheet, we only want to get the information from the last 4 quarters
    # We only need the first column and the last 4 columns
    if sheet.name == "DumpQ":
        raw_df = raw_df.iloc[:, [0, -4, -3, -2, -1]]

    # Clean the dataframe and reconstruct it
    cleaned_df = clean_and_reconstruct_fundamentals(raw_df, reconstruct_df=True)

    # Once reconstructed the DumpQ sheet, we want to get the TTMs
    # For this we sum the last 4 columns
    if sheet.name == "DumpQ":
        # We want to agregate the last 4 columns
        # Some rows must be summed, others must be averaged and others we must keep the last value
        rows_to_average = [
            "Gross Profit Ratio",
            "EBITDA ratio",
            "Operating Income ratio",
            "Income Before Tax Ratio",
            "Net Income ratio",
            "Forex Rate",
        ]
        rows_to_keep_last_value = [
            "Weighted Average Shares Outstanding",
            "Weighted Average Shares Outstanding Diluted",
            "Cash and Cash Equivalents",
            "Short-Term Investments",
            "Cash and Short-Term Investments",
            "Net Receivables",
            "Inventory",
            "Other Current Assets",
            "Total Current Assets",
            "PP&E",
            "Goodwill",
            "Intangible Assets",
            "Investments",
            "Tax Assets",
            "Other Non-Current Assets",
            "Total Non-Current Assets",
            "Other Assets",
            "Total Assets",
            "Accounts Payable",
            "Short-Term Debt",
            "Tax Payable",
            "Deferred Revenue",
            "Other Current Liabilities",
            "Total Current Liabilities",
            "Long-Term Debt",
            "Deferred Tax Liabilities",
            "Other Non-Current Liabilities",
            "Total Non-Current Liabilities",
            "Other Liabilities",
            "Capital Lease Obligations",
            "Total Liabilities",
            "Preferred Stock",
            "Common Stock",
            "Retained Earnings",
            "Other Comprehensive Income/Loss",
            "Other Total Stockholders Equity",
            "Total Stockholders Equity",
            "Total Liabilities And Stockholders Equity",
            "Minority Interest",
            "Total Liabilities & Equity",
        ]
        cleaned_df["TTM"] = None

        # Iterate through each row of the DataFrame
        for i in range(len(cleaned_df)):
            # Get the row name
            row_name = cleaned_df.index[i]

            # Perform the appropriate operation based on the row name
            # If the row name is in the list of rows to average, then average the last 4 columns
            if row_name in rows_to_average:
                cleaned_df.loc[row_name, "TTM"] = cleaned_df.iloc[i, :4].mean()
            elif row_name in rows_to_keep_last_value:
                cleaned_df.loc[row_name, "TTM"] = cleaned_df.iloc[i, -2]
            else:
                cleaned_df.loc[row_name, "TTM"] = cleaned_df.iloc[i, :4].sum()

        # Rename the last column to "TTM"
        cleaned_df = cleaned_df.rename(columns={cleaned_df.columns[-1]: "TTM"})
        # Drop all columns except "TTM"
        cleaned_df = cleaned_df.iloc[:, [-1]]

        # Replace all the NaN values with 0
        cleaned_df = cleaned_df.fillna(0)

    # Calculate some fundamental metrics
    df = fundamentalCalculator(cleaned_df)
    return df


def get_last_column_letter(sheet):
    for i in range(1, 1000):
        if sheet.range(1, i).value is None:
            return sheet.range(1, i - 1).get_address(False, False)
