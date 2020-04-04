#Barfy's Finance
##Intermediate Programming With Python Final Project
###Daniel, John, Jose, & Kay


####Run & Install below line of code in Spyder's terminal to continue 
#conda install -c conda-forge pysimplegui
#or
#!pip install pysimplegui

import PySimpleGUI as sg
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import urllib.request as ur
import json
from os import path

#### John
# getTicker(company)
# Parameters: company -- a string of a company name
# Scrapes a ticker website and searches for the ticker of the company parameter
# Returns: company financial ticker | error if company doesn't exist
def getTicker(company):
    
    url = 'https://www.marketwatch.com/tools/quotes/lookup.asp?siteID=mktw&Lookup='+company.upper()+'&Country=all&Type=All'
    
    page = requests.get(url)
    
    if page.status_code == 200:
        
        #Begin parsing the marketwatch website
        content = BeautifulSoup(page.content, "html.parser")
        
        #Find all HTML hrefrences
        hrefs = content.find_all('a')
        string = str()
        
        #Try - Except determines if company parameter matches what marketwatch found
        try:
            #If there is no class called bottomborder, it means Marketwatch couldn't
            #Find that company
            companyname = str(content.findAll("td", {"class": "bottomborder"})[1])
        except IndexError:
            return sg.PopupError('Not A Real Company')
        else:
            #Check to see if the company name returned by web matches input
            companyname = companyname[25:companyname.find('<', 25)]
            mo = re.search(company.lower(), companyname.lower())
            
            #Scrapes the website and finds the ticker as well, if it exists
            for i in range(len(hrefs)):
                if '/investing/stock' in hrefs[i]['href']:
                    string = str(hrefs[i]['href'])
                    break
            
            #If regular expression finds a match, we return the company ticker
            if mo != None:
                if string[17:] != '':
                    return string[17:].upper()
            #If there is no match, we return that it's not a real company (at least in the eyes of Marketwatch) 
            else:
                return sg.PopupError('Not A Real Company')
            
    else:
        return sg.PopupError('No Response...')

#### John
# companyCheck(ticker)
# Parameters: ticker -- a string financial ticker
# Searches the same marketwatch website. If the inputted company / ticker returns the string
            #'There were no matches found', returns false, otherwise true
            #We do this as another check because Marketwatch should be able to 
            #return the same ticker, if we search for the ticker
# Returns: Boolean -- true if company exists, false otherwise
def companyCheck(ticker):
    url = 'https://www.marketwatch.com/tools/quotes/lookup.asp?siteID=mktw&Lookup='+ticker.upper()+'&Country=all&Type=All'
    
    page = requests.get(url)
    
    if page.status_code == 200:
        
        #Similar to above, search for all important classes
        content = BeautifulSoup(page.content, "html.parser")
        divs = content.findAll("div", {"class": "important"})
        
        #If the length of divs is > 0, this means we found a 'There were no matches found'
        #From Marketwatch
        if len(divs) != 0:
            return False
        else:
            return True
        
    else:
        sg.PopupError('No Response...')

#### John
# calcs(balancesheet)
# Parameters: balancesheet from StockRow.com -- a pandas dataframe
# Searches the balancesheet dataframe for specific indexes, and will use these to calculate
        #ratios for each of the two returned years.
# Returns: Dictionary of calculated ratios
def calcs(balancesheet):
  indexes = balancesheet.index
  
  #We search each row of the balancesheet parameter for the inputs into the ratio equations
  #The excel sheet from stock row has the indexes named, so we must search for
  #The corresponding index of what we're searching for, before we continue
  #We found this to be the easiest way.
  
  CA = {'Year 1' : balancesheet.iloc[indexes.get_loc('Total current assets'), 0],
        'Year 2' : balancesheet.iloc[indexes.get_loc('Total current assets'), 1]}
  CL = {'Year 1' : balancesheet.iloc[indexes.get_loc('Total current liabilities'), 0],
        'Year 2' : balancesheet.iloc[indexes.get_loc('Total current liabilities'), 1]}
  TA = {'Year 1' : balancesheet.iloc[indexes.get_loc('Total Assets'), 0],
        'Year 2' : balancesheet.iloc[indexes.get_loc('Total Assets'), 1]}
  TL = {'Year 1' : balancesheet.iloc[indexes.get_loc('Total liabilities'), 0],
        'Year 2' : balancesheet.iloc[indexes.get_loc('Total liabilities'), 1]}
  OE = {'Year 1' : balancesheet.iloc[indexes.get_loc('Shareholders Equity (Total)'), 0],
        'Year 2' : balancesheet.iloc[indexes.get_loc('Shareholders Equity (Total)'), 1]}
  
  #Calculate debt ratio for each year -- TL/TA
  debtratio = {'Year 1' : round((TL['Year 1']/TA['Year 1']),2),
               'Year 2' : round((TL['Year 2']/TA['Year 2']),2)}
  
  #Calculate current ratio for each year -- CA/CL
  currentratio = {'Year 1' : round((CA['Year 1']/CL['Year 1']),2),
                  'Year 2' : round((CA['Year 2']/CL['Year 2']),2)}
  
  #Calculate asset percentage change -- (TA1 - TA2) / TA2 *100
  assetperchange = round(((balancesheet.iloc[indexes.get_loc('Total Assets'), 1] - balancesheet.iloc[indexes.get_loc('Total Assets'), 0])/balancesheet.iloc[indexes.get_loc('Total Assets'), 0])*100, 2)
  
  #Listed in the sheet, we just grab from it
  ppenet =  {'Year 1' : balancesheet.iloc[indexes.get_loc('Property, Plant, Equpment (Net)'), 0],
             'Year 2' : balancesheet.iloc[indexes.get_loc('Property, Plant, Equpment (Net)'), 1]}
  
  #Calculate debt equity ratio -- TL/OE
  debtequity = {'Year 1' : round((TL['Year 1']/OE['Year 1']),2),
                'Year 2' : round((TL['Year 2']/OE['Year 2']),2)}
  goodcomp = str()
  
  #We then classify the company into a specific financial condition
  #Please see the user instructions for a more visual table than this
  if currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Very Strong Financial Condition'
  
  elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Ok Financial Condition'  

  elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Ok Financial Condition'

  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Ok Financial Condition'
    
  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Poor Financial Condition'

  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Poor Financial Condition'
    
  elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Poor Financial Condition'
    
  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Poor Financial Condition'

  else:
    goodcomp = 'Further Analysis Needed'

  return {'Debt Ratio':debtratio, 'Current Ratio':currentratio, 'Debt Equity Ratio':debtequity, 'Percent Asset Change':assetperchange, 'PPE, Net':ppenet, 'Financial Condition':goodcomp}

#### John
# useCSV(stock, sheet)
# Parameters: stock -- a string financial ticker | sheet -- a string of which financial statement to use
# Downloads the respective sheet as an excel document from stockrow, and outputs it into a pandas dataframe
# Returns: Corresponding 'sheet' -- a dataframe
def useCSV(stock,sheet):
  #stock == ticker. If the ticker doesn't come in as an uppercase, we convert it
  stock = stock.upper()
  
  #Below, we get each specified sheet that follows from the 'sheet' parameter
  if sheet.upper() == 'INCOME STATEMENT':
      IS = requests.get('https://stockrow.com/api/companies/'+stock+'/financials.xlsx?dimension=A&section=Income%20Statement&sort=desc')
      if IS.status_code == 200:
          open(stock+'_IS.xlsx', 'wb').write(IS.content)
      else:
          sg.PopupError('No response...')
  elif sheet.upper() == 'BALANCE SHEET':
      BS = requests.get('https://stockrow.com/api/companies/'+stock+'/financials.xlsx?dimension=A&section=Balance%20Sheet&sort=desc')
      if BS.status_code == 200:
          open(stock+'_BS.xlsx', 'wb').write(BS.content)
      else:
          sg.PopupError('No response...')
  elif sheet.upper() == 'CASH FLOW':
      CF = requests.get('https://stockrow.com/api/companies/'+stock+'/financials.xlsx?dimension=A&section=Cash%20Flow&sort=desc')
      if CF.status_code == 200:
          open(stock+'_CF.xlsx', 'wb').write(CF.content)
      else:
          sg.PopupError('No response...')

  #We then read each downloaded sheet into a pandas dataframe
  #Return the pandas dataframe
  if sheet.upper() == 'INCOME STATEMENT':
    return pd.read_excel(stock+'_IS.xlsx', index_col=0)
  elif sheet.upper() == 'BALANCE SHEET':
    return pd.read_excel(stock+'_BS.xlsx')
  elif sheet.upper() == 'CASH FLOW':
    return pd.read_excel(stock+'_CF.xlsx', index_col=0)

#### John
# balsheet(stock)
# Parameters: stock -- a string financial ticker
# Duplicates useCSV for the balancesheet, but allows easier calculation in the calcs(balancesheet) function
# Returns: Balance Sheet -- a pandas dataframe
def balsheet(stock):
  stock = stock.upper()
  BS = requests.get('https://stockrow.com/api/companies/'+stock+'/financials.xlsx?dimension=A&section=Balance%20Sheet&sort=desc')
  
  #We do the same thing as above, for the balance sheet again
  #This is because the rearranging code (i.e., BS_Editor), requires the balancesheet
  #From the function above, but calcs requires the balance sheet returned here
  #Just a quirk of how we ended up coding them!
  if BS.status_code == 200:
      open(stock+'_BS.xlsx', 'wb').write(BS.content)
  else:
      sg.PopupError('No response...')
    
  return pd.read_excel(stock+'_BS.xlsx', index_col =0)

#### Daniel
# useWebscraping(url, sheet)
# Parameters: url -- a string financial ticker | sheet -- a string corresponding to the financial statement to get
# Scrapes the Yahoo Finance website and places information for each sheet into a dataframe
# Returns: Pandas Dataframe -- containing the information from financial sheets
def useWebScraping(url,sheet):
#------------------Income Sheet-------------------------------------------------
  if sheet.upper() == 'INCOME STATEMENT':
    url = url.upper()
    url_is = 'https://finance.yahoo.com/quote/' + url + '/financials?p=' + url
    read_data = ur.urlopen(url_is).read()
    soup_is=BeautifulSoup(read_data,'lxml')

    ## Data Manipulation
    iss = []
    for l in soup_is.find_all('div'):
      # Find all data structure that is 'div'
      iss.append(l.string) # Add each element one by one on the list
    # Exclude these columns
    iss = [e for e in iss if e not in ('Operating Expenses','Non-recurring Events')]
    # Filter out "none" elements
    new_is = list(filter(None,iss))
    # Start from the 12th position
    new_is = new_is[12:]
    #How many items at beginning?
    count = 0
    for line in new_is:
        if line != 'Total Revenue':
            count += 1
        else:
            break
    # Iterate 4 items at a time and store them in tuples
    is_data = list(zip(*[iter(new_is)]*count))
    # Read it into a Data Frame
    Income_st = pd.DataFrame(is_data[0:])

    ## Data Cleaning
    # First row with be the header
    Income_st.columns = Income_st.iloc[0]
    Income_st = Income_st.iloc[1:,]
    
    #Drop TTM Column
    Income_st.drop(['ttm'], axis = 1, inplace = True)
    
    #Cleanup index
    Income_st.rename(columns={"Annual": ""}, inplace = True)
    Income_st.set_index('', inplace = True)
    Income_st = Income_st.iloc[:,0:2]
      
    return Income_st

#------------------Balance Sheet------------------------------------------------ 
  if sheet.upper() == 'BALANCE SHEET':
    url = url.upper()
    url_bs = 'https://finance.yahoo.com/quote/' + url +'/balance-sheet?p=' + url
    read_data = ur.urlopen(url_bs).read()
    soup_bs=BeautifulSoup(read_data,'lxml')
    # Data Manipulation
    bs = []
    for l in soup_bs.find_all('div'):
      # Find all data structure that is 'div'
      bs.append(l.string) # Add each element one by one on the list  
    # Exclude these columns
    bs = [e for e in bs if e not in ('Operating Expenses','Non-recurring Events')]
    # Filter out "none" elements
    new_bs = list(filter(None,bs))
    # Start from the 12th position
    new_bs = new_bs[12:]
    #How many items at beginning?
    count = 0
    for line in new_bs:
        if line != 'Cash And Cash Equivalents':
            count += 1
        else:
            break
    # Iterate 4 items at a time and store them in tuples
    bs_data = list(zip(*[iter(new_bs)]*count))
    # Read it into a Data Frame
    Balance_st = pd.DataFrame(bs_data[0:])

    ## Data Cleaning
    # First row with be the header
    Balance_st.columns = Balance_st.iloc[0]
    Balance_st = Balance_st.iloc[1:,]
    
    # #Cleanup index
    Balance_st.rename(columns={"Annual": ""}, inplace = True)
    Balance_st.set_index('', inplace = True)
    Balance_st = Balance_st.iloc[:,0:2]

    return Balance_st

#------------------Cash Flow Sheet----------------------------------------------
  if sheet.upper() == 'CASH FLOW':
    url = url.upper()
    url_cf = 'https://finance.yahoo.com/quote/' + url + '/cash-flow?p='+ url
    read_data = ur.urlopen(url_cf).read()

    # Read the URL
    soup_cf=BeautifulSoup(read_data,'lxml')
    ## Data Manipulation
    cf = []
    for l in soup_cf.find_all('div'):
      # Find all data structure that is 'div'
      cf.append(l.string) # Add each element one by one on the list
    # Exclude these columns
    cf = [e for e in cf if e not in ('Operating Expenses','Non-recurring Events')]
    # Filter out "none" elements
    new_cf = list(filter(None,cf))
    # Start from the 12th position
    new_cf = new_cf[12:]
    #How many items are there at the beginning?
    count = 0
    for line in new_cf:
        if line != 'Net Income':
            count += 1
        else:
            break
    # Iterate 4 items at a time and store them in tuples
    cf_data = list(zip(*[iter(new_cf)]*count))
    # Read it into a Data Frame
    Cash_st = pd.DataFrame(cf_data[0:])

    ## Data Cleaning
    # First row with be the header
    Cash_st.columns = Cash_st.iloc[0]
    Cash_st = Cash_st.iloc[1:,]
    
    #Drop TTM Column
    Cash_st.drop(['ttm'], axis = 1, inplace = True)
    
    #Cleanup index
    Cash_st.rename(columns={"Annual": ""}, inplace = True)
    Cash_st.set_index('', inplace = True)
    Cash_st = Cash_st.iloc[:,0:2]

    return Cash_st

#### Daniel
# wsCalcs(bs)
# Parameters: bs -- a pandas dataframe containing the balancesheet
# Takes the bs dataframe and calculates the important financial condition ratios, only for Yahoo Finance
# Returns: Dictionary of calculated financial ratios
def wsCalcs(bs):
  indexes = bs.index
  # Ratio Calculation
  #Exactly the same as calcs function above
  CA = {'Year 1': float(bs.iloc[indexes.get_loc('Total Current Assets'), 0].replace(',','')),
        'Year 2': float(bs.iloc[indexes.get_loc('Total Current Assets'), 1].replace(',',''))}
  CL = {'Year 1': float(bs.iloc[indexes.get_loc('Total Current Liabilities'),0].replace(',','')),
        'Year 2': float(bs.iloc[indexes.get_loc('Total Current Liabilities'),1].replace(',',''))}
  TA = {'Year 1': float(bs.iloc[indexes.get_loc('Total Assets'),0].replace(',','')),
        'Year 2': float(bs.iloc[indexes.get_loc('Total Assets'),1].replace(',',''))}
  TL = {'Year 1': float(bs.iloc[indexes.get_loc('Total Liabilities'),0].replace(',','')),
        'Year 2': float(bs.iloc[indexes.get_loc('Total Liabilities'),0].replace(',',''))}
  OE = {'Year 1': float(bs.iloc[indexes.get_loc("Total stockholders' equity"), 0].replace(',','')),
        'Year 2': float(bs.iloc[indexes.get_loc("Total stockholders' equity"), 1].replace(',',''))}
  debtratio = {'Year 1': round((TL['Year 1']/TA['Year 1']),2),
               'Year 2': round((TL['Year 2']/TA['Year 2']),2)}
  currentratio = {'Year 1': round((CA['Year 1']/CL['Year 1']),2),
                  'Year 2': round((CA['Year 2']/CL['Year 2']),2)}
  assetperchange = round(((float(bs.iloc[indexes.get_loc('Total Assets'), 1].replace(',','')) - TA['Year 1'])/(TA['Year 1']))*100, 2)
  ppenet =  {'Year 1': bs.iloc[indexes.get_loc('Gross property, plant and equipment'), 0].replace(',',''),
             'Year 2': bs.iloc[indexes.get_loc('Gross property, plant and equipment'), 1].replace(',','')}
  debtequity = {'Year 1': round((TL['Year 1']/OE['Year 1']),2),
                'Year 2': round((TL['Year 2']/OE['Year 2']),2)}
  # Analysis of condition of the Company
  goodcomp = str()
  
  if currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Very Strong Financial Condition'
  
  elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Ok Financial Condition'  

  elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Ok Financial Condition'

  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Ok Financial Condition'
    
  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] < 1.5:
    goodcomp = 'Poor Financial Condition'

  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Poor Financial Condition'
    
  elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Poor Financial Condition'
    
  elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] > 1.5:
    goodcomp = 'Poor Financial Condition'

  else:
    goodcomp = 'Further Analysis Needed'
    
  return {'Debt Ratio':debtratio, 'Current Ratio':currentratio, 'Debt Equity Ratio':debtequity, 'Percent Asset Change':assetperchange, 'PPE, Net':ppenet, 'Financial Condition':goodcomp}

#### Kay
# apiCalcs(balancesheet)
# Parameters: balancesheet -- a pandas dataframe
# Calculates the financial ratios from the API's balance sheet dataframe object, only for API
# Returns: Dictionary containing the important financial condition ratios
def apiCals(balanceSheet):
    # debt ratio
    Total_debt_2019 = balanceSheet.loc['Total debt'][0]
    
    #Same ratio calculations as above
    CA = {'Year 1':float(balanceSheet.loc['Total current assets'][0]),
        'Year 2' : float(balanceSheet.loc['Total current assets'][1])}
    CL = {'Year 1': float(balanceSheet.loc['Total current liabilities'][0]),
        'Year 2' : float(balanceSheet.loc['Total current liabilities'][1])}
    TA = {'Year 1':float(balanceSheet.loc['Total assets'][0]),
        'Year 2' : float(balanceSheet.loc['Total assets'][1])}
    TL = {'Year 1':float(balanceSheet.loc['Total liabilities'][0]),
        'Year 2' : float(balanceSheet.loc['Total liabilities'][1])}
    OE = {'Year 1':float(balanceSheet.loc['Total shareholders equity'][0]),
            'Year 2':float(balanceSheet.loc['Total shareholders equity'][1])}

    debtequity = {'Year 1': round((TL['Year 1']/OE['Year 1']),2),
                'Year 2': round((TL['Year 2']/OE['Year 2']),2)}  
    debtratio = {'Year 1' : round((TL["Year 1"] / TA["Year 1"]),2), 
                    'Year 2' : round((TL['Year 2']/TA['Year 2']),2)}
    currentratio = {'Year 1' : round((CA['Year 1']/CL['Year 1']),2),
                    'Year 2' : round((CA['Year 2']/CL['Year 2']),2)}
    assetperchange = round((( TA['Year 1'] - TA['Year 2'])/ TA['Year 2'])*100, 2)
    ppenet =  {'Year 1': float(balanceSheet.loc['Property, Plant & Equipment Net'][0]),
                'Year 2' : float(balanceSheet.loc['Property, Plant & Equipment Net'][1])}
    goodcomp = str()

    #Company financial condition analysis
    if currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] < 1.5:
      goodcomp = 'Very Strong Financial Condition'
    
    elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] < 1.5:
      goodcomp = 'Ok Financial Condition'  
      
    elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] > 1.5:
      goodcomp = 'Ok Financial Condition'
      
    elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] < 1.5:
      goodcomp = 'Ok Financial Condition'
      
    elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] < 1.5:
      goodcomp = 'Poor Financial Condition'
      
    elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] < .4 and debtequity['Year 1'] > 1.5:
      goodcomp = 'Poor Financial Condition'
      
    elif currentratio['Year 1'] >= 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] > 1.5:
      goodcomp = 'Poor Financial Condition'
      
    elif currentratio['Year 1'] < 1.0 and debtratio['Year 1'] > .4 and debtequity['Year 1'] > 1.5:
      goodcomp = 'Poor Financial Condition'
      
    else:
      goodcomp = 'Further Analysis Needed'

    x =  {'Debt Ratio':debtratio, 'Current Ratio':currentratio, 'Debt Equity Ratio':debtequity, 'Percent Asset Change':assetperchange, 'PPE, Net':ppenet, 'Financial Condition':goodcomp}
    
    return x

#### Kay
# combine(data)
# Parameters: data -- a pandas dataframe
# combine the statments of 2019 and 2018 together. Put 2019 before 2018.
# Returns: out -- a dataframe
def combine(data):
    data_2019 = pd.io.json.json_normalize(data['financials'][0])
    data_2018 = pd.io.json.json_normalize(data['financials'][1])
    out = pd.concat([data_2019,data_2018],ignore_index=True)
    out = out.T
    out = out.iloc[::-1]
    print(out)
    print('\n\n')
    return out

#### Kay
# apiPrint(companyName, sheet)
# Parameters: companyName -- a string financial ticker
# combine the statments of 2019 and 2018 together. Put 2019 before 2018.
# Returns: out -- a dataframe
def apiPrint(companyName, sheet):
    
    #Get the response objects for each financial sheet
    general_url = "https://financialmodelingprep.com/api/v3/financials/"
    income_statement_url = general_url + "income-statement/" + companyName
    balance_sheet_url = general_url + "balance-sheet-statement/" + companyName
    cash_flow_url = general_url + "cash-flow-statement/" + companyName
    income_r = requests.get(income_statement_url)
    balance_sheet_r = requests.get(balance_sheet_url)
    cash_flow_r = requests.get(cash_flow_url)
    
    #We then import the data, and combine into one dataframe
    if(income_r.status_code == 200 & balance_sheet_r.status_code == 200 & cash_flow_r.status_code == 200):
        if sheet.upper() == 'INCOME STATEMENT':
            income_data = json.loads(income_r.content.decode('utf-8'))
            income_data = combine(income_data)
            return income_data
        
        elif sheet.upper() == 'BALANCE SHEET':
            balance_data = json.loads(balance_sheet_r.content.decode('utf-8'))
            balance_sheet = combine(balance_data)
            return balance_sheet
        
        elif sheet.upper() == 'CASH FLOW':
            cash_data = json.loads(cash_flow_r.content.decode('utf-8'))
            cash_data = combine(cash_data)
            return cash_data
    else:
        sg.PopupError("stock name incorrect")
        
### Jose
## THIS SECTION CONTAINS 3 FUNCTIONS USED TO EDIT BS, IS, AND SCF ##
# BSeditor(balancesheet)
# Parameters: balancesheet -- a pandas dataframe
# Rearranges, calculates ratios, and edits the pandas dataframe to make it more
        #Similar to ones we see in class
# Returns: BS_edited -- a dataframe
def BSeditor(balancesheet): 
  # converts dates to str for easier manipulation
  balancesheet.columns = balancesheet.columns.astype(str)

  # Grab data for B/S for end of year current and previous 3
  # financial statements source STOCKROW shows BS in 3 month increments for all companies

  BS_EOY = balancesheet.iloc[:,1:3]
  # show values in thousands
  BS_EOY = BS_EOY.div(1000)
  BS_EOY = BS_EOY.round(0)

  #Calculates ratios and rearranges
  pdeltas = []
  ddeltas = []
  for index, row in BS_EOY.iterrows():
      pdelta = round((row[0]-row[1])/(row[1]),2)
      pdeltas.append(pdelta)
      ddelta = (row[0]-row[1])
      ddeltas.append(ddelta)

  BS_EOY['% Change'] = pdeltas
  BS_EOY['$ Change'] = ddeltas

  # inserts row names
  BS_rownam = balancesheet[balancesheet.columns[0]]
  BS_EOY.insert(loc = 0, column = '', value = BS_rownam)

  # insert row headers
  BS_EOY.loc[-1] = ['Assets','','','','']  # adding a row
  BS_EOY.index = BS_EOY.index + 1  # shifting index
  BS_EOY = BS_EOY.sort_index()  
  
  #Inserting row at specific index, and rearrange the index
  pos = BS_EOY.loc[BS_EOY['']=='Total Assets'].index.values
  pos = int(pos)
  nrow = pd.DataFrame({'':'Liabilities', balancesheet.columns[1]:'', balancesheet.columns[2]:'','% Change':'','$ Change':''}, index=[pos+.5])
  BS_EOY = BS_EOY.append(nrow, ignore_index=False)
  BS_EOY = BS_EOY.sort_index().reset_index(drop=True)

  #Inserting row at specific index, and rearrange the index
  pos = BS_EOY.loc[BS_EOY['']=='Total liabilities'].index.values
  pos = int(pos)
  nrow = pd.DataFrame({'':"Shareholders' Equity", balancesheet.columns[1]:'', balancesheet.columns[2]:'','% Change':'','$ Change':''}, index=[pos+.5])
  BS_EOY = BS_EOY.append(nrow, ignore_index=False)
  BS_EOY = BS_EOY.sort_index().reset_index(drop=True)

  # sets dataframe 1st columns as index for compatability with calcs function
  index = BS_EOY[BS_EOY.columns[0]]
  BS_EOY = BS_EOY.drop(columns = [''])
  BS_EOY = BS_EOY.set_index(index, drop = True)

  #get ratios
  ratios = calcs(BS_EOY)
  #append ratios to df
  BS_EOY.loc['Current Ratio'] = [ratios['Current Ratio']['Year 1'], '','','']
  BS_EOY.loc['Debt Ratio'] = [ratios['Debt Ratio']['Year 1'], '','','']
  BS_EOY.loc['Debt Equity Ratio'] = [ratios['Debt Equity Ratio']['Year 1'], '','','']
  BS_EOY.loc['Percent Asset Change'] = [ratios['Percent Asset Change'], '','','']
  BS_EOY.loc['Financial Condition'] = [ratios['Financial Condition'], '','','']
  BS_edited = BS_EOY
  
  return BS_edited

#### Jose
# ISeditor(incstatement)
# Parameters: incstatement -- a pandas dataframe
# Rearranges, calculates ratios, and edits the pandas dataframe to make it more
        #Similar to ones we see in class
# Returns: IS_edited -- a dataframe
def ISeditor(incstatement): 
  # converts dates to str for easier manipulation
  incstatement.columns = incstatement.columns.astype(str)
  # grabas only date, no time values
  dates = []
  for i in incstatement.columns:
      date = i[:10]
      dates.append(date)

  incstatement.columns = dates

  # Grab data for I/S for end of year current and previous 1
  IS_EOY = incstatement.iloc[:,0:2]

  ratios_df = pd.DataFrame(IS_EOY.loc['Revenue Growth'])
  ratios_df = ratios_df.T
  ratios_df = ratios_df.append(IS_EOY.loc['Gross Margin'])
  ratios_df = ratios_df.append(IS_EOY.loc['EBIT Margin'])
  ratios_df = ratios_df.append(IS_EOY.loc['EBT margin'])
  ratios_df = ratios_df.append(IS_EOY.loc['Net Profit Margin'])
  ratios_df = ratios_df.append(IS_EOY.loc['Operating Cash Flow Margin'])

  # drop % values before dividing all by 1000
  IS_EOY.drop('Revenue Growth', inplace=True)
  IS_EOY.drop('Gross Margin', inplace=True)
  IS_EOY.drop('EBIT Margin', inplace=True)
  IS_EOY.drop('EBT margin', inplace=True)
  IS_EOY.drop('Net Profit Margin', inplace=True)
  IS_EOY.drop('Operating Cash Flow Margin', inplace=True)

  # show values in thousands
  IS_EOY = IS_EOY.div(1000)
  IS_EOY = IS_EOY.round(0)

  # re-add % values
  IS_edited = pd.concat([IS_EOY,ratios_df])
  IS_edited = IS_edited[(IS_edited != 0).all(1)]

  return IS_edited

#### Jose
# SCFeditor(scf)
# Parameters: scf -- a pandas dataframe
# Rearranges, calculates ratios, and edits the pandas dataframe to make it more
        #Similar to ones we see in class
# Returns: SCF_edited -- a dataframe
def SCFeditor(scf): 
  # converts dates to str for easier manipulation
  scf.columns = scf.columns.astype(str)
  # grabas only date, no time values
  dates = []
  for i in scf.columns:
      date = i[:10]
      dates.append(date)

  scf.columns = dates

  #grab only values for last two years, EOY represents 'End of Year'
  SCF_EOY = scf.iloc[:,0:2]

  # show values in thousands
  SCF_EOY = SCF_EOY.div(1000)
  SCF_EOY = SCF_EOY.round(0)

  SCF_EOY = SCF_EOY.dropna()
  SCF_edited = SCF_EOY

  return SCF_edited

#This sets the theme of the GUI. We chose Dark Blue because it looks nice!
sg.theme('Dark Blue 3')

#### John
def main():
    
    #Layout provides the exact layout we will see in the GUI
    #You can read more about the layout syntax in PySimpleGUI's cookbook
    #Warning: syntax is extremely specific, and can break the GUI
    layout = [[sg.Text("Welcome to Barfy's Finance! \n\nThis project will print financial statements and ratios for you using several different methods, \nwhich you can choose!\n\n", 
            justification='center')],
            [sg.Text('\nEnter folder to download files to: ')],
              [sg.In(key='input')],
              [sg.FolderBrowse(target='input')],
              [sg.Text()],
            [sg.Radio('Stock Row', "RADIO1", default=True),
             sg.Radio('Yahoo Finance', "RADIO1"),
             sg.Radio('Financial Modeling Prep', "RADIO1")],
            [sg.Text('\nEnter Company Name:')],
              [sg.Input()],
              [sg.Button('Enter'), sg.Exit()]]
    
    #Create's the main window of the GUI, with title "Barfy's Finance"
    window = sg.Window("Barfy's Finance", layout)
    
    #Infinite Loop recommended by PySimpleGUI's cookbook
    #Essentially will keep the program / window open until user exits it
    #Warning: Again, syntax is very specific as outlined by the cookbook,
        #Can easily break the GUI
    while True:
        event, values = window.read() #Needed per the GUI cookbook
        
        #event is anything that happens within the window -- button presses, text enter, etc.
        #Again, very specific according to the cookbook
        if event is None or event == 'Exit':
            break
        try:
            os.chdir(values['input']) #change the directory to the selected path
        except OSError:
            sg.PopupError('Enter valid download directory')
        else:
    
            #Excel Docs
            #values[0] = stockrow ; values[1] = yahoo finance; values[2] = API
            #True vs. False changes due to which radio button is pressed
            if values[0] == True and values[1] == False and values[2] == False:
                
                #values[3] is the company name input
                #Error if nothing is inputted -- we need a 
                if values[3] == '':
                    sg.PopupError('Error! Please Enter Company Name!')
                else:
                    
                    #set company to the inputted name
                    company = values[3]
                    ticker = getTicker(company)
                    
                    #Run first ticker / company check
                    if ticker != 'Error':
                        #Run second ticker / company check
                        if companyCheck(ticker) == True:
                            #Check to see whether the user already searched for
                            #and downloaded files of specific company
                            if path.exists(ticker + 'Income Statement.xlsx') == False:
                                #Again, another exception handler
                                #Stockrow was tricky
                                try:
                                    useCSV(ticker,'Income Statement')
                                except Exception:
                                    sg.PopupError('No response from Stock Row')
                                else:
                                    #Loop over a list of financial statement strings
                                    #We then get the CSV file
                                    #Edit the dataframe / CSV file
                                    #Export the edited version
                                    #Delete the downloaded version
                                    for element in ['Income Statement', 'Balance Sheet', 'Cash Flow']:
                                        if element == 'Income Statement':
                                            sheet = useCSV(ticker,element).iloc[:, 0:2]
                                            sheet_edited = ISeditor(sheet)
                                            sheet_edited.to_excel(values['input']+'/'+ticker+element+'.xlsx')
                                            os.remove(ticker.upper() + '_IS.xlsx')
                                        elif element == 'Balance Sheet':
                                            bs = useCSV(ticker,element)
                                            sheet_edited = BSeditor(bs)
                                            sheet_edited.to_excel(values['input']+'/'+ticker+element+'.xlsx')
                                            os.remove(ticker.upper() + '_BS.xlsx')
                                        elif element == 'Cash Flow':
                                            sheet = useCSV(ticker,element).iloc[:, 0:2]
                                            sheet_edited = SCFeditor(sheet)
                                            sheet_edited.to_excel(values['input']+'/'+ticker+element+'.xlsx')
                                            os.remove(ticker.upper() + '_CF.xlsx')
                                        
                                        #We then autostart the file for the user
                                        os.startfile(values['input']+'/'+ticker+element+'.xlsx')
                                    
                                    #Calculate the ratios of the balancesheet
                                    financials = balsheet(ticker)
                                    calcslist = calcs(financials)
                                    endstring = str()
                                    
                                    #Again, we delete the intially downloaded BS
                                    os.remove(ticker.upper() + '_BS.xlsx')
                                    
                                    #Loop over the dictionary
                                    #Add them all to a string for easy GUI output
                                    for i in calcslist.keys():
                                        if i == 'Percent Asset Change' or i == 'Financial Condition':
                                            tempstring = '\n' + i + ': ' + str(calcslist[i])
                                            endstring += tempstring + '\n'
                                        elif i != 'Percent Asset Change':
                                            tempstring = '\n' + i + ': '
                                            if i != 'Financial Condition':
                                                for e in calcslist[i].keys():
                                                    tempstring+='\t' + str(e) + ': ' + str(calcslist[i][e])
                                            endstring+= tempstring + '\n'
                                    
                                    #We then create another window titled Results (for the ratios)
                                    layout2 = [[sg.Text(endstring)]]
                                    output = sg.Window('Results', layout2)
                                    
                                    #Same code as above -- persistent window
                                    while True:
                                            event, values = output.read()
                                            if event is None or event == 'Exit':
                                                break
                                    output.close()
                            elif path.exists(ticker + 'Income Statement.xlsx') == True:
                                sg.PopupError('File path already exists! Choose different company...')
                        else:
                            sg.PopupError('Error! No Such Company Exists!')
            
            #Webscraping
            #values[1] = yahoo finance / webscraping
            elif values[0] == False and values[1] == True and values[2] == False:
                
                #Create an empty balancesheet
                balancesheet = pd.DataFrame()
                if values[3] == '':
                    sg.PopupError('Error! Please Enter Company Name!')
                else:
                    company = values[3]
                    ticker = getTicker(company)
                    
                    #First ticker check
                    if ticker != 'Error':
                        #Second ticker check
                        if companyCheck(ticker) == True:
                            #Check to see if user already searched the company
                            if path.exists(ticker + 'Income Statement.xlsx') == False:
                                for element in ['Income Statement', 'Balance Sheet', 'Cash Flow']:
                                    
                                    #Loop over the list of financial statements
                                    #Scrape Yahoo Finance for them!
                                    if element == 'Balance Sheet':
                                        balancesheet = useWebScraping(ticker,element)
                                    sheet = useWebScraping(ticker,element)
                                    sheet.to_excel(values['input']+'/'+ticker+element+'.xlsx')
                                    
                                    #Auto start the excel document
                                    os.startfile(values['input']+'/'+ticker+element+'.xlsx')
                                
                                #calculate the ratios
                                calcslist = wsCalcs(balancesheet)
                                endstring = str()
                                
                                #Prints the ratios in the same way as above
                                for i in calcslist.keys():
                                    if i == 'Percent Asset Change' or i == 'Financial Condition':
                                        tempstring = '\n' + i + ': ' + str(calcslist[i])
                                        endstring += tempstring + '\n'
                                    elif i != 'Percent Asset Change':
                                        tempstring = '\n' + i + ': '
                                        if i != 'Financial Condition':
                                            for e in calcslist[i].keys():
                                                tempstring+='\t' + str(e) + ': ' + str(calcslist[i][e])
                                        endstring+= tempstring + '\n'
                                
                                #Another persistent results window
                                layout2 = [[sg.Text(endstring)]]
                                output = sg.Window('Results', layout2)
                                while True:
                                        event, values = output.read()
                                        if event is None or event == 'Exit':
                                            break
                                output.close()
                            elif path.exists(ticker + 'Income Statement.xlsx') == True:
                                sg.PopupError('File path already exists! Choose different company...')
                        else:
                            sg.PopupError('Error! No Such Company Exists!')
            
            #API
            #values[2] = Financial Modeling Prep / API
            elif values[0] == False and values[1] == False and values[2] == True:
                #Create empty balance sheet
                balancesheet = pd.DataFrame()
                if values[3] == '':
                    sg.PopupError('Error! Please Enter Company Name!')
                else:
                    company = values[3]
                    ticker = getTicker(company)
                    #First ticker check
                    if ticker != 'Error':
                        #second ticker check
                        if companyCheck(ticker) == True:
                            #Check to see if user searched for company
                            if path.exists(ticker + 'Income Statement.xlsx') == False:
                                
                                #Loop over financial statements
                                for element in ['Income Statement', 'Balance Sheet', 'Cash Flow']:
                                    if element == 'Balance Sheet':
                                        balancesheet = apiPrint(ticker,element)
                                    sheet = apiPrint(ticker,element)
                                    sheet.to_excel(values['input']+'/'+ticker+element+'.xlsx')
                                   
                                    #Auto start the excel sheet
                                    os.startfile(values['input']+'/'+ticker+element+'.xlsx')
                                
                                #calculate ratios same ways as above!
                                calcslist = apiCals(balancesheet)
                                endstring = str()
                                for i in calcslist.keys():
                                    if i == 'Percent Asset Change' or i == 'Financial Condition':
                                        tempstring = '\n' + i + ': ' + str(calcslist[i])
                                        endstring += tempstring + '\n'
                                    elif i != 'Percent Asset Change':
                                        tempstring = '\n' + i + ': '
                                        if i != 'Financial Condition':
                                            for e in calcslist[i].keys():
                                                tempstring+='\t' + str(e) + ': ' + str(calcslist[i][e])
                                        endstring+= tempstring + '\n'
                                
                                #Persistent results window
                                layout2 = [[sg.Text(endstring)]]
                                output = sg.Window('Results', layout2)
                                while True:
                                        event, values = output.read()
                                        if event is None or event == 'Exit':
                                            break
                                output.close()
                            elif path.exists(ticker + 'Income Statement.xlsx') == True:
                                sg.PopupError('File path already exists! Choose different company...')
                        else:
                            sg.PopupError('Error! No Such Company Exists!')
    #Closes the whole application GUI when user exits
    #Quits the infinite loop
    window.close()

if __name__ == '__main__':
    main()