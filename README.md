# Vitruvina
A conversational Slack virtual assistant for a very basic corporate finance analytics, written in Python 3. 

# About
This project is made for University of Leeds Fintech Hackathon 2018 to solve the challenge of improving stakeholders trust by increasing public accessibilities to corporate financial information from leveraging conversational interface. 
It uses external APIs for natural language processing and to retrieve company financials dataset. Analytics are calculated locally within the client and uses event-driven architecture through webhooks to interact with Slack.

# Features
The bot is actively hosted in HiTECH Innovation Leeds Slack workspace. It's able to show company financial accounts such as balance sheet, financial statement and generating basic analytics about profitability and liquidity of a US public company in a given fiscal period.

### Example of profitability analytics

![Alt Text](https://github.com/farhannysf/vitruvina/blob/master/docs/profitabilityExample.gif)

### Example of liquidity analytics

![Alt Text](https://github.com/farhannysf/vitruvina/blob/master/docs/liquidityExample.gif)

### Example of balance sheet

![Alt Text](https://github.com/farhannysf/vitruvina/blob/master/docs/balancesheetExample.gif)

### Example of income statement

![Alt Text](https://github.com/farhannysf/vitruvina/blob/master/docs/incomestatementExample.gif)

# Sites/Tools used

### Tools

* [aiohttp](https://docs.aiohttp.org/en/stable/)
* [asyncio](https://docs.python.org/3.6/library/asyncio.html)
* [python-dotenv](https://github.com/theskumar/python-dotenv)
* [sanic](https://sanicframework.org/)

### APIs

* [Slack](https://api.slack.com/)
* [Dialogflow](https://dialogflow.com/)
* [Intrinio](https://intrinio.com/)
* [Cleverbot](https://www.cleverbot.com/)

