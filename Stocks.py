import xlwings as xw
import pandas as pd
import matplotlib.pyplot as plt
from DataReparationAuxFunctions import *
import xlsxwriter 

def main():
    wb = xw.Book.caller()
    financials_sheet = wb.sheets["Financials"]
    processed_page = wb.sheets["Processed"]
    dump_page = wb.sheets["Dump"]
    ticker = dump_page["A1"].value.replace("https://roic.ai/company/", "")
    financials_sheet["D2"].value = ticker
    options_page = wb.sheets["Options"]
    dump_number = calculate_dump_letter(dump_page)
    dump_letter = xlsxwriter.utility.xl_col_to_name(dump_number-2)
    raw_df = pd.DataFrame(dump_page["A1:"+dump_letter+"104"].value)
    raw_df.columns = raw_df.iloc[0]
    raw_df = raw_df.drop(0)
    raw_df.set_index(raw_df.columns[0], drop=True, inplace=True)
    cleaned_df = clean_and_reconstruct_fundamentals(raw_df, reconstruct_df=True)
    market_cap = int(options_page["B3"].value) * 1000000000
    df = FundamentalCalculator(cleaned_df)
    processed_page["A1"].value = df
    divisor = int(options_page["B1"].value)
    clean_pages(financials_sheet, processed_page, dump_page)
    print_financials(df, divisor, financials_sheet, market_cap)
    



    




if __name__ == '__main__':
    xw.Book("Test.xlsm").set_mock_caller()
    main()



def print_financials(df, divisor, financials_sheet, market_cap):
    
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
    basic_df["Shares Diluted"] = aux_df["Weighted Average Shares Outstanding Diluted"] / divisor
    basic_df["Book value per share"] = aux_df["Book value per share"]
    financials_sheet["D20"].value = basic_df.T.iloc[:,-10:]

    # Margins
    margins_df = pd.DataFrame(index=aux_df.index)
    margins_df["Revenue %"] = 100
    margins_df["Gross Margin %"] = aux_df["Gross Profit Ratio"] * 100
    margins_df["R&D %"] = aux_df["Research and Development Exp. Ratio"] * 100
    margins_df["SG&A %"] = aux_df["Selling, General and Administrative Exp. Ratio"] * 100
    margins_df["Other %"] = aux_df["Other Expenses Ratio"] * 100
    margins_df["EBITDA Margin %"] = aux_df["EBITDA ratio"] * 100
    margins_df["Depreciation & Amortization %"] = aux_df["Depreciation and Amortization Ratio"] * 100
    margins_df["Operating Margin %"] = aux_df["Operating Income ratio"]* 100
    margins_df["Interest Income %"] = aux_df["Net Interest Income Ratio"] * 100
    margins_df["Net Margin %"] = aux_df["Net Income ratio"]* 100
    margins_df["Free Cash Flow Margin %"] = aux_df["Free Cash Flow ratio"]* 100
    financials_sheet["D36"].value = margins_df.T.iloc[:,-10:]

    # Profitability
    prof_df = pd.DataFrame(index=aux_df.index)
    prof_df["Return on Assets %"] = aux_df["Return on Assets"] * 100
    prof_df["Return on Equity %"] = aux_df["Return on Equity"] * 100
    prof_df["Return on Capital Employed %"] = aux_df["ROCE"] * 100
    prof_df["Return on Invested Capital %"] = aux_df["Return on Invested Capital"] * 100
    prof_df["Cash Flow Return on Investment %"] = aux_df["CFROI"] * 100
    financials_sheet["D49"].value = prof_df.T.iloc[:,-10:]

    # Financial Health
    fin_health_df = pd.DataFrame(index=aux_df.index)
    fin_health_df["Cash & Cash Equivalents"] = aux_df["Cash and Cash Equivalents"] / divisor
    fin_health_df["Short-Term Investments"] = aux_df["Short-Term Investments"] / divisor
    fin_health_df["Cash & Short-Term Investments"] = aux_df["Cash and Short-Term Investments"] / divisor
    fin_health_df["Long-Term Investements"] = aux_df["Investments"] / divisor
    fin_health_df["Cash & Investments"] = aux_df["Cash & Investments"] / divisor
    fin_health_df["Short-Term Debt"] = aux_df["Short-Term Debt"] / divisor
    fin_health_df["Long-Term Debt"] = aux_df["Long-Term Debt"] / divisor
    fin_health_df["Total Debt"] = aux_df["Total Debt"] / divisor
    fin_health_df["Net Debt"] = aux_df["Total Debt"] / divisor
    fin_health_df["Net Debt w/Investments"] = aux_df["Net Debt w/Investments"] / divisor
    financials_sheet["D60"].value = fin_health_df.T.iloc[:,-1]

    financials_sheet["G61"].value = aux_df["Current Ratio"].iloc[-1]


    a = aux_df["Working Capital"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    b = aux_df["Retained Earnings"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    c = aux_df["Operating Income"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    d = market_cap / aux_df["Total Liabilities"].iloc[-1]
    e = aux_df["Revenue"].iloc[-1] / aux_df["Total Assets"].iloc[-1]
    z_score = (1.2*a)+(1.4*b)+(3.3*c)+(0.6*d)+(1.0*e)
    financials_sheet["I61"].value = z_score
    
    financials_sheet["K61"].value = aux_df["EBITDA to Net Debt"].iloc[-1]


    # Other metrics
    other_df = pd.DataFrame(index=aux_df.index)
    other_df["Asset Turnover Ratio"] = aux_df["Asset Turnover Ratio"]
    other_df["Inventory Turnover"] = aux_df["Inventory Turnover"]
    other_df["Receivables Turnover"] = aux_df["Receivables Turnover"]
    financials_sheet["D72"].value = other_df.T.iloc[:,-10:]

    # Chart Data
    chart_df = pd.DataFrame(index=aux_df.index)
    chart_df["Cash and Short-Term Investments"] = aux_df["Cash and Short-Term Investments"] / divisor
    chart_df["Total Debt"] = aux_df["Total Debt"] / divisor
    financials_sheet["D77"].value = chart_df.T.iloc[:,-10:]

    
@xw.sub()
def clear_dump():
    wb = xw.Book.caller()

    dump_page = wb.sheets["Dump"]
    dump_page.clear_contents()

    processed_page = wb.sheets["Processed"]
    processed_page.clear_contents()

def clean_pages(financials_sheet, processed_page, dump_page):
    
    # Clear Dump & Processed
    dump_page.clear_contents()
    processed_page.clear_contents()

    # Clear Financials
    financials_sheet["E20:N79"].value = ""

    # Reprint Text
    financials_sheet["G60"].value = "Current Ratio"
    financials_sheet["I60"].value = "Z-Score"
    financials_sheet["K60"].value = "EBITDA / Net Debt"


    
# @xw.sub()
# def save_file():
#     wb_from = xw.Book.caller()
#     wb_to = xw.Book(f"{ticker}.xlsx")

#     wb_from.sheets['Financials'].copy()
#     wb_to.sheets['Financials'].copy(after=wb_to.sheets[0])

 
#     wb_to.save()