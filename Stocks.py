import xlwings as xw
import pandas as pd
from win32com.client import constants as xlconstants


def main():
    # Get a reference to the caller workbook
    wb = xw.Book.caller()

    # Create references to specific sheets in the workbook
    financials_sheet = wb.sheets["Financials"]
    tracking_sheet = wb.sheets["Tracking"]
    options_sheet = wb.sheets["Options"]
    income_statement_sheet = wb.sheets["IncomeStatement"]
    balance_sheet_sheet = wb.sheets["BalanceSheet"]
    cash_flow_sheet = wb.sheets["CashFlow"]
    ratios_sheet = wb.sheets["Ratios"]

    # Replace all comas with periods and vice versa in [income_statement_sheet, balance_sheet_sheet, cash_flow_sheet, ratios_sheet]
    pages = [income_statement_sheet, balance_sheet_sheet, cash_flow_sheet, ratios_sheet]
    for page in pages:

        # Create a pandas dataframe from the sheet
        df = (
            page.range("B4:CZ93").options(pd.DataFrame, index=False, header=False).value
        )
        print(df)
        # Replace all periods with a temporary string
        df = df.apply(
            lambda x: x.str.replace(".", "TEMP") if x.dtype == "object" else x
        )
        # Replace all commas with periods
        df = df.apply(lambda x: x.str.replace(",", ".") if x.dtype == "object" else x)
        # Replace all temporary strings with commas
        df = df.apply(
            lambda x: x.str.replace("TEMP", ",") if x.dtype == "object" else x
        )
        # Write the dataframe back to the sheet
        page.range("B4:CZ93").value = df.values


@xw.sub
def clean_pages():
    wb = xw.Book.caller()
    income_statement_sheet = wb.sheets["IncomeStatement"]
    balance_sheet_sheet = wb.sheets["BalanceSheet"]
    cash_flow_sheet = wb.sheets["CashFlow"]
    ratios_sheet = wb.sheets["Ratios"]

    pages = [income_statement_sheet, balance_sheet_sheet, cash_flow_sheet, ratios_sheet]
    for page in pages:
        page.clear()


if __name__ == "__main__":
    xw.Book("Stocks.xlsm").set_mock_caller()
    main()
