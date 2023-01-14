import pandas as pd

from DataReparationAuxFunctions import clean_and_reconstruct_fundamentals, fundamentalCalculator


def process_sheet(sheet, max_length_letter):
    # Create a dataframe from the range of cells specified on the sheet
    raw_df = pd.DataFrame(sheet["A1:"+max_length_letter+"104"].value)
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
        # Sum the last 4 columns
        cleaned_df["TTM"] = cleaned_df.iloc[:, -4:].sum(axis=1)
        # Drop all columns except "TTM"
        cleaned_df = cleaned_df.iloc[:, [-1]]

        print(cleaned_df)


    # Calculate some fundamental metrics
    df = fundamentalCalculator(cleaned_df)
    return df

def getLastColumnLetter(sheet):
    for i in range(1, 1000):
        if sheet.range(1,i).value == None:
            return sheet.range(1,i-1).get_address(False, False)