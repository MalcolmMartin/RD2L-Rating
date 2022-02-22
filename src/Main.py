'''
StratzToGo
'''

from dotenv import load_dotenv
import logging
import os
import pandas as pd
import sys
from Bot_Run import bot_main
from Local_Run import local_main

# Set up log file
logging.basicConfig(filename="Stratz2Go.log")

# Have log capture the warnings
logging.captureWarnings(True)

# Lets special characters be printed to console (comment out when done)
sys.stdout.reconfigure(encoding='utf-8')

# Displays entire table instead of sample, max decimals 3
pd.set_option("display.max_rows", None, "display.max_columns",
              None, "display.precision", 3)
    
def main():
    load_dotenv()
    ENVIRONMENT = os.getenv('ENVIRONMENT')
    if ENVIRONMENT == 'Local':
        local_main()
    elif ENVIRONMENT == 'Bot':
        bot_main()
    else:
        print('Unrecognized Environment')
    
main()