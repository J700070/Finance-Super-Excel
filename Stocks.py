import xlwings as xw
import pandas as pd
import matplotlib.pyplot as plt
from DataReparationAuxFunctions import *
from DataManipulation import *
from pairwise_comparison import *
import xlsxwriter


def main():
    # Get a reference to the caller workbook
    wb = xw.Book.caller()

    # Create references to specific sheets in the workbook
    financials_sheet = wb.sheets["Financials"]
    processed_page = wb.sheets["Processed"]
    processedQ_page = wb.sheets["ProcessedQ"]
    dump_page = wb.sheets["Dump"]
    dumpQ_page = wb.sheets["DumpQ"]
    options_page = wb.sheets["Options"]

    # Extract the ticker symbol from the "Dump" sheet and add it to the "Financials" sheet
    ticker = dump_page["A1"].value.replace("https://roic.ai/company/", "")
    financials_sheet["D2"].value = ticker

    # We want to get all the information from the "Dump" sheet, so we need to know the last column
    # We can get this by counting the number of columns in the first row and then converting it to a letter
    max_length_letter_dump = get_last_column_letter(dump_page)
    max_length_letter_dumpQ = get_last_column_letter(dumpQ_page)

    # Process the "Dump" sheet
    df = process_sheet(dump_page, max_length_letter_dump)
    dfQ = process_sheet(dumpQ_page, max_length_letter_dumpQ)

    # Save the result to the "Processed" and "ProcessedQ" sheets
    processed_page["A1"].value = df
    processedQ_page["A1"].value = dfQ

    # Get divisor from options sheet
    divisor = int(options_page["B1"].value)

    # Clean up the pages
    clean_pages(
        financials_sheet, processed_page, dump_page, dumpQ_page, processedQ_page
    )

    # Get market cap from options sheet
    market_cap = int(options_page["B3"].value) * 1e9

    # Print financials
    write_financials(df, dfQ, divisor, financials_sheet, market_cap)


def write_financials(df, dfQ, divisor, financials_sheet, market_cap):
    df["TTM"] = dfQ["TTM"]

    # Basic Data
    aux_df = df.copy().T
    basic_df = pd.DataFrame(index=aux_df.index)
    basic_df["Revenue"] = aux_df["Revenue"] / divisor
    basic_df["Gross Profit"] = aux_df["Gross Profit"] / divisor
    basic_df["EBITDA"] = aux_df["EBITDA"] / divisor
    basic_df["Operating Income"] = aux_df["Operating Income"] / divisor
    basic_df["Net Income"] = aux_df["Net Income"] / divisor
    basic_df["Free Cash Flow"] = aux_df["Free Cash Flow"] / divisor
    basic_df["Revenue per share"] = aux_df["Revenue per share"]
    basic_df["Operating Income per share"] = aux_df["Operating Income per share"]
    basic_df["EPS"] = aux_df["EPS"]
    basic_df["FCF per share"] = aux_df["FCF per share"]
    basic_df["Dividends per share"] = aux_df["Dividends per share"]
    basic_df["Shares"] = aux_df["Weighted Average Shares Outstanding"] / divisor
    basic_df["Shares Diluted"] = (
        aux_df["Weighted Average Shares Outstanding Diluted"] / divisor
    )
    basic_df["Book value per share"] = aux_df["Book value per share"]
    financials_sheet["D20"].value = basic_df.T.iloc[:, -10:]

    # Margins
    margins_df = pd.DataFrame(index=aux_df.index)
    margins_df["Revenue %"] = 100
    margins_df["Gross Margin %"] = aux_df["Gross Profit Ratio"] * 100
    margins_df["R&D %"] = aux_df["Research and Development Exp. Ratio"] * 100
    margins_df["SG&A %"] = (
        aux_df["Selling, General and Administrative Exp. Ratio"] * 100
    )
    margins_df["Other %"] = aux_df["Other Expenses Ratio"] * 100
    margins_df["EBITDA Margin %"] = aux_df["EBITDA ratio"] * 100
    margins_df["Depreciation & Amortization %"] = (
        aux_df["Depreciation and Amortization Ratio"] * 100
    )
    margins_df["Operating Margin %"] = aux_df["Operating Income ratio"] * 100
    margins_df["Interest Income %"] = aux_df["Net Interest Income Ratio"] * 100
    margins_df["Net Margin %"] = aux_df["Net Income ratio"] * 100
    margins_df["Free Cash Flow Margin %"] = aux_df["Free Cash Flow ratio"] * 100
    financials_sheet["D36"].value = margins_df.T.iloc[:, -10:]

    # Profitability
    prof_df = pd.DataFrame(index=aux_df.index)
    prof_df["Return on Assets %"] = aux_df["Return on Assets"] * 100
    prof_df["Return on Equity %"] = aux_df["Return on Equity"] * 100
    prof_df["Return on Capital Employed %"] = aux_df["ROCE"] * 100
    prof_df["Return on Invested Capital %"] = aux_df["Return on Invested Capital"] * 100
    prof_df["Cash Flow Return on Investment %"] = aux_df["CFROI"] * 100
    financials_sheet["D49"].value = prof_df.T.iloc[:, -10:]

    # Financial Health
    fin_health_df = pd.DataFrame(index=aux_df.index)
    fin_health_df["Cash & Cash Equivalents"] = (
        aux_df["Cash and Cash Equivalents"] / divisor
    )
    fin_health_df["Short-Term Investments"] = aux_df["Short-Term Investments"] / divisor
    fin_health_df["Cash & Short-Term Investments"] = (
        aux_df["Cash and Short-Term Investments"] / divisor
    )
    fin_health_df["Long-Term Investements"] = aux_df["Investments"] / divisor
    fin_health_df["Cash & Investments"] = aux_df["Cash & Investments"] / divisor
    fin_health_df["Short-Term Debt"] = aux_df["Short-Term Debt"] / divisor
    fin_health_df["Long-Term Debt"] = aux_df["Long-Term Debt"] / divisor
    fin_health_df["Total Debt"] = aux_df["Total Debt"] / divisor
    fin_health_df["Net Debt"] = aux_df["Total Debt"] / divisor
    fin_health_df["Net Debt w/Investments"] = aux_df["Net Debt w/Investments"] / divisor
    financials_sheet["D60"].value = fin_health_df.T.iloc[:, -1]

    financials_sheet["G61"].value = aux_df["Current Ratio"].iloc[-1]

    a = aux_df["Working Capital"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    b = aux_df["Retained Earnings"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    c = aux_df["Operating Income"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    d = market_cap / aux_df["Total Liabilities"].iloc[-1]
    e = aux_df["Revenue"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    z_score = (1.2 * a) + (1.4 * b) + (3.3 * c) + (0.6 * d) + (1.0 * e)
    financials_sheet["I61"].value = z_score

    financials_sheet["K61"].value = aux_df["EBITDA to Net Debt"].iloc[-1]

    # Other metrics
    other_df = pd.DataFrame(index=aux_df.index)
    other_df["Asset Turnover Ratio"] = aux_df["Asset Turnover Ratio"]
    other_df["Inventory Turnover"] = aux_df["Inventory Turnover"]
    other_df["Receivables Turnover"] = aux_df["Receivables Turnover"]
    financials_sheet["D72"].value = other_df.T.iloc[:, -10:]

    # Chart Data
    chart_df = pd.DataFrame(index=aux_df.index)
    chart_df["Cash and Short-Term Investments"] = (
        aux_df["Cash and Short-Term Investments"] / divisor
    )
    chart_df["Total Debt"] = aux_df["Total Debt"] / divisor
    financials_sheet["D77"].value = chart_df.T.iloc[:, -10:]


@xw.func
def clear_dump():
    wb = xw.Book.caller()

    dump_page = wb.sheets["Dump"]
    dump_page.clear_contents()

    dump_page = wb.sheets["DumpQ"]
    dump_page.clear_contents()

    processed_page = wb.sheets["Processed"]
    processed_page.clear_contents()

    processed_page = wb.sheets["ProcessedQ"]
    processed_page.clear_contents()


@xw.func
def generate_comparison_matrix():
    wb = xw.Book.caller()

    comparison_page = wb.sheets["Comparison"]
    options_page = wb.sheets["Options"]

    # Get list of stocks to compare from options page
    # These values are all cells below A19 until the first empty cell
    stocks_to_compare = options_page["A19"].expand("down").value

    # Make pandas dataframe from list of stocks
    # Both columns and rows are "stocks_to_compare"
    comparison_matrix = pd.DataFrame(index=stocks_to_compare, columns=stocks_to_compare)

    # Write dataframe to excel
    comparison_page["A1"].value = comparison_matrix


def clean_pages(
    financials_sheet, processed_page, dump_page, dump_page_q, processed_page_q
):

    # Clear Dump & Processed
    dump_page.clear_contents()
    dump_page_q.clear_contents()
    processed_page.clear_contents()
    processed_page_q.clear_contents()

    # Clear Financials
    financials_sheet["E20:N79"].value = ""

    # Reprint Text
    financials_sheet["G60"].value = "Current Ratio"
    financials_sheet["I60"].value = "Z-Score"
    financials_sheet["K60"].value = "EBITDA / Net Debt"


if __name__ == "__main__":
    xw.Book("Stocks.xlsm").set_mock_caller()
    main()
