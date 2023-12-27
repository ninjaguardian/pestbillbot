#VERSION - 1.1.7


import os
if os.path.isfile('C:/Users/carte/OneDrive/Desktop/Python code/discord/bot.py'):
    botpyloc = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/bot.py'
    system = "pc"
elif os.path.isfile('/home/plum-pi/Desktop/bot.py'):
    botpyloc = '/home/plum-pi/Desktop/bot.py'
    system = "pi"
elif os.path.isfile('/home/container/bot.py'):
    botpyloc = '/home/container/bot.py'
    system = "solar"
else:
    print("Could not detect system.")
    exit()

#/topkdr soon?

print("System:",system)
if system == "pc":
    EVENTIMAGELOC = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/eventimage.png'
    filecsv = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/variables.csv'
    eventembedcolorloc = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/eventembedcolor.txt'
    eventloc = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/event.txt'
    PESTBILL_VARcsv = '/server/plugins/Skript/variables.csv'
    tokenloc = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/BOTTOKEN.txt'
    sftpPASSloc = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/sftpPASS.txt'
    sftpUSERloc = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/sftpUSER.txt'
    githubtokenloc = 'C:/Users/carte/OneDrive/Desktop/Python code/discord/GITTOKEN.txt'
elif system == "solar":
    EVENTIMAGELOC = '/home/container/eventimage.png'
    filecsv = '/home/container/variables.csv'
    eventembedcolorloc = '/home/container/eventembedcolor.txt'
    eventloc = '/home/container/event.txt'
    PESTBILL_VARcsv = '/server/plugins/Skript/variables.csv'
    tokenloc = '/home/container/BOTTOKEN.txt'
    sftpPASSloc = '/home/container/sftpPASS.txt'
    sftpUSERloc = '/home/container/sftpUSER.txt'
    githubtokenloc = '/home/container/GITTOKEN.txt'
elif system == "pi":
    EVENTIMAGELOC = '/home/plum-pi/Desktop/eventimage.png'
    filecsv = '/home/plum-pi/Desktop/variables.csv'
    eventembedcolorloc = '/home/plum-pi/Desktop/eventembedcolor.txt'
    eventloc = '/home/plum-pi/Desktop/event.txt'
    PESTBILL_VARcsv = '/server/plugins/Skript/variables.csv'
    tokenloc = '/home/plum-pi/Desktop/BOTTOKEN.txt'
    sftpPASSloc = '/home/plum-pi/Desktop/sftpPASS.txt'
    sftpUSERloc = '/home/plum-pi/Desktop/sftpUSER.txt'
    githubtokenloc = '/home/plum-pi/Desktop/GITTOKEN.txt'
else:
    print("system is not valid!")
    exit()





#--------------------------------------------------------------------------------------------------
offset = 11

with open(botpyloc, 'r') as f:
    curline = f.readline()
    ver = ''
    for cur in range(len(curline)-offset-1):
        ver = ver+curline[cur+offset]
print("Current:",ver)



from github import Github
from packaging.version import Version, parse
import sys
import subprocess
with open(githubtokenloc, 'r') as f:
    g = Github(f.read())
repo = g.get_repo('ninjaguardian/pestbillbot')

contents = repo.get_contents('bot.py')

decoded = contents.decoded_content
decoded_str = decoded.decode("UTF-8")
decoded_firstline = decoded_str.splitlines()[0]
gitver = ''
for gitcur in range(len(decoded_firstline)-offset):
    gitver = gitver+decoded_firstline[gitcur+offset]
print("Github:",gitver)

def restartpythonscript():
    print("argv was",sys.argv)
    print(f"sys.executable was {sys.executable}")
    print("restart now")
    subprocess.call(["python", os.path.join(sys.path[0], __file__)] + sys.argv[1:])

gitverparsed = parse(gitver)
verparsed = parse(ver)
if gitverparsed>verparsed:
    print("Downloading....")
    with open(botpyloc, 'wb') as f:
        f.write(decoded)
    print("Downloaded new bot.py")
    restartpythonscript()
    exit("New version ran")
elif verparsed>=gitverparsed:
    print("Keep bot.py")
else:
    print("Error getting version")
  
#--------------------------------------------------------------------------------------------------


import time
from discord.ext import commands
from discord import app_commands
import discord
from datetime import datetime
import csv
import pysftp
import codecs
import io
import aiohttp
import aiofiles
import functools
import typing
host = 'ftp.minehut.com'
port = 2223
with open(sftpUSERloc, 'r') as f:
    username = f.read()
with open(sftpPASSloc, 'r') as f:
    password = f.read()
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

with open(tokenloc, 'r') as f:
    BOT_TOKEN = f.read()
CHANNEL_ID = 1139304414885183658
MOD_ONLY_CHANNEL_ID = 1182685204775714887
BYPASS_ROLE = 1139294768090853536
PESTBILL_ID = 1139292425353973790





PERMISSION_NOT_FOUND_EMBED = discord.Embed()
PERMISSION_NOT_FOUND_EMBED.add_field(name="**HEY!**",value=str("""```ansi
[2;31m[2;31mYou do not have permission to do that![0m[2;31m[0m
```"""))
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


def decimal_to_hexadecimal(decimal_num: int):
    hexadecimal_num = hex(decimal_num)
    return hexadecimal_num

def hexadecimal_to_decimal(hexadecimal_str):
    decimal_num = int(hexadecimal_str, 16)
    return decimal_num

def hex_to_ascii(hex_string):
    # Convert the hexadecimal string to bytes
    byte_data = bytes.fromhex(hex_string)

    try:
        # Decode the bytes to ASCII
        ascii_text = byte_data.decode('ascii')
        return ascii_text
    except UnicodeDecodeError:
        # Handle exceptions in case of non-ASCII characters
        return "Unable to decode some characters as ASCII"

def decode_encoded_string(encoded_string, encoding):
    decoded_string = codecs.decode(encoded_string, encoding)
    return decoded_string

def is_server_owner(interaction: discord.Interaction):
    if interaction.user.id == interaction.guild.owner_id:
        return True
    return False

def minutefix():
    if len(str(datetime.now().minute)) == 1:
        return "0"+str(datetime.now().minute)
    else:
        return datetime.now().minute
    

def updateandrestartbot():
    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    channel.send("Checking for updates... (getting current version)")

    offset = 11

    with open(botpyloc, 'r') as f:
        curline = f.readline()
        ver = ''
        for cur in range(len(curline)-offset-1):
            ver = ver+curline[cur+offset]
    print("Current:",ver)
    channel.send(f"Found {ver}\nChecking for updates... (connecting to github)")

    with open(githubtokenloc, 'r') as f:
        g = Github(f.read())
    repo = g.get_repo('ninjaguardian/pestbillbot')

    contents = repo.get_contents('bot.py')

    decoded = contents.decoded_content
    decoded_str = decoded.decode("UTF-8")
    channel.send("Checking for updates... (getting github version)")
    decoded_firstline = decoded_str.splitlines()[0]
    gitver = ''
    for gitcur in range(len(decoded_firstline)-offset):
        gitver = gitver+decoded_firstline[gitcur+offset]
    print("Github:",gitver)
    channel.send(f"Found {gitver}")
    gitverparsed = parse(gitver)
    verparsed = parse(ver)
    if gitverparsed>verparsed:
        channel.send(f"Found new version: {gitver}")
        print("Downloading....")
        with open(botpyloc, 'wb') as f:
            f.write(decoded)
            channel.send(f"Downloaded and restarting. {ver}>{gitver}")
        print("Downloaded new bot.py")
        restartpythonscript()
        exit("New version ran")
        return True
    elif verparsed>=gitverparsed:
        print("Keep bot.py")
        channel.send(f"No new version found ||Github: {gitver}   Current: {ver}||")
        return False
    else:
        channel.send("Error getting version")
        print("Error getting version")
        return False

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)


#Boot message
@bot.event
async def on_ready():
    print("Bot is ready")
    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    await channel.send("Bot is ready")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        await channel.send(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
        await channel.send(e)

#off message
@bot.event
async def on_disconnect():
    print("Turning bot off...")

#if ctx.channel.id == CHANNEL_ID or discord.utils.get(ctx.guild.get_member(ctx.message.author.id).roles, id=BYPASS_ROLE):
#runs if message sent in CHANNEL_ID or by user with BYPASS_ROLE

#@commands.has_role(BYPASS_ROLE)
#Must have BYPASS_ROLE to run

#slash command that only sender can see response too
#@bot.tree.command(name="hello")
#async def hello(interaction: discord.Interaction):
#    await interaction.response.send_message(f"Hello {interaction.user.mention}", ephemeral=True)


@bot.tree.command(description="Gets the current pestbill event")
async def event(ctx):
    file = discord.File(EVENTIMAGELOC, filename='eventimage.png')  
    with open(eventembedcolorloc, 'r') as f:
        EVENT_EMBED=discord.Embed(title="Event", color=int(f.read()))
    with open(eventloc, 'r') as f:
        EVENT_EMBED.add_field(name="",value=f"The current event is **{f.read()}**!", inline=False)
    EVENT_EMBED.set_thumbnail(url="attachment://eventimage.png")

    await ctx.response.send_message(file=file, embed=EVENT_EMBED, ephemeral=True)


@bot.tree.command(description="Sets the current event")
@app_commands.describe(event = "Set the current event", hexcolornohashtag = "Color of embed sidebar as a hex color", imageurl = "URL of the image displayed")
@app_commands.check(is_server_owner)
async def setevent(ctx, event: str=None, hexcolornohashtag: str=None, imageurl: str=None):
    if imageurl is None:
        file = discord.File(EVENTIMAGELOC, filename='eventimage.png')
    else:        
        async with aiohttp.ClientSession() as session:
            async with session.get(imageurl) as resp:
                if resp.status != 200:
                    await ctx.response.send_message("Could not download file!", ephemeral=True)
                eventimgfiledata = io.BytesIO(await resp.read())
                file = discord.File(eventimgfiledata, 'eventimage.png')
                tempf = await aiofiles.open(EVENTIMAGELOC, mode='wb')
                await tempf.write(await resp.read())
                await tempf.close()
    if event is None:
        with open(eventloc, 'r') as f:
            event = f.read()
    if hexcolornohashtag is None:
        with open(eventembedcolorloc, 'r') as f:
            hexcolornohashtag = ""
            hexcolornohashtagconverted = decimal_to_hexadecimal(int(f.read()))
            for curchar in range(len(hexcolornohashtagconverted)-2):
                hexcolornohashtag = hexcolornohashtag+hexcolornohashtagconverted[curchar+2]
    SET_EVENT_EMBED=discord.Embed(title="Event", color=int(hexcolornohashtag, 16))
    SET_EVENT_EMBED.add_field(value=f"Set the current event to: **{event}** and the color to **{hexcolornohashtag}** ||decimal: **{int(hexcolornohashtag, 16)}**||", name="Set image manualy!!!", inline=False)
    SET_EVENT_EMBED.set_thumbnail(url="attachment://eventimage.png")
    await ctx.response.send_message(file=file, embed=SET_EVENT_EMBED, ephemeral=True)
    with open(eventloc, 'w') as f:
        f.write(f'{event}')
    with open(eventembedcolorloc, 'w') as f:
        f.write(f'{int(hexcolornohashtag, 16) }')


@setevent.error
async def setevent_error(interaction: discord.Interaction, error):
    if interaction.user.id == interaction.guild.owner_id:
        await interaction.response.send_message(f"Don't add a #, add one of the https:// things. | {error}", ephemeral=True)
    else:
        await interaction.response.send_message(embed=PERMISSION_NOT_FOUND_EMBED, ephemeral=True)

@bot.tree.command(description="Turns bot off")
@app_commands.check(is_server_owner)
async def shutdown(ctx):
   await ctx.response.send_message("Bot is being shut down...", ephemeral=True)
   channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
   await channel.send("Shutting down bot!")
   await bot.close()

@shutdown.error
async def shutdown_error(interaction: discord.Interaction, error):
    if interaction.user.id == interaction.guild.owner_id:
        await interaction.response.send_message(f"idk what went wrong... {error}", ephemeral=True)
    else:
        await interaction.response.send_message(embed=PERMISSION_NOT_FOUND_EMBED, ephemeral=True)



@bot.tree.command(description="Updates bot.py and restarts bot")
@app_commands.check(is_server_owner)
async def updatebot(ctx):
   await ctx.response.send_message("Updating and restarting bot!", ephemeral=True)
   channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
   await channel.send("Updating and restarting bot!")
   await run_blocking(updateandrestartbot, None, None)
   await ctx.response.edit_original_response("Updated? Maybe?", ephemeral=True)
   

@updatebot.error
async def updatebot_error(interaction: discord.Interaction, error):
    if interaction.user.id == interaction.guild.owner_id:
        await interaction.response.send_message(f"idk what went wrong... {error}", ephemeral=True)
    else:
        await interaction.response.send_message(embed=PERMISSION_NOT_FOUND_EMBED, ephemeral=True)


@bot.tree.command(description="Gets a player's kdr")
@app_commands.describe(player = "The player to check")
async def kdr(interaction: discord.Interaction, player: str):
    kdrresponsetimestart = time.time()
    await interaction.response.send_message('Loading... (getting variables.csv)', ephemeral=True)
    try:
        conn = pysftp.Connection(host=host,port=port,username=username, password=password,cnopts=cnopts)
        CONNWORKED = True
        print("connection established successfully")
    except: 
        CONNWORKED = False
        print('failed to establish connection to targeted server')
    if CONNWORKED is True:
        current_dir = conn.pwd
        print('our current working directory is: ',current_dir)
        print('available list of directories: ',conn.listdir())
        if os.path.exists(filecsv):
            print("file removed")
            os.remove(filecsv)
        conn.get(PESTBILL_VARcsv, localpath=filecsv)
        print("new file got")
        read = []
        with open(filecsv, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                read.append(line)
            print("read new file")
        with open(filecsv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([f"Data last updated {datetime.now().month}/{datetime.now().day}/{datetime.now().year} {datetime.now().hour}:{minutefix()} (MM/DD/YYYY HH:MM CST)"])
            writer.writerows(read)
            print('written')

    await interaction.edit_original_response(content=f"Loading... (getting {player}'s data)")
#____________________________________________

    playerhex = player.encode('utf-8').hex()
    playerhexfix = ""
    PHLEN = 0
    for i in playerhex:
        PHLEN = PHLEN+1
    #PHLENHALF = int(PHLEN/2)
    #print(f"{PHLEN}/2={PHLENHALF}")
    # CURRENTVALUEPHFIX = 0
    # for i in range(PHLENHALF):
    #     if '6a' in playerhex[CURRENTVALUEPHFIX]+playerhex[CURRENTVALUEPHFIX+1]:
    #         playerhexfix = playerhexfix+"4a"
    #     else:              #6a and 4a are j and J
    #         playerhexfix = playerhexfix+str(playerhex[CURRENTVALUEPHFIX]+playerhex[CURRENTVALUEPHFIX+1])
    #     CURRENTVALUEPHFIX = CURRENTVALUEPHFIX+2
    #print(f"playerhexfix>{playerhexfix}")




    print(playerhex.upper())
    print(playerhexfix.upper())


    file = open(filecsv)
    type(file)
    csvreader = csv.reader(file)
    #print(header)
    for row in csv.reader(open(filecsv)):
        rowstr = str(row)
        if not rowstr.find("kdr::uuidname") == -1:
                for row in csvreader:
                    rowstr = str(row)
                    if not rowstr.find("kdr::uuidname") == -1:
                        if not rowstr.find(playerhex.upper()) == -1:
                            if not rowstr.find("]", 0, len(playerhex)+73) == -1:
                                playeruuid = ""
                                for i in range(15,51):
                                    playeruuid = playeruuid+rowstr[i]
                                    #print(rowstr[i])
                                #print("---------------------------------")
                                #print(row)
                                #print(playeruuid)


    #print(rows)
    killshex=""
    for row in csv.reader(open(filecsv)):
        rowstr = str(row)
        if not rowstr.find(f"kills::{playeruuid}") == -1:
            print(row)
            for i in range(59,75):
                killshex=killshex+rowstr[i]
    #print(playeruuid)
    kills=hexadecimal_to_decimal(killshex)
    print(kills)

    deathshex=""
    for row in csv.reader(open(filecsv)):
        rowstr = str(row)
        if not rowstr.find(f"deaths::{playeruuid}") == -1:
            print(row)
            for i in range(60,76):
                deathshex=deathshex+rowstr[i]
    #print(playeruuid)
    deaths=hexadecimal_to_decimal(deathshex)
    print(deaths)

    await interaction.edit_original_response(content=f"Loading... (Finalizing)")


    timestamp = ""
    gettimestampcurrentrow = 0
    for row in csv.reader(open(filecsv)):
        if gettimestampcurrentrow == 0:
            gettimestampcurrentrow = 1
            timestamp = row[0]
            print(row)


    topkdrname = ''

    for row in csv.reader(open(filecsv)):
        rowstr = str(row)
        if not rowstr.find("topkdrname") == -1:
            for i in range(32,len(rowstr)-2):
                #print(rowstr[i])
                topkdrname = topkdrname+rowstr[i]
    topkdrnameencode = topkdrname.encode('utf-8')
    topkdrnamefinal = hex_to_ascii(decode_encoded_string(topkdrnameencode, 'utf-8'))


    if topkdrnamefinal == player:
        KDR_EMBED=discord.Embed(title=f"{player}'s KDR", color=int('e0bd00', 16))
        KDR_EMBED.add_field(value=f'''{player}'s KDR is {round(kills/deaths,2)}!
They also have the **top kdr**!''', name="KDR", inline=False)
    else:
        KDR_EMBED=discord.Embed(title=f"{player}'s KDR", color=int('fa2d1e', 16))
        KDR_EMBED.add_field(value=f"{player}'s KDR is {round(kills/deaths,2)}!", name="KDR", inline=False)
    KDR_EMBED.add_field(value=f"{player}'s has {kills} kills!", name="Kills", inline=False)
    # KDR_EMBED.add_field(value=f'''{player}'s has {deaths} deaths!\n\nIf these numbers are wierdly big, wait a bit and try again. If it's not fixed, contact <@733487800124571679>''', name="Deaths", inline=False)
    KDR_EMBED.add_field(value=f'''{player}'s has {deaths} deaths!''', name="Deaths", inline=False)
    KDR_EMBED.set_thumbnail(url=f'https://mc-heads.net/combo/{player}')
    KDR_EMBED.set_footer(text=f'''{timestamp}
Even if the stats file was recently downloaded, new stats are only added after a restart.''')
    kdrresponsetimeend = time.time()
    kdrresponsetime = kdrresponsetimeend-kdrresponsetimestart
    await interaction.edit_original_response(content=f"Time taken ≈ {kdrresponsetime} seconds",embed=KDR_EMBED)
        
        

#____________________________________________

@kdr.error
async def kdr_error(interaction: discord.Interaction, error):
    if interaction.user.id == interaction.guild.owner_id:
        await interaction.edit_original_response(content=f"Hello owner! This is the error: {error}")
    else:
        KDR_EMBED_ERROR=discord.Embed(title=f"ERROR WHILE FETCHING KDR!", color=int('fa2d1e', 16))
        KDR_EMBED_ERROR.add_field(value='''> The player's name is CASE-SENSITIVE! Make sure you spelled it perfectly with no spaces.
> The player may have had their stats wiped due to them being low.
> The player may have not joined the game before.
> DM <@733487800124571679> for more help!''', name="Common mistakes", inline=False)
        await bot.get_channel(MOD_ONLY_CHANNEL_ID).send(f'''Someone had a kdr error! 
                                                        
ctx: {interaction}

error: {error}''')
        await interaction.edit_original_response(content="",embed=KDR_EMBED_ERROR)










#set up solarhosting.cc and fix rate limiting and update pip. ask in the server?

#pestbill water freezes
#leave messages dont show up for me (maybe donkey) in discordsrv

#/setevent allows url for image
#topkdr npc sending kdr value

#example. /kdr a. someone with name starting with a might get selected instead of nobody. (presumably fixed)

#leaderboard
#/topkdr
#say if player is topkdr


#more stuff in bot-console
#non case sensitive var
#/help
#/ping

bot.run(BOT_TOKEN)
