import discord
import os
import asyncio
import datetime
import requests
import json
import time
import datetime
import champions

print('Logging into Discord...\n')

client = discord.Client()
region = 'na1' # Other regions acceptable since 5/24/2017: ru, kr, br1, oc1, jp1, eun1, euw1, na1, tr1, la1, la2
APIKEY = ''
inUse = False


def requestSummonerInfo(summonerName):
    URL = "https://" + region + ".api.riotgames.com/lol/summoner/v3/summoners/by-name/" + summonerName + "?api_key=" + APIKEY
    response = requests.get(URL)
    return response.json()

def requestCurrentGame(summonerID):
    URL = "https://" + region + ".api.riotgames.com/lol/spectator/v3/active-games/by-summoner/" + summonerID + "?api_key=" + APIKEY
    response = requests.get(URL)
    return response.json()
def findChampion(champID):
    URL = "https://" + region + ".api.riotgames.com/lol/static-data/v3/champions/" + champID + "?api_key=" + APIKEY
    response = requests.get(URL)
    return response.json()
def requestRankedInfo(summonerID):
    URL = "https://" + region + ".api.riotgames.com/lol/league/v3/positions/by-summoner/" + summonerID + "?api_key=" + APIKEY
    response = requests.get(URL)
    return response.json()
@client.event
async def on_message(message):
    global region
    global inUse
    if message.content.startswith('%'):
        if message.content.lower().startswith('%getsummoner'):
            if inUse == True:
                await client.send_message(message.channel, 'Currently gathering data! Please wait a moment!')
                return
            '''
                Usage: !getsummoner <summonername>
                Returns the summoner name, level and summoner ID of the name specified
            '''
            inUse = True
            userstr = message.content
            userstr = userstr.replace("%getsummoner", "")
            userstr = userstr.replace(" ", "")
            responseJSON = requestSummonerInfo(userstr)
            try:
                summonerID = responseJSON['id']
                summonerID = str(summonerID)
            except:
                await client.send_message(message.channel, 'Player ' + userstr + ' does not exist!')
                inUse = False
                return
            summonerName = responseJSON['name']
            summonerName = str(summonerName)
            summonerLevel = responseJSON['summonerLevel']
            summonerLevel = str(summonerLevel)
            em = discord.Embed(description='**Summoner Name: **' + summonerName + '\n**Summoner ID: **' + summonerID + '\n**Summoner Level: **' + summonerLevel, colour=0x0099FF)
            em.set_author(name='Result')
            await client.send_message(message.channel, '', embed=em)
            inUse = False
        elif message.content.lower().startswith('%gamestatus'):
            '''
                Usage: !gamestatus <summonername>
                Returns the game status of the summoner name specified
            '''
            if inUse == True:
                await client.send_message(message.channel, 'Currently gathering data! Please wait a moment!')
                return
            inUse = True
            userstr = message.content
            userstr = userstr.replace("%gamestatus", "")
            userstr = userstr.replace(" ", "")
            playerList = '\n'
            playerList2 = '\n'
            responseJSON = requestSummonerInfo(userstr)
            try:
                summonerID = responseJSON['id']
                summonerID = str(summonerID)
            except:
                await client.send_message(message.channel, 'Player ' + userstr + ' does not exist!')
                inUse = False
                return
            gameResponseJSON = requestCurrentGame(summonerID)
            try:
                gameMode = gameResponseJSON['gameMode']
                gameMode = str(gameMode)
            except:
                await client.send_message(message.channel, 'This player is not in a game!')
                inUse = False
                return
            await client.send_message(message.channel, '*Please wait while I fetch the data...*')
            gameTime = gameResponseJSON['gameLength']
            gameTime = int(gameTime)
            mins, gameTime = divmod(gameTime, 60)
            hours, mins = divmod(mins, 60)
            currentGameTime = ('%02d:%02d:%02d' % (hours, mins, gameTime))
            time.sleep(9)
            for x in gameResponseJSON['participants']:
                summonerName = x['summonerName']
                gameID = x['summonerId']
                gameID = str(gameID)
                champion = x['championId']
                # currentChampion = findChampion(str(champion))
                try:
                    currentChampion = champions.get_champion(int(champion))
                except:
                    currentChampion = 'CHAMPION NOT FOUND'
                # champName = currentChampion['name']
                # champName = str(champName)
                # Get the persons ranked info too because we're dicks
                rankedResponseJSON = requestRankedInfo(gameID)
                try:
                    if str(rankedResponseJSON[0]['queueType']) == 'RANKED_SOLO_5x5':
                        rankedTier = rankedResponseJSON[0]['tier']
                        rankedRank = rankedResponseJSON[0]['rank']
                    else:
                        rankedTier = 'Unranked'
                        rankedRank = ''
                except:
                    rankedTier = 'Unranked or Not Found'
                    rankedRank = ''
                team = x['teamId']
                if team == 100:
                    playerList += ('**Summoner Name: **' + str(summonerName) + '\n**Champion: **' + currentChampion + '\n**Solo Queue Rank: **' + str(rankedTier) + ' ' + str(rankedRank) + '\n\n')
                elif team == 200:
                    playerList2 += ('**Summoner Name: **' + str(summonerName) + '\n**Champion: **' + currentChampion + '\n**Solo Queue Rank: **' + str(rankedTier) + ' ' + str(rankedRank) + '\n\n')
            em = discord.Embed(description=playerList, colour=0x0099FF)
            em2 = discord.Embed(description=playerList2, colour=0x990099) 
            em.set_author(name='Blue Team')
            em2.set_author(name='Purple Team')
            await client.send_message(message.channel, '{}'.format(message.author.mention) + '\n**Gamemode: **' + gameMode + '\n**Current Game Time: **' + '`' + str(currentGameTime) + '`')
            await client.send_message(message.channel, '', embed=em)
            await client.send_message(message.channel, '', embed=em2)
            inUse = False
        
        elif message.content.lower() == '%help':
            em = discord.Embed(description='`%getsummoner <summonername>` - Gets the summoner name, level and ID of the name specified. \n`%gamestatus <summonername>` - Gets the current game status of the name specified.', colour=0xB3ECFF)
            em.set_author(name='All Commands', icon_url=client.user.avatar_url)
            await client.send_message(message.channel, '', embed=em)
        elif message.content.lower() == '%shutdown':
            if message.author.top_role.permissions.administrator:
                await client.send_message(message.channel, 'Shutting down...')
                await client.logout()


            
@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    await client.change_presence(game=discord.Game(name='Type %help'))

    
client.run('key')