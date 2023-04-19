import randfacts
import discord
import asyncio
import datetime
import random
from discord.ext import commands
from discord.utils import get
import smtplib
import json
import requests
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
import numpy as np
from PIL import Image
from io import BytesIO
import os

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="$" , intents = intents)
client.remove_command('help')

def get_qoute():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    qoute = json_data[0]['q'] + " -" + json_data[0]['a']
    return(qoute)


async def insertLetter(letter, pos , board):
    board[pos] = letter

async def spaceIsFree(pos , board):
    return board[pos] == ':white_large_square:'

async def printBoard(ctx , board):
    await ctx.send(f"{board[1]}{board[2]}{board[3]}\n{board[4]}{board[5]}{board[6]}\n{board[7]}{board[8]}{board[9]}")

async def isWinner(bo, le):
    return (bo[7] == le and bo[8] == le and bo[9] == le) or (bo[4] == le and bo[5] == le and bo[6] == le) or(bo[1] == le and bo[2] == le and bo[3] == le) or(bo[1] == le and bo[4] == le and bo[7] == le) or(bo[2] == le and bo[5] == le and bo[8] == le) or(bo[3] == le and bo[6] == le and bo[9] == le) or(bo[1] == le and bo[5] == le and bo[9] == le) or(bo[3] == le and bo[5] == le and bo[7] == le)

async def playerMove(ctx , board):
    run = True
    while run:
        msg = await ctx.send("Please select a position to place an \'X\' (1-9):")
        movem = await client.wait_for("message")
        move = movem.content
        try:
            move = int(move)
            if move > 0 and move < 10:
                if await spaceIsFree(move , board):
                    run = False
                    await insertLetter(':x:', move , board)
                else:
                    await ctx.send('Sorry, this space is occupied!')
            else:
                await ctx.send('Please type a number within the range!')
        except:
            await ctx.send('Please type a number!')


async def compMove(board):
    possibleMoves = [x for x, letter in enumerate(board) if letter == ':white_large_square:' and x != 0]
    move = 0

    for let in [':o:', ':x:']:
        for i in possibleMoves:
            boardCopy = board[:]
            boardCopy[i] = let
            if await isWinner(boardCopy, let):
                move = i
                return move

    cornersOpen = []
    for i in possibleMoves:
        if i in [1,3,7,9]:
            cornersOpen.append(i)

    if len(cornersOpen) > 0:
        move = await selectRandom(cornersOpen)
        return move

    if 5 in possibleMoves:
        move = 5
        return move

    edgesOpen = []
    for i in possibleMoves:
        if i in [2,4,6,8]:
            edgesOpen.append(i)

    if len(edgesOpen) > 0:
        move = await selectRandom(edgesOpen)

    return move

async def selectRandom(li):
    import random
    ln = len(li)
    r = random.randrange(0,ln)
    return li[r]

async def isBoardFull(board):
    if board.count(':white_large_square:') > 1:
        return False
    else:
        return True

async def main(ctx):
    board = [':white_large_square:' for x in range(10)]
    await printBoard(ctx , board)

    while not(await isBoardFull(board)):
        if not(await isWinner(board, ':o:')):
            await playerMove(ctx , board)
            await printBoard(ctx , board)
        else:
            await ctx.send('Sorry, 0\'s won this time!')
            break

        if not(await isWinner(board, ':x:')):
            move = await compMove(board)
            if move == 0:
                pass
            else:
                await insertLetter(":o:", move , board)
                await ctx.send(f"Computer placed an 'O\' in position {move}")
                await printBoard(ctx , board)
        else:
            await ctx.send('X\'s won this time! Good Job!')
            break

    if await isBoardFull(board):
        await ctx.send('Tie Game!')


embedhelp = discord.Embed(title = "Help Index" ,description = f"The prefix of the bot is $")
embedhelp.add_field(name = f"`$kick`" , value = f"For more info type $help kick",inline = True)
embedhelp.add_field(name = f"`$ban`" , value = "For more info type $help ban", inline = True)
embedhelp.add_field(name = f"`$inspire`", value ="For more info type $help inspire" , inline = True )
embedhelp.add_field(name = f"`Autorole`" , value = f"For more info type $help autorole" , inline = True)
embedhelp.add_field(name = f"`$suggestion`" , value = f"For more info type $help suggestion" ,inline = True)
embedhelp.add_field(name = f"`$mute / $unmute`" , value = f"For more info type $help mute or $help_unmute" , inline = True)
embedhelp.add_field(name = f"`$giveaway`" , value = f"For more info type $help giveaway" ,inline = True)
embedhelp.add_field(name = f"`Welcoming new members`" , value = f"For more info type $help wlcm",inline = True)
embedhelp.add_field(name = f"`$clear`" , value = f"For more info type $help clear",inline = True)
embedhelp.add_field(name = f"`Leave Messages`" , value = "For more info type help leave")
embedhelp.add_field(name = "`$battle`" , value = "Battle against your friends to earn pride and martian bucks. For more info type $help battle")
embedhelp.add_field(name = "`$give`" , value = "Help out your friends by giving them martianbucks. For more info type $help give")
embedhelp.add_field(name = "`$buy`" , value = "Buy gear to help you out in the field. For more info type $help buy")
embedhelp.add_field(name = "`$sell`" , value = "Sell old gear to make space for shining new ones. For more info type $help sell")
embedhelp.add_field(name = "`$recruit`" , value = "Recruit members to fight for you. They will add to your defense stat. For more info type $help recruit")
embedhelp.add_field(name = "`$shop`" , value = "See what is available for you to buy.")
embedhelp.add_field(name = "`$whois`" , value = "Learn about your enemy before challenging them. For more info type $help whois")
embedhelp.add_field(name = "$punish" , value = "Punish members in the server. For more info type $help punish")
embedhelp.add_field(name = "Ghost Ping Detection" , value = "Detects ghost pings and sends a message stating the message and the author.")
embedhelp.add_field(name = "Facts" , value = "Get random facts by typing `$fact`")
embedhelp.add_field(name = "TictacToe" , value = "Play a quick game of TicTacToe against your computer by typing `$tictactoe`")
embedhelp.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
embedhelp.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")

def convert(time):
    pos = ["s","m","h","d"]
    time_dict={"s" : 1 , "m" : 60 , "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in time:
        return -1

    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    gcount = 0
    mcount = 0
    async for guild in client.fetch_guilds(limit = None):
        gcount += 1
        async for members in guild.fetch_members(limit = None):
            mcount += 1
    await client.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name= f"{gcount} servers and {mcount} users."))

#mongodb
cluster = MongoClient(f'mongodb+srv://Martianbot:{password}@clustermartianbot.erq2f.mongodb.net/MartianBot?retryWrites=true&w=majority')
db = cluster['MartianBot']
collection = db["Settings"]
collectionb = db["Battle"]

@client.command()
async def tictactoe(ctx):
    await main(ctx)

@client.command()
async def fact(ctx):
    x = randfacts.getFact()
    await ctx.send(x)
@client.event
async def on_message_delete(message):
    pings = ["@everyone" , "@here"]
    for member in message.guild.members:
        pings.append(f"<@!{member.id}>")
    for role in message.guild.roles:
        pings.append(f"<@&{role.id}>")
    splits = message.content.split()
    for split in splits:
        if split in pings:
            embed = discord.Embed(title = "Ghost Ping Detected!" , description = f"{message.author.mention}")
            embed.add_field(name = "The message:" , value = message.content)
            embed.set_thumbnail(url = message.author.avatar_url)
            await message.channel.send(embed = embed)
@client.command()
@commands.has_permissions(administrator = True)
async def punish(ctx , member : discord.Member = None , *, punishment):
    if punishment == "ping":
        for i in range(40):
            msg = await ctx.send(member.mention)
            await msg.delete()
        await ctx.send(f"{member.mention} has been pinged 41 times")
    if punishment == "spam":
        for i in range(15):
            await member.send(f"{ctx.author.name} has punished you.")
        await ctx.send(f"{member.mention} has been spammed!")
@client.command()
async def wanted(ctx , member : discord.Member = False):
    if member == False:
        member = ctx.author
    response = requests.get("https://cdn.discordapp.com/attachments/829391016577728585/841259980496699412/wanted.jpg")
    image = Image.open(BytesIO(response.content))
    pic = member.avatar_url
    data = BytesIO(await pic.read())
    pfp = Image.open(data)
    pfp = pfp.resize((306 , 303))
    image.paste(pfp , (68 , 142))
    image.save("profile.jpg")
    await ctx.send(file = discord.File("profile.jpg"))
    os.remove("profile.jpg")

@client.command()
async def invite(ctx):
    embed = discord.Embed(title = "Invite Me!" , description = "https://discord.com/oauth2/authorize?client_id=829348323814408232&permissions=8&scope=bot")
    embed.add_field(name = "Invite Link to the MartianBot server:" , value = "https://discord.gg/dRRVkAxWJW")
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/840910743640604702/840939813413716008/bot_bg.jpg")
    await ctx.send(embed = embed)
#COMMANDS
#Clear Command
@client.command(aliases=["c"])
@commands.has_permissions(manage_messages = True)
async def clear(ctx,amount=2):
    await ctx.channel.purge(limit=amount)


#Kick Command
@client.command(aliases=["k"])
@commands.has_permissions(kick_members = True)
async def kick(ctx,member : discord.Member ,*,reason="no reason provided"):
    server=ctx.guild
    await member.kick(reason=reason)
    await ctx.send(member.name+"has been kicked from this server for"+" "+reason)

#Ban Command
@client.command(aliases=["b"])
@commands.has_permissions(ban_members = True)
async def ban(ctx,member : discord.Member ,*,reason="no reason provided"):
    await member.ban(reason=reason)
    await ctx.send(member.name+"has been banned from this server for"+" "+reason)

#Giveaway Command
@client.command(aliases=["G"])
@commands.has_permissions(administrator = True)
async def giveaway(ctx):
        await ctx.send("Let's start with this giveaway! Answer these questions within 15 seconds.")

        questions = ["Mention the channel you intend to host the giveaway in",
                    "What should be the duration of the giveaway?(s|m|h|d)" ,
                    "What is the prize of this giveaway?"]
        answers = []
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel


        for i in questions:
            await ctx.send(i)

            try:
                msg = await client.wait_for("message" , timeout = 15.0 , check = check)
            except asyncio.TimeoutError:
                await ctx.send(f"You did not answer in time. Please be quicker next time.")
                return
            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"You did not mention the channel properly. Do it like this {ctx.channel.mention} next time")
            return
        channel = client.get_channel(c_id)

        time = convert(answers[1])

        if time == "-1":
            await ctx.send(f"You did not enter the time with a proper unit. Enter the time with units s for second or m for minute or h for hour or d for day")
            return

        if time == "-2":
            await ctx.send(f"You did not enter the time with a proper integer. Please enter the time with a proper integer next time")
            return

        prize = answers[2]

        await ctx.send("The giveaway will be held in "+channel.mention+" and will last"+answers[1])

        embed = discord.Embed(title = "Giveaway!" , description = f"{prize}" , color = ctx.author.color)

        embed.add_field(name = "Hosted By:" , value = ctx.author.mention)
        embed.set_footer(text = f"Ends {answers[1]} from now!")
        my_msg = await channel.send(embed = embed)
        await my_msg.add_reaction("🎉")
        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(my_msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(client.user))

        if len(users) == 0:
            await channel.send(f"Not enough people reacted. The giveaway has been cancelled. 😞")
            return

        winner = random.choice(users)

        await channel.send(f'Congratulations {winner.mention} has won the giveaway! {winner.mention} will be recieving {prize} from {ctx.author.mention}')

#Suggestion Command
@client.command(aliases = ["s"])
async def suggestion(ctx ,*,suggestion):
    cluster1 = MongoClient(f'mongodb+srv://Martianbot:{password}@clustermartianbot.erq2f.mongodb.net/MartianBot?retryWrites=true&w=majority')
    db1 = cluster['MartianBot']
    collection1 = db["Suggestions"]
    await ctx.send("Would you like to send us your email address so that we can mail a reply back? y/n")
    msg = await client.wait_for("message")
    if msg.content == "y":
        await ctx.send("What is your email address")
        msgemailthing = await client.wait_for("message")
        msgemail = msgemailthing.content
    else:
        msgemail = None
        await ctx.send("Ok")
    suggestiondict = {"Suggestion" : suggestion , "Email" : msgemail}
    collection1.insert_one(suggestiondict)
    await ctx.send("Your suggestion has been sent succesfully")


#Mute Command
@client.command(aliases=["m"])
@commands.has_permissions( administrator = True )
async def mute(ctx , *, member : discord.Member):
    serverid = member.guild.id
    x = db.Settings.find_one({"_id": serverid })
    value_mute_role = x["Mute"]
    if value_mute_role == None:
        await ctx.send("You have not set the mute role yet." )
    else:
        nrole = ctx.guild.get_role(value_mute_role)
        await member.add_roles(nrole)
        await ctx.send(f"{member.mention} has been muted succesfully")


#Inspire
@client.command(aliases = ["i"])
async def inspire(ctx):
    qoute = get_qoute()
    await ctx.send(qoute)

#Unmute
@client.command(aliases = ["u"])
@commands.has_permissions(administrator = True)
async def unmute(ctx , member:discord.Member):
    serverid = member.guild.id
    x = db.Settings.find_one({"_id": serverid })
    value_mute_role = x["Mute"]
    muted_role = ctx.guild.get_role(value_mute_role)
    await member.remove_roles(muted_role)
    await ctx.send(f"{member.mention} has been unmuted succesfully")

@client.command()
async def q(ctx , *, Question):
    ans = [
        "Absolutely" ,
        "Not Possible" ,
        "I have searched through all the search engines on this universe and the answer is No."
        "I have searched through all the search engines on this universe and the answer is Yes."
        ]
    random.shuffle(ans)
    answ = ans[1]
    await ctx.send(answ)

@client.command()
async def battle(ctx , *, member : discord.Member):
    if ctx.author.id == member.id :
        await ctx.send("You cannot challenge yourself.")
        return
    clusterb = MongoClient(f"mongodb+srv://Martianbot:{password}@clustermartianbot.erq2f.mongodb.net/MartianBot?retryWrites=true&w=majority")
    Database = clusterb["MartianBot"]
    collectionb = Database["Battle"]
    try:
        dict1 = {"_id" : ctx.author.id , "level" : 1 , "MartianBucks" : 0 , "rank" : "Beginner" , "sweapon" : None , "lweapon" : None , "helmet" : None , "armour" : None , "defenseStat" : 0 , "offenseStat" : 0 , "army" : 0}
        collectionb.insert_one(dict1)
    except:
        pass
    try:
        dict2 = data = {"_id" : member.id , "level" : 1 , "MartianBucks" : 0 , "rank" : "Beginner" , "sweapon" : None , "lweapon" : None , "helmet" : None , "armour" : None , "defenseStat" : 0 , "offenseStat" : 0 , "army" : 0}
        collectionb.insert_one(dict2)
    except:
        pass
    await ctx.send(f"Does {member.mention} want to participate?(y/n)")
    msg = await client.wait_for("message")
    if msg.author == member and msg.content == "y" or msg.content == "Y":
        x = member.id
        y = ctx.author.id
        requester = Database.Battle.find_one({"_id": y})
        warrior = Database.Battle.find_one({"_id" : x})
        value_lvl1 = requester["level"]
        value_lvl2 = warrior["level"]
        #Person2
        if value_lvl1 < 5:
            titleP = "Beginner"
        elif value_lvl1 > 4 and value_lvl1 < 10:
            titleP = "Trainee"
        elif value_lvl1 > 9 and value_lvl1 < 30:
            titleP = "Gladiator"
        elif value_lvl1 > 29 and value_lvl1 < 60:
            titleP = "Veteran"
        elif value_lvl1 > 59 and value_lvl1 < 150 :
            titleP = "Legend"
        elif value_lvl1 > 149:
            titleP = "GODLIKE"
        #Person2
        if value_lvl2 < 5:
            titleF = "Beginner"
        elif value_lvl2 > 4 and value_lvl1 < 10:
            titleF = "Trainee"
        elif value_lvl2 > 9 and value_lvl1 < 30:
            titleF = "Gladiator"
        elif value_lvl2 > 29 and value_lvl1 < 60:
            titleF = "Veteran"
        elif value_lvl2 > 59 and value_lvl1 < 150 :
            titleF = "Legend"
        elif value_lvl2 > 149:
            titleF = "GODLIKE"
        Database.Battle.update_one({"_id" : ctx.author.id} , {"$set":{"rank" : titleP}})
        Database.Battle.update_one({"_id" : member.id} , {"$set":{"rank" : titleF}})
        ui1 = db.Battle.find_one({"_id" : ctx.author.id})
        ui2 = db.Battle.find_one({"_id" : member.id})
        offense1 = ui1["offenseStat"]
        defense1 = ui1["defenseStat"]
        offense2 = ui2["offenseStat"]
        defense2 = ui2["defenseStat"]
        army1 = ui1["army"]
        army2 = ui2["army"]
        total = value_lvl1 + value_lvl2 + offense1 + defense1 + offense2 + defense2
        prob1 = (value_lvl1 + offense1 + defense1) / total
        prob2 = (value_lvl2 + offense2 + defense2) / total
        embedb = discord.Embed(title = "Battle!" , description= f"{ctx.author.mention}  ⚔️ {member.mention}" , color = ctx.author.color)
        embedb.add_field(name = f"Level: {int(value_lvl1)}" , value = f"{titleP}" , inline = True)
        embedb.add_field(name = f"Level: {int(value_lvl2)}" , value = f"{titleF}" , inline = True)
        embedb.add_field(name = f"Chance of {ctx.author.display_name} :" , value = f"{int((prob1*100)+0.5)}%" , inline = False)
        embedb.add_field(name = f"Chance of {member.display_name}:" , value = f"{int((prob2*100)+0.5)}%" , inline = True)
        embedb.add_field(name = f"Offense Stat of {ctx.author.display_name}:" , value = f"{offense1}" , inline = False)
        embedb.add_field(name = f"Offense Stat of {member.display_name}:" , value = f"{offense2}" , inline = True)
        embedb.add_field(name = f"Defense Stat of {ctx.author.display_name}:" , value = f"{defense1}" , inline = False)
        embedb.add_field(name = f"Defense Stat of {member.display_name}:" , value = f"{defense2}" , inline = True)
        embedb.add_field(name = f"Army of {ctx.author.display_name}:" , value = f"{army1} troop(s)" , inline = False)
        embedb.add_field(name = f"Army of {member.display_name}" , value = f"{army2} troops(s)" , inline = True)
        await ctx.send(embed = embedb)

        rn = random.random()
        if prob1 > prob2:
            lesserno = prob2
        if prob2 > prob1:
            lesserno = prob1
        else:
            lesserno = prob1
        if rn > lesserno:
            if lesserno == prob1:
                winner = member
            else:
                winner = ctx.message.author
        if rn < lesserno:
            if lesserno == prob1:
                winner = ctx.message.author
            else:
                winner = member
        winnerdata = Database.Battle.find_one({"_id" : winner.id})
        oldwinnerlvl = winnerdata["level"]
        newwinnerlvl = oldwinnerlvl+0.2
        Database.Battle.update_one({"_id" : winner.id} , {"$set":{"level" : newwinnerlvl}})
        await asyncio.sleep(5)
        embedw = discord.Embed(title = f"The winner is {winner.display_name}" , description = f"{winner.display_name}#{winner.discriminator} will be recieving 500 MartianBucks")
        embedw.add_field(name = f"Level:" , value = f"{int(newwinnerlvl)} (+0.2)")
        await ctx.send(embed = embedw)
        martianbucks = winnerdata["MartianBucks"]
        added = int(martianbucks) + 500
        Database.Battle.update_one({"_id" : winner.id} , {"$set" : {"MartianBucks" : added}})
    if msg.author != ctx.author and msg.content == "n":
        await ctx.send("The battle has been cancelled.")
        return
    else:
        pass

@client.command()
async def shop(ctx):
    embed = discord.Embed(title = "Shop" , description = "A higher offence or defence increases your chance of winning")
    embed.add_field(name = "OFFENSIVE"  , value = "Only one of each type can be used at a time.", inline = False)
    embed.add_field(name = "SOLID WEAPONRY", value = "You will need to sell your previous solid weapon to get a new one" , inline = False)
    embed.add_field(name = "BOXING GLOVE 🥊 (+0.5 offense)" , value = "1000 MartianBucks")
    embed.add_field(name = "KNIFE 🔪 (+1 offence)" , value = "5000 MartianBucks")
    embed.add_field(name = "DAGGER 🗡️ (+5 offense)" , value = "25000 MartianBucks")
    embed.add_field(name = "BOMB 💣  (+10 offense)" , value = "150000 MartianBucks")
    embed.add_field(name = "NUKE ☢️  (+50 offense)" , value = "600000 MartianBucks")
    embed.add_field(name = "LIQUID WEAPONRY" , value = "You will need to sell your previous liquid weapon to get a new one" , inline = False)
    embed.add_field(name = "HELICOBACTER PYLORI 🦠 (+15 offense)" , value = "100000 MartianBucks")
    embed.add_field(name = "NAPALM 🧪(+20 offense)" , value = "500000 MartianBucks")
    embed.add_field(name = "BIOWEAPON : BACILLUS ANTHRACIS 🧫 (+50 offense)" , value = "11000000 MartianBucks")
    embed.add_field(name = "DEFENSIVE" , value = "You cannot have more than one of each type of armour" , inline = False)
    embed.add_field(name = "HELMETS:" , value = "PROTECTS THE HEAD" , inline = False)
    embed.add_field(name = "GENERIC CAP 🧢 (+0.5 defense)" , value = "1000 MartianBucks")
    embed.add_field(name = "RESCUE WORKER'S HELMET⛑️(+1 defense)" , value = "5000 MartianBucks")
    embed.add_field(name = "ASTRONAUT HELMET 👩‍🚀 (+5 defense)" , value = "10000 MartianBucks")
    embed.add_field(name = "CROWN 👑 (+10 defense)" , value = "30000 MartianBucks")
    embed.add_field(name = "MILITARY HELMET 🪖 (+20 defense)" , value = "60000 MartianBucks")
    embed.add_field(name = "ARMOUR:" , value = "CLOTHING TO PROTECT BODY" , inline = False)
    embed.add_field(name = "SAMURAI OUTFIT 👘 (+10 defense)" , value = "30000 MartianBucks")
    embed.add_field(name = "FULL BODY CHAINMAIL🤺 (+30 defense)" , value = "90000 MartianBucks")
    embed.add_field(name = "ARMY (+1 offense per recruit)" , value = "1000 MartianBucks per recruit" , inline = False)
    await ctx.send(embed = embed)

@client.command()
async def buy(ctx , *,itemu):
    item = itemu.lower()
    if item == "boxing glove":
        price = 1000
        gain = 0.5
        type = "sweapon"
        defense_stat = 0
        offense_stat = 0.5
    elif item == "knife":
        price = 5000
        gain = 1
        type = "sweapon"
        defense_stat = 0
        offense_stat = 1
    elif item == "dagger":
        price = 25000
        gain = 5
        type = "sweapon"
        defense_stat = 0
        offense_stat = 5
    elif item == "bomb":
        price = 150000
        gain = 10
        type = "sweapon"
        defense_stat = 0
        offense_stat = 10
    elif item == "nuke" :
        price = 600000
        gain = 50
        type = "sweapon"
        defense_stat = 0
        offense_stat = 50
    elif item == "helicobacter pylori":
        price = 100000
        gain = 15
        type = "lweapon"
        defense_stat = 0
        offense_stat = 15
    elif item == "napalm":
        price = 500000
        gain = 20
        type = "lweapon"
        defense_stat = 0
        offense_stat = 20
    elif item == "bioweapon:bacillus anthracis" or item == "bacillus anthracis":
        price = 11000000
        gain = 50
        type = "lweapon"
        defense_stat = 0
        offense_stat = 50
    elif item == "cap" or item == "generic cap":
        price = 1000
        gain = 0.5
        type = "helmet"
        defense_stat = 0.5
        offense_stat = 0
    elif item == "rescue worker's helmet" or item == "rescue helmet":
        price = 5000
        gain = 1
        type = "helmet"
        defense_stat = 1
        offense_stat = 0
    elif item == "astronaut helmet" or item == "space helmet":
        price = 10000
        gain = 5
        type = "helmet"
        defense_stat = 5
        offense_stat = 0
    elif item == "crown":
        price = 30000
        gain = 10
        type = "helmet"
        defense_stat = 10
        offense_stat = 0
    elif item == "military helmet":
        price = 60000
        gain = 20
        type = "helmet"
        defense_stat = 20
        offense_stat = 0
    elif item == "samurai outfit" or item == "kimono" or item == "samurai armour":
        price = 30000
        gain = 10
        type = "armour"
        defense_stat = 10
        offense_stat = 0
    elif item == "full body chainmail" or item == "chainmail":
        price = 90000
        gain = 30
        type = "armour"
        defense_stat = 30
        offense_stat = 0
    else:
        await ctx.send("item not found")
        return
    try:
        userinfo = db.Battle.find_one({"_id" : ctx.author.id})
        needed = userinfo[type]
    except:
        await ctx.send("You do not have enough money")
    if needed != None:
        await ctx.send("You will need to sell your previous item in the category first")
        return
    else:
        info1 = db.Battle.find_one({"_id" : ctx.author.id})
        money = info1["MartianBucks"]
        defense = info1["defenseStat"]
        attack = info1["offenseStat"]
        new_defense = defense + defense_stat
        new_offense = attack + offense_stat
        if money >= price:
            deducted = money - price
            db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"MartianBucks" : deducted}})
            db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {type : item}})
            db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"defenseStat" : new_defense}})
            db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"offenseStat" : new_offense}})
            await ctx.send(f"{ctx.author.mention} has bought {item} for {price} MartianBucks")
        else:
            await ctx.send("You do not have enough MartianBucks for the transaction")
@client.command()
async def sell(ctx , *, itemu):
    item = itemu.lower()
    if item == "boxing glove":
        price = random.randint(500 , 1000)
        gain = 0.5
        type = "sweapon"
        defense_stat = 0
        offense_stat = 0.5
    elif item == "knife":
        price = random.randint(3000 , 5000)
        gain = 1
        type = "sweapon"
        defense_stat = 0
        offense_stat = 1
    elif item == "dagger":
        price = random.randint(20000 , 25000)
        gain = 5
        type = "sweapon"
        defense_stat = 0
        offense_stat = 5
    elif item == "bomb":
        price = random.randint(100000 , 150000)
        gain = 10
        type = "sweapon"
        defense_stat = 0
        offense_stat = 10
    elif item == "nuke" :
        price = random.randint(400000 , 500000)
        gain = 50
        type = "sweapon"
        defense_stat = 0
        offense_stat = 50
    elif item == "helicobacter pylori":
        price = random.randint(80000 , 100000)
        gain = 15
        type = "lweapon"
        defense_stat = 0
        offense_stat = 15
    elif item == "napalm":
        price = random.randint(400000 , 500000)
        gain = 20
        type = "lweapon"
        defense_stat = 0
        offense_stat = 20
    elif item == "bioweapon:bacillus anthracis" or item == "bacillus anthracis":
        price = random.randint(10000000 , 11000000)
        gain = 50
        type = "lweapon"
        defense_stat = 0
        offense_stat = 50
    elif item == "cap" or item == "generic cap":
        price = random.randint(700 , 1000)
        gain = 0.5
        type = "helmet"
        defense_stat = 0.5
        offense_stat = 0
    elif item == "rescue worker's helmet" or item == "rescue helmet":
        price = random.randint(4000 , 5000)
        gain = 1
        type = "helmet"
        defense_stat = 1
        offense_stat = 0
    elif item == "astronaut helmet" or item == "space helmet":
        price = random.randint(7000 , 10000)
        gain = 5
        type = "helmet"
        defense_stat = 5
        offense_stat = 0
    elif item == "crown":
        price = random.randint(25000 , 30000)
        gain = 10
        type = "helmet"
        defense_stat = 10
        offense_stat = 0
    elif item == "military helmet":
        price = random.randint(40000 , 60000)
        gain = 20
        type = "helmet"
        defense_stat = 20
        offense_stat = 0
    elif item == "samurai outfit" or item == "kimono" or item == "samurai armour":
        price = random.randint(20000 , 30000)
        gain = 10
        type = "armour"
        defense_stat = 10
        offense_stat = 0
    elif item == "full body chainmail" or item == "chainmail":
        price = random.randint(70000, 90000)
        gain = 30
        type = "armour"
        defense_stat = 30
        offense_stat = 0
    else:
        await ctx.send("item not found")
        return
    infom = db.Battle.find_one({"_id" : ctx.author.id})
    if infom[type] != item:
            await ctx.send("You don't have this item")
            return
    await ctx.send(f"The merchant offered {price} for your {item}. Would you like to take it? (y/n)")
    msg = await client.wait_for("message")

    if msg.author == ctx.author and msg.content == "y" :
        db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {type : None}})
        userinfo = db.Battle.find_one({"_id" : ctx.author.id})
        martianbucks = userinfo["MartianBucks"]
        add = int(martianbucks) + price
        db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"MartianBucks" : add}})
        await ctx.send(f"{ctx.author.mention} has succesfully sold his {item}")
    else:
        return
@client.command()
async def recruit(ctx , *, quantityn):
    quantity = int(quantityn)
    offense_stat_add = 0
    price = 0
    for i in range(quantity):
        offense_stat_add += 1
        price += 1000
    try:
        uinfo = collectionb.find_one({"_id" : ctx.author.id})
        offense = uinfo["offenseStat"]
        money = uinfo["MartianBucks"]
        army = uinfo["army"]
    except:
        await ctx.send("You do not have enough money.")
        return
    if price <= money :
        newoffense = offense + offense_stat_add
        newmoney = money - price
        newarmy = army + offense_stat_add
        db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"offenseStat" : newoffense}})
        db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"MartianBucks" : newmoney}})
        db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"army" : newarmy}})
        await ctx.send(f"{ctx.author.mention} now has {newarmy} troop(s), {newmoney} MartianBucks and {newoffense} offense stat ")
    if price > money :
        await ctx.send("You don't have enough money")
        return
@client.command()
async def whois(ctx , *, member : discord.Member):
    try:
        ui1 = collectionb.find_one({"_id" : member.id})
        martianbucks = ui1["MartianBucks"]
        rank = ui1["rank"]
        offense1 = ui1["offenseStat"]
        defense1 = ui1["defenseStat"]
        army1 = ui1["army"]
        primary = ui1["sweapon"]
        secondary =  ui1["lweapon"]
        helmet =  ui1["helmet"]
        armour = ui1["armour"]
    except:
        martianbucks = 0.00
        rank = "Beginner"
        offense1 = "0"
        defense1 = "0"
        army1 = "0"
        primary = "None"
        secondary = "None"
        helmet = "None"
        armour = "None"
    embedj = discord.Embed(title = f"{member.display_name}#{member.discriminator}" , description = f"UserID: {member.id}")
    embedj.add_field(name = "MartianBucks:" , value = f"**{martianbucks}**")
    embedj.add_field(name = "Rank:" , value = rank)
    embedj.add_field(name = "Offense Stat:" , value = f"**{offense1}**" , inline = False)
    embedj.add_field(name = "Defense Stat:" , value = f"**{defense1}**" , inline = False)
    embedj.add_field(name = "Primary Weapon:" , value = f"**{primary}**" , inline = False)
    embedj.add_field(name = "Secondary Weapon:" , value = f"**{secondary}**" , inline = False)
    embedj.add_field(name = "Helmet:" , value = f"**{helmet}**" , inline = False)
    embedj.add_field(name = "Armour:" , value = f"**{armour}**" , inline = False)
    embedj.set_thumbnail(url = member.avatar_url)
    embedj.set_footer(text = f"Requested by {ctx.author.display_name}#{ctx.author.discriminator}" , icon_url = ctx.author.avatar_url)
    await ctx.send(embed = embedj)
@client.command()
async def give(ctx , member : discord.Member , amount):
    moneytogive = int(amount)
    try:
        allinfodonor = db.Battle.find_one({"_id" : ctx.author.id})
        martianbucksdonor = allinfodonor["MartianBucks"]
    except:
        await ctx.send("You do not have enough money.")
        return
    if martianbucksdonor >= int(amount) :
        aftergive = int(martianbucksdonor) - int(amount)
        db.Battle.update_one({"_id" : ctx.author.id} , {"$set" : {"MartianBucks" : aftergive}})
    else:
        await ctx.send("You do not have enough money")
        return

    try:
        data = {"_id" : member.id , "level" : 1 , "MartianBucks" : 0 , "rank" : "Beginner" , "sweapon" : None , "lweapon" : None , "helmet" : None , "armour" : None ,defenseStat : 0 , offenseStat : 0 , "army" : 0}
        db.Battle.insert_one(data)
        bonus = amount
        db.Battle.update_one({"_id": member.id}, {"$set": {"MartianBucks": bonus}})
        await ctx.send(f"**{member.display_name}#{member.discriminator}** has received {amount} MartianBucks from **{ctx.author.display_name}#{ctx.author.discriminator}**")
    except:
        acceptordata = db.Battle.find_one({"_id" : member.id})
        acceptorbucks = acceptordata["MartianBucks"]
        bonus = int(acceptorbucks) + int(amount)
        db.Battle.update_one({"_id": member.id}, {"$set": {"MartianBucks": bonus}})
        await ctx.send(f"**{member.display_name}#{member.discriminator}** has received {amount} MartianBucks from **{ctx.author.display_name}#{ctx.author.discriminator}**")
#On bot join
@client.event
async def on_guild_join(guild):
    serverid = guild.id
    settings = {"_id" : serverid , "WelcomeChannel:" : None , "GoodbyeChannel:" : None , "Autorole": None , "Mute":None , "Userleavemsg" : None , "Userjoinmsg" : None}
    collection.insert_one(settings)

#On bot leave
@client.event
async def on_guild_remove(guild):
    serverid = guild.id
    db.Settings.delete_one({"_id" : serverid})




@client.event
async def on_member_join(member):
    embedjoin = discord.Embed(title = "Welcome to the server!" , description = member.mention , color = member.color)
    embedjoin.set_thumbnail(url = member.avatar_url)
    serverid = member.guild.id
    x = collection.find_one({"_id": serverid })
    value_welcomechannel = x["WelcomeChannel:"]
    if value_welcomechannel != None:
        nchannel = client.get_channel(value_welcomechannel)
        await nchannel.send(embed = embedjoin)
    else:
        return

    y = collection.find_one({"_id": serverid })
    value_wlcm_msg = y["Userjoinmsg"]
    value_autorole = y["Autorole"]
    if value_wlcm_msg != None:
        await nchannel.send(value_wlcm_msg)
    if value_autorole != None:
        role = member.guild.get_role(value_autorole)
        await member.add_roles(role)


@client.event
async def on_member_remove(member):
    serverid = member.guild.id
    xyz = collection.find_one({"_id": serverid })
    value_leavechannel = xyz["GoodbyeChannel:"]
    if value_leavechannel != None:
        nchannel = client.get_channel(value_leavechannel)
    if value_leavechannel == None:
        return
    xyxz = collection.find_one({"_id" : serverid})
    value_leavemessage = xyxz["Userleavemsg"]
    if value_leavemessage == None:
        await nchannel.send(f"{member.name}#{member.discriminator} has left this server.")
    else:
        await nchannel.send(f"{member.name}#{member.discriminator} has left this server. {value_leavemessage}")



#Help Commands
@client.command()
async def help(ctx , *,type = "n"):
    type = type.lower()
    if type == "punish":
        embed = discord.Embed(title = "`$punish`" , description = "Punish members in the server with this command" , color = ctx.author.color)
        embed.add_field(name = "Features:" , value = "MartianBot can punish users in two ways. The first method punishes them by ghost pinging them 40 times and then pinging them for confirming that the user has been pinged. The second method punishes them by spamming messages in their DM")
        embed.add_field(name = "Permissions Required" , value = "The user is required to have administrator permission to use this command")
        embed.add_field(name = "Syntax:" , value = "$punish <@member> <ping / spam>")
        await ctx.send(embed = embed)
    elif type == "battle":
        embed = discord.Embed(title = "`$battle`" , color = ctx.author.color)
        embed.add_field(name = "Syntax:" , value = f"$battle {ctx.author.mention}")
        await ctx.send(embed = embed)
    elif type == "give":
        embed = discord.Embed(title = "`$give`" , color = ctx.author.color)
        embed.add_field(name = "Syntax" , value = f"$give {ctx.author.mention} 0")
        await ctx.send(embed = embed)
    elif type == "buy":
         embed = discord.Embed(title = "`$buy`" , color = ctx.author.color)
         embed.add_field(name = "Syntax" , value = "$buy Boxing Glove")
         await ctx.send(embed = embed)
    elif type == "sell":
        embed = discord.Embed(title = "`$sell`" , color = ctx.author.color)
        embed.add_field(name = "Syntax" , value = "$sell Boxing Glove")
        await ctx.send(embed = embed)
    elif type == "recruit":
        embed = discord.Embed(title = "`$recruit`" , color = ctx.author.color)
        embed.add_field(name = "Syntax" , value = "$recruit 5")
        await ctx.send(embed = embed)
    elif type == "whois":
        embed = discord.Embed(title = "`$whois`" , color = ctx.author.color)
        embed.add_field(name = "Syntax" , value = f"$whois {ctx.author.mention}")
        await ctx.send(embed = embed)
    elif type == "leave":
        embed = discord.Embed(title = "Leave Messages" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"Set the channel where the leave message will be sent by typing $setchannelleave <#channel> and the message can be set by typing $setleavemsg <message>" , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission to kick members to use this command. Other users will not be able to use this." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "kick":
        embed = discord.Embed(title = "$kick" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The kick command can be used by typing `$kick @member`. Example: $kick {ctx.author.mention} " , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission to kick members to use this command. Other users will not be able to use this." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "ban":
        embed = discord.Embed(title = "$ban" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The ban command can be used by typing `$ban @member`. Example: $ban {ctx.author.mention} " , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have permission to ban members to use this command. Other users will not be able to use this." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "inspire":
        embed = discord.Embed(title = "$inspire" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The inspire command can be used to send an inspirational qoute. Example: `$inspire`" , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission to send messages to use this command." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "autorole":
        embed = discord.Embed(title = "Autorole" , color = ctx.author.color)
        embed.add_field(name = "What it does:" , value = f"The Autorole feature of the bot automatically gives a new member a role." , inline = True)
        embed.add_field(name = "Roles required:" , value = "The server is required to have a role set by typing $setautorole <@role>" , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "suggestion":
        embed = discord.Embed(title = "$suggestion" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The suggestion command lets users post their suggestions to improve the bot. It can be used by typing $suggestion <Your suggestion here>. Example: `$suggestion Add a feature`" , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission to read messages to use this command." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "mute":
        embed = discord.Embed(title = "$mute" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The mute command can be used by typing `$mute @member`. Example : $mute {ctx.author.mention}. The muted role is also required to be set by typing $setmuterole <@role> ", inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission to mute members to use this command. Other users will not be able to use this." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "unmute":
        embed = discord.Embed(title = "$unmute" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The unmute command can be used by typing `$unmute @member`. Example: $unmute {ctx.author.mention} " , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission of administrator to use this command. Other users will not be able to use this." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "giveaway":
        embed = discord.Embed(title = "$giveaway" , color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The giveaway command can be used by typing $giveaway. example:`$giveaway`" , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission of administrator to use this command. Other users will not be able to use this." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "wlcm":
        embed = discord.Embed(title = "Welcoming New Members" , color = ctx.author.color)
        embed.add_field(name = "Usage" , value = f"The bot welcomes the members in a channel set by typing $setchanneljoin. The new members are also sent a message welcoming them to the server. A custom welcome message can also be set by typing '$setmsgwlcm <message>`" , inline = True)
        embed.add_field(name = "Things required:" , value = "The channel for the message has to be set in the server" , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    elif type == "clear":
        embed = discord.Embed(title = "`$clear`", color = ctx.author.color)
        embed.add_field(name = "How to use:" , value = f"The clear command can be used by typing `clear <no.of messages>`. Example: `$clear 5`" , inline = True)
        embed.add_field(name = "Permissions required:" , value = "The user is required to have the permission to manage messages to use this command. Other users will not be able to use this." , inline = True)
        embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/829391016577728585/830829763572138004/bot_bg.jpg')
        embed.set_footer(text = f"For more questions, send an email to questions.martianbot@gmail.com")
        await ctx.send(embed = embed)
    else:
        await ctx.send(embed = embedhelp)
#Settings Stuff
@client.command()
@commands.has_permissions(administrator = True)
async def setchanneljoin(ctx , *, channel : discord.TextChannel):
    channel_id = channel.id
    serverid = ctx.guild.id
    db.Settings.update_one({"_id": serverid},{"$set":{"WelcomeChannel:": channel_id}})
    await ctx.send("Updated Succesfully")


@client.command()
@commands.has_permissions(administrator = True)
async def setchannelleave(ctx , *,channel : discord.TextChannel):
    channelid = channel.id
    serverid = ctx.guild.id
    db.Settings.update_one({"_id": serverid},{"$set":{"GoodbyeChannel:": channelid}})
    await ctx.send("Updated Succesfully")


@client.command()
@commands.has_permissions(administrator = True)
async def setmuterole(ctx, *,role : discord.Role):
    role_id = role.id
    serverid = ctx.guild.id
    db.Settings.update_one({"_id": serverid},{"$set":{"Mute": role_id}})
    await ctx.send("Muted role has been updated succesfully")

@client.command()
@commands.has_permissions(administrator = True)
async def setautorole(ctx, *,role : discord.Role):
    role_id = role.id
    serverid = ctx.guild.id
    db.Settings.update_one({"_id": serverid},{"$set":{"Autorole": role_id}})
    await ctx.send("Autorole has been updated succesfully")


@client.command()
@commands.has_permissions(administrator = True)
async def setwlcmmsg(ctx , *, message):
    serverid = ctx.guild.id
    db.Settings.update_one({"_id" : serverid} , {"$set":{"Userjoinmsg" : message}})
    await ctx.send("Welcome message has been updated succesfully")

@client.command()
@commands.has_permissions(administrator = True)
async def setleavemsg(ctx , *, message):
    serverid = ctx.guild.id
    db.Settings.update_one({"_id" : serverid} , {"$set":{"Userleavemsg" : message}})
    await ctx.send("Leave message has been updated succesfully")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.channel.send(f'ERROR: Forbidden. Missing Permissions!')
    if isinstance(error, commands.BotMissingAnyRole):
        await ctx.channel.send(f'ERROR: Bot Missing Any Role')
    if isinstance(error, commands.BotMissingRole):
        await ctx.channel.send(f'ERROR: Bot Missing Role')
    if isinstance(error, commands.CommandInvokeError):
        raise error
    else:
        pass

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $clear <number of messages to clear>")


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $kick @<member>")


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $ban @<member>")


@suggestion.error
async def suggestion_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $suggestion <Your suggestion>.")


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $mute @<member>.")

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $unmute @<member>")


@q.error
async def q_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $q <question>")


@battle.error
async def battle_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $battle @<member>")


@buy.error
async def buy_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $buy <item name>")

@punish.error
async def punisherror(ctx , error):
    if isinstance(error , commands.MissingRequiredArgument):
        await ctx.send("Syntax : $punish <@member> <punishment (ping / spam)>")

@sell.error
async def sell_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $sell <item name>")


@recruit.error
async def recruit_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $recruit <number of troops to recruit>")


@give.error
async def give_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $give <amount>")


@whois.error
async def whois_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $whois @<member>")


@setchanneljoin.error
async def chanjoin(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $setchanneljoin #<channel>")


@setchannelleave.error
async def chanleave(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $setchannelleave #<channel>")

@setmuterole.error
async def muterole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $setmuterole @<role>")


@setautorole.error
async def autorole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Syntax : $setautorole @<role>")
client.run("ODI5MzQ4MzIzODE0NDA4MjMy.YG200A.Q7TOZZ2LWgkFpJltDZy7buGMAQg")
