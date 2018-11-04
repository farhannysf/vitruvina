from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

dialogflowToken = environ['dialogflowToken']
cleverbotToken = environ['cleverbotToken']
slackUrl= environ['slackUrl']
intrinioLogin = environ['intrinioLogin']
intrinioPass = environ['intrinioPass']