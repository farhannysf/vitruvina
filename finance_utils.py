import random 
import settings
import asyncio
import aiohttp

async def generate_balanceSheet(queries, ticker, account):
    balanceSheet_data = await intrinioData(queries, ticker, account)
    balanceSheet = await generate_statementData(balanceSheet_data)
    
    return balanceSheet

async def financeGet(*args, **kwargs):
    auth = aiohttp.BasicAuth(login = settings.intrinioLogin, password = settings.intrinioPass)
    async with aiohttp.ClientSession(auth=auth) as client:
        async with client.get(*args, **kwargs) as response:
            response.body = await response.read()

            return response

async def resolveTicker(companyQuery):
    url = 'https://api.intrinio.com/securities'
    params = {'query':companyQuery}
    response = await financeGet(url=url, params=params)
    tickerData = await response.json()
    return tickerData['data']


async def intrinioData(queries, companyTicker, account):
    url = 'https://api.intrinio.com/financials/standardized?'
    params = {'identifier':companyTicker, 'statement': account, 'fiscal_year':queries['fiscalYear'], 'fiscal_period':queries['fiscalPeriod']}
    response = await financeGet(url, params=params)
    financeData = await response.json()
    return financeData['data']

async def generate_statementData(financeData):
    statementData = {x['tag']: x['value'] for x in financeData}
    return statementData

async def generateStatement(financeData, accountType):
    statementData = await generate_statementData(financeData)
    statement = '\n\n'.join([f'{accountType.get(key) or key}: USD {value:,}' for key, value in statementData.items()])
    return statement

async def generateProfitability(incomeStatement, balanceSheet):
    totalgrossprofit = incomeStatement.get('totalgrossprofit')
    operatingrevenue = incomeStatement.get('operatingrevenue')
    totaloperatingincome = incomeStatement.get('totaloperatingincome')
    netincome = incomeStatement.get('netincome')
    totalnoncurrentliabilities = balanceSheet.get('totalnoncurrentliabilities')
    totalequity = balanceSheet.get('totalequity')
    totalassets = balanceSheet.get('totalassets')
    retainedearnings = balanceSheet.get('retainedearnings')
    
    try:
        gross_profit = round(totalgrossprofit / operatingrevenue * 100, 2)
        operating_profit = round(totaloperatingincome / operatingrevenue * 100, 2)
        net_profit = round(netincome / operatingrevenue * 100, 2)
        return_on_capital_employed = round(totaloperatingincome / (totalnoncurrentliabilities + totalequity + retainedearnings) * 100, 2)
        return_on_equity = round(totaloperatingincome/ totalequity * 100, 2)
        return_on_assets = round(totaloperatingincome / totalassets * 100, 2)
    

        profitability = await profitabilityString(totalgrossprofit, operatingrevenue, gross_profit, totaloperatingincome, operating_profit, 
            netincome, net_profit, totalnoncurrentliabilities, totalequity, retainedearnings, return_on_capital_employed, return_on_equity, 
            return_on_assets, totalassets)
    
    except:
        profitability = 'Data not available.'

    return profitability

async def generateLiquidity(balanceSheet):
    totalcurrentassets = balanceSheet.get('totalcurrentassets')
    totalcurrentliabilities = balanceSheet.get('totalcurrentliabilities')
    totalnoncurrentliabilities = balanceSheet.get('totalnoncurrentliabilities')
    totalequity = balanceSheet.get('totalequity')
    
    try:
        currentratio = round(totalcurrentassets / totalcurrentliabilities, 2)
        gearingratio = round(totalnoncurrentliabilities / totalequity, 2)
        liquidity = await liquidityString(totalcurrentassets, totalcurrentliabilities, currentratio, totalnoncurrentliabilities, totalequity, gearingratio)
    
    except:
        liquidity = 'Data not available'

    return liquidity

balanceSheet_dict = {
    'cashandequivalents': 'Cash and Equivalent',
    'shortterminvestments': 'Short Term Investments',
    'notereceivable': 'Note Receivable',
    'accountsreceivable': 'Accounts Receivable',
    'netinventory': 'Net Inventory',
    'othercurrentassets': 'Other Current Assets',
    'totalcurrentassets': 'Total Current Assets',
    'netppe': 'Net Property, Plant And Equipment',
    'longterminvestments': 'Long Term Investments',
    'goodwill': 'Goodwill',
    'intangibleassets': 'Intangible Assets',
    'othernoncurrentassets': 'Other Non-Current Assets',
    'totalnoncurrentassets': 'Total Non-Current Assets',
    'totalassets': 'Total Assets',
    'shorttermdebt': 'Short Term Debt',
    'accountspayable': 'Accounts Payable',
    'accruedexpenses': 'Accrued Expenses',
    'totalcurrentliabilities': 'Total Current Liabilities',
    'longtermdebt': 'Long Term Debt',
    'othernoncurrentliabilities': 'Other Non-Current Liabilities',
    'totalnoncurrentliabilities': 'Total Non-Current Liabilities',
    'totalliabilities': 'Total Liabilities',
    'commitmentsandcontingencies': 'Commitments and Contigencies',
    'commonequity': 'Common Equity',
    'retainedearnings': 'Retained Earnings',
    'aoci': 'Accumulated Other Comprehensive Income',
    'totalcommonequity': 'Total Common Equity',
    'totalequity': 'Total Equity',
    'totalequityandnoncontrollinginterests': 'Total Equity And Non-Controlling Interests',
    'totalliabilitiesandequity': 'Total Liabilities and Equity',
    'currentdeferredrevenue': 'Current Deferred Revenue',
    'noncurrentdeferredrevenue': 'Non-Current Deferred Revenue'}

incomeStatement_dict = {
    'operatingrevenue': 'Operating Revenue',
    'totalrevenue': 'Total Revenue',
    'operatingcostofrevenue': 'Operating Cost Of Revenue',
    'totalcostofrevenue': 'Total Cost Of Revenue',
    'totalgrossprofit': 'Total Gross Profit',
    'sgaexpense': 'Selling, General And Administrative Expenses',
    'rdexpense': 'Research And Development Expense',
    'totaloperatingexpenses': 'Total Operating Expense',
    'totaloperatingincome': 'Total Operating Income',
    'otherincome': 'Other Income',
    'totalotherincome': 'Total Other Income',
    'totalpretaxincome': 'Total Pretax Income',
    'incometaxexpense': 'Income Tax Expense',
    'netincomecontinuing': 'Net Income From Continuing Operations ',
    'netincome': 'Net Income',
    'netincometocommon': 'Net Income Available to Common Shareholders',
    'weightedavebasicsharesos': 'Weighted Average Basic Shares Outstanding',
    'basiceps': 'Basic Earnings Per Share',
    'weightedavedilutedsharesos': 'Weighted Average Diluted Shares Outstanding',
    'dilutedeps': 'Diluted Earnings Per Share',
    'weightedavebasicdilutedsharesos': 'Weighted Average Basic Diluted Shares Outstanding',
    'basicdilutedeps': 'Basic Diluted Earnings Per Share',
    'cashdividendspershare': 'Cash Dividend Per Share'
}

async def profitabilityString(totalgrossprofit, operatingrevenue, gross_profit, totaloperatingincome, operating_profit, 
    netincome, net_profit, totalnoncurrentliabilities, totalequity, retainedearnings, return_on_capital_employed, return_on_equity, 
    return_on_assets, totalassets):
    profitability = f'''
*Gross Profit Margin*
```
Total Gross Profit: USD {totalgrossprofit:,}
Operating Revenue: USD {operatingrevenue:,}
Gross Profit Margin: {gross_profit:,}%```
The gross profit margin measures a company's manufacturing or production process efficiency. It is the percentage of sales revenue remaining after subtracting the company’s cost of goods sold.

*Operating Profit Margin*
```
Total Operating Income: USD {totaloperatingincome:,}
Operating Revenue: USD {operatingrevenue:,}
Operating Profit Margin: {operating_profit:,}%
```
Operating margin measures how much profit a company makes on a dollar of sales, after paying for variable costs of production such as wages and raw materials, but before paying interest or tax.

*Net Profit Margin*
```
Net Income: USD {netincome:,}
Operating Revenue: USD {operatingrevenue:,}
Net Profit Margin: {net_profit}%
```
Net profit margin is the percentage of revenue left after all expenses have been deducted from sales.  The measurement reveals the amount of profit that a business can extract from its total sales.

*Return on Capital Employed*
```
Total Operating Income: USD {totaloperatingincome:,}
Total Non-Current Liabilities: USD {totalnoncurrentliabilities:,}
Total Equity: USD {totalequity:,}
Retained Earnings: USD {retainedearnings:,}
Return on Capital Employed: {return_on_capital_employed:,}%
```
Return on Capital Employed measures how efficiently a company can generate profits from its capital employed by comparing net operating profit to capital employed, it shows how many dollars in profits each dollar of capital employed generates.

*Return on Equity*
```
Net Income: USD {netincome:,}
Total Equity: USD {totalequity:,}
Return on Equity: {return_on_equity:,}%
```
Measures the ability of a firm to generate profits from its shareholders investments in the company. In other words, the return on equity ratio shows how much profit each dollar of common stockholders' equity generates.

*Return on Assets*
```
Total Operating Income: USD {totaloperatingincome:,}
Total Assets: USD {totalassets:,}
Return on Assets: {return_on_assets}%
```
ROA is an indicator of how profitable a company is relative to its total assets. It reveals how efficient a company's management is at using its assets to generate earnings.

'''
    return profitability

async def liquidityString(totalcurrentassets, totalcurrentliabilities, currentratio, totalnoncurrentliabilities, totalequity, gearingratio):
    print (currentratio)
    liquidity = f'''
*Current Ratio*
```
Total Current Assets: USD {totalcurrentassets:,}
Total Current Liabilities: USD {totalcurrentliabilities:,}
Current Ratio: {currentratio}:1
```
Current ratio measures a company\'s ability to pay short-term and long-term obligations. 
*Gearing Ratio*
```
Total Non-Current Liabilities: USD {totalnoncurrentliabilities:,}
Total Equity: USD {totalequity:,}
Gearing Ratio: {gearingratio}%
```
The gearing ratio measures the proportion of a company's borrowed funds to the net amount of funds invested in a business by its owners, plus any retained earnings. The ratio indicates the financial risk to which a business is subjected, since excessive debt can lead to financial difficulties.
'''
    return liquidity