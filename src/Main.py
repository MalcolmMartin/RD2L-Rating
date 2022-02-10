'''
StratzToGo
'''

import fileinput
import logging
import pandas as pd
import sys
from Collection import add_to_collection
from Collection import collection_summary
from Collection import identify_in_summary
from Collection import rank_identified_collection
from Match_Processing import get_processed_match_df
from OriginalLoop import get_dotabuff_hero_lane_data
from Utilities import clean_csv_file

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
    # TODO: Add options for league filtering, columns to print, etc.
    # Error Handling and data validation
    # Scan multiple players sequentially
    # Accept instructions in "command argument(s)" format
    for line in fileinput.input():
        instructions = line.split()
        if instructions[0] == "help":
            print("Command not set up")
        # Reference Data
        if instructions[0] == "dotabuff":
            get_dotabuff_hero_lane_data()
            print("Successfully scraped dotabuff for hero-lane data")
        elif instructions[0] == "opendota":
            print("Command not set up")
        elif instructions[0] == "stratz":
            print("Command not set up")
        # Match Scanning (match_id)
        elif instructions[0] == "match":
            get_processed_match_df(instructions[1])
            print("Successfully scanned match " + instructions[1])
        # League Scanning
        elif instructions[0] == "league":
            print("Command not set up")
        # Player Scanning
        elif instructions[0] == "player":
            print("Command not set up")
        #TODO: Filter remake lobbies
        # Game Collection Scanning (collection_name, match_id(s))
        elif instructions[0] == "collection":
            for match_id in instructions[2:]:
                add_to_collection(instructions[1],
                                  get_processed_match_df(match_id))
            clean_csv_file(instructions[1])
            clean_csv_file(instructions[1] + '_short')
            print("Successfully scanned below matches to " +
                  instructions[1] + " collection:")
            print(*instructions[2:], sep = ", ")
        # Summarize Game Collection (collection_name)
        elif instructions[0] == "summarize":
            collection_summary(instructions[1])
            print("Successfully summarized " + instructions[1] + " collection")
        # Link to team structure (collection_name, player_filename)
        elif instructions[0] == "identify":
            identify_in_summary(instructions[1], instructions[2])
            print("Successfully added player identification from " +
                  instructions[2] + " to " + instructions[1] + " collection")
        #TODO: Add option for no teams (i.e. in-house league)
        # Power Rankings (collection_name)
        elif instructions[0] == "rank":
            rank_identified_collection(instructions[1])
            print("Successfully created power rankings for " +
                  instructions[1] + " collection")
        # RD2L Functions
        elif instructions[0] == "rd2l":
            if instructions[1] == "matches":
                print("Command not set up")
            elif instructions[1] == "":
                print("Command not set up")
        # No command match
        else:
            print("No matching command")
main()