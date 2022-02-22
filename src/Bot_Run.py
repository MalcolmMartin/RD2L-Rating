'''
StratzToGo
'''

import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os
import pandas as pd
import sys
from Collection import add_to_collection
from Collection import collection_summary
from Collection import identify_in_summary
from Collection import rank_identified_collection
from Match_Processing import get_processed_match_df
from OriginalLoop import get_dotabuff_hero_lane_data
from Utilities import clean_csv_file
    
def bot_main():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    
    bot = commands.Bot(command_prefix='!')
    
    @bot.event
    async def on_ready():
        guild = discord.utils.get(bot.guilds, name=GUILD)
    
        print(
            f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
    
    @bot.command(name='match', \
                 help='Provides Stratz2Go scores for the given match id')
    async def process_match(ctx, match_id):
        processed_df = get_processed_match_df(match_id)
        response = 'Hero Name: Stratz2Go Score'
        for row in processed_df.itertuples(index = True, name ='Pandas'):
                response += '\n' + getattr(row, "hero_name") + ': ' + \
                    f"{getattr(row, 'total_advantage'):.2f}"
        await ctx.send(response)
    
    @bot.command(name='dotabuff', \
                 help='Updates hero-lane expectation data')
    @commands.has_role('stratz-admin')
    async def dotabuff_scrape(ctx):
        get_dotabuff_hero_lane_data()
        response = 'Updated hero-lane expectation data from dotabuff'
        await ctx.send(response)
    
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command')
    
    bot.run(TOKEN)