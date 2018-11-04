import random
import settings
import finance_utils 
import asyncio
import aiohttp


from time import strftime
from datetime import date

from sanic import Sanic, response
from sanic.response import json


app = Sanic()

async def aioGet(*args, **kwargs):
    async with aiohttp.ClientSession() as client:
        async with client.get(*args, **kwargs) as response:
            response.body = await response.read()

            return response

async def aioPost(*args, **kwargs):
    async with aiohttp.ClientSession() as client:
        async with client.post(*args, **kwargs) as response:
            response.body = await response.read()

            return response

async def nlp(message, userId):
    url = 'https://api.api.ai/v1/query'
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': settings.dialogflowToken}
    data = {'v': strftime('%Y%m%d'), 'query': message, 'lang': 'en','sessionId': userId}
    response = await aioPost(url=url, headers=headers, json=data)
    intent = await response.json()
    return intent

async def nlpContext(userId):
    url = 'https://api.api.ai/v1/contexts'
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': settings.dialogflowToken}
    params = {'v': strftime('%Y%m%d'), 'sessionId': userId}
    response = await aioGet(url=url, headers=headers, params=params)
    context = await response.json()
    return context

async def cleverbot(textClean):
    url = "https://www.cleverbot.com/getreply"
    fetchData = await aioGet(url, params={'key': settings.cleverbotToken, 'input': textClean})
    cleverbotData = await fetchData.json()
    return cleverbotData['output']

async def reply(message):
    url = settings.slackUrl
    data = {'text': message }
    await aioPost(url=url, json=data)

async def logicUnit(request): 
    userId = request.json['event']['user']
    textClean = request.json['event']['text'].replace('<@UDGQJD9FT>', '').strip()
    nlpResult = await nlp(textClean, userId)
    intent = nlpResult['result']['metadata'].get('intentName', 'cleverbot')
    
    if intent == 'cleverbot':
        cleverbotOutput = await cleverbot(textClean)
        await reply(cleverbotOutput)
        return
        
    if intent == 'finance':
        queries = {'companyQuery':''.join(e for e in nlpResult['result']['parameters'].get('companies') if e.isalnum()),
            'account':[nlpResult['result']['parameters'].get('accounts')],
            'fiscalPeriod':nlpResult['result']['parameters'].get('fiscalPeriod'),
            'fiscalYear':nlpResult['result']['parameters'].get('number-integer')}
    
    if intent == 'finance-followup':
        context = await nlpContext(userId)
        queries = {'companyQuery':''.join(e for e in context[0]['parameters'].get('companies') if e.isalnum()),
            'account':[context[0]['parameters'].get('accounts')],
            'fiscalPeriod':context[0]['parameters'].get('fiscalPeriod'),
            'fiscalYear':context[0]['parameters'].get('number-integer')}

    tickerData = await finance_utils.resolveTicker(queries["companyQuery"])

    if len(tickerData) == 0:
        message = 'Sorry, I can\'t found the company.'
    else:
        companyData = {'companyTicker':tickerData[0]['ticker'], 'companyName':tickerData[0]['security_name']}
        account = queries['account'][0].replace(' ', '_').replace('?', '')
        financeData = await finance_utils.intrinioData(queries, companyData['companyTicker'], account)
        
        if account == 'balance_sheet':
            balanceSheet = await finance_utils.generateStatement(financeData, finance_utils.balanceSheet_dict)
            message = f'*{queries["fiscalPeriod"]} {queries["fiscalYear"]} Balance Sheet for {companyData["companyName"]} ({companyData["companyTicker"]})*\n```{balanceSheet}```'

        if account == 'income_statement':
            incomeStatement = await finance_utils.generateStatement(financeData, finance_utils.incomeStatement_dict)
            message = f'*{queries["fiscalPeriod"]} {queries["fiscalYear"]} Income Statement for {companyData["companyName"]} ({companyData["companyTicker"]})*\n```{incomeStatement}```'
        
        if account == 'profitability':
            account = ['income_statement', 'balance_sheet']
            incomeStatement_data = await finance_utils.intrinioData(queries, companyData['companyTicker'], account[0])
            balanceSheet_data = await finance_utils.intrinioData(queries, companyData['companyTicker'], account[1])
            incomeStatement = await finance_utils.generate_statementData(incomeStatement_data)
            balanceSheet = await finance_utils.generate_statementData(balanceSheet_data)
            profitability = await finance_utils.generateProfitability(incomeStatement, balanceSheet)
            message = f'Here is some key financial metrics to help you understand the profitability of {companyData["companyName"]}\n*{queries["fiscalPeriod"]} {queries["fiscalYear"]} Profitability of {companyData["companyName"]} ({companyData["companyTicker"]})*\n{profitability}'

        if account == 'liquidity':
            account = 'balance_sheet'
            balanceSheet_data = await finance_utils.intrinioData(queries, companyData['companyTicker'], account)
            balanceSheet = await finance_utils.generate_statementData(balanceSheet_data)
            liquidity = await finance_utils.generateLiquidity(balanceSheet)
            message = f'Here is some key financial metrics to help you understand the profitability of {companyData["companyName"]}\n*{queries["fiscalPeriod"]} {queries["fiscalYear"]} Liquidity of {companyData["companyName"]} ({companyData["companyTicker"]})*\n{liquidity}'
        
        await reply(message)
    return

@app.route('/vitruvina', methods=['POST'])
async def mention(request):
    verifyCheck = request.json.get('challenge')
    if verifyCheck:
        return json({'challenge': verifyCheck})
    
    loop = asyncio.get_event_loop()
    loop.create_task(logicUnit(request))
    
    return response.json(
        {'message': 'Success'},
        headers={'X-Slack-No-Retry': 1},
        status=1490
    )
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)