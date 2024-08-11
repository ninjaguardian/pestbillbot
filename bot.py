#VERSION - 1.2.5

# This work is licensed under CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/deed.en
# By ninjaguardian on github


EVENT_IMAGE_LOC = './eventimage.png'
VARS_CSV_LOC = './variables.csv'
EVENT_COLOR_LOC = './eventembedcolor.txt'
EVENT_LOC = './event.txt'
DISCORD_BOT_TOKEN_LOC = './BOTTOKEN.txt'
SFTP_PASS_LOC = './sftpPASS.txt'
SFTP_USER_LOC = './sftpUSER.txt'
GITHUB_TOKEN_LOC = './GITTOKEN.txt'
SFTP_CSV_LOC = '/server/plugins/Skript/variables.csv'


KEY9217_lolz_h1br0_te5t='123456789dseasd'
TOKEN = 'KEY9217_lolz_h1br0_te5t=123456789dseasd'
test = 'fio-u-================================================================'


#--------------------------------------------------------------------------------------------------
offset = 11

with open(__file__, 'r') as f:
    curline = f.readline()
    ver = ''
    for cur in range(len(curline)-offset-1):
        ver = ver+curline[cur+offset]
print("Current:",ver)



from github import Github
from packaging.version import Version, parse
import sys
import subprocess
with open(GITHUB_TOKEN_LOC, 'r') as f:
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
    with open(__file__, 'wb') as f:
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
with open(SFTP_USER_LOC, 'r') as f:
    username = f.read()
with open(SFTP_PASS_LOC, 'r') as f:
    password = f.read()
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

with open(DISCORD_BOT_TOKEN_LOC, 'r') as f:
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
    print("Checking for updates... (getting current version)")

    offset = 11

    with open(__file__, 'r') as f:
        curline = f.readline()
        ver = ''
        for cur in range(len(curline)-offset-1):
            ver = ver+curline[cur+offset]
    print("Current:",ver)
    print(f"Found {ver}\nChecking for updates... (connecting to github)")

    with open(GITHUB_TOKEN_LOC, 'r') as f:
        g = Github(f.read())
    repo = g.get_repo('ninjaguardian/pestbillbot')

    contents = repo.get_contents('bot.py')

    decoded = contents.decoded_content
    decoded_str = decoded.decode("UTF-8")
    print("Checking for updates... (getting github version)")
    decoded_firstline = decoded_str.splitlines()[0]
    gitver = ''
    for gitcur in range(len(decoded_firstline)-offset):
        gitver = gitver+decoded_firstline[gitcur+offset]
    print("Github:",gitver)
    print(f"Found {gitver}")
    gitverparsed = parse(gitver)
    verparsed = parse(ver)
    if gitverparsed>verparsed:
        print(f"Found new version: {gitver}")
        print("Downloading....")
        with open(__file__, 'wb') as f:
            f.write(decoded)
            print(f"Downloaded and restarting. {ver}>{gitver}")
        print("Downloaded new bot.py")
        restartpythonscript()
        exit("New version ran")
        return True
    elif verparsed>=gitverparsed:
        print("Keep bot.py")
        print(f"No new version found ||Github: {gitver}   Current: {ver}||")
        return False
    else:
        print("Error getting version")
        print("Error getting version")
        return False

async def run_blocking(blocking_func: typing.Callable) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)


#Boot message
@bot.event
async def on_ready():
    print(f"Bot is ready ({ver} on {system})")
    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    await channel.send(f"Bot is ready ({ver} on {system})")

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

@bot.tree.command(description="Shows the bot latency")
async def ping(ctx):
    SET_PING_EMBED=discord.Embed(title="Ping", color=int('1e63d4', 16))
    SET_PING_EMBED.add_field(name="",value=f'''The bot's ping is: {bot.latency}ms''',inline=False)
    await ctx.response.send_message(embed=SET_PING_EMBED, ephemeral=True)

@bot.tree.command(description="Gets the current pestbill event")
async def event(ctx):
    file = discord.File(EVENT_IMAGE_LOC, filename='eventimage.png')  
    with open(EVENT_COLOR_LOC, 'r') as f:
        EVENT_EMBED=discord.Embed(title="Event", color=int(f.read()))
    with open(EVENT_LOC, 'r') as f:
        EVENT_EMBED.add_field(name="",value=f"The current event is **{f.read()}**!", inline=False)
    EVENT_EMBED.set_thumbnail(url="attachment://eventimage.png")

    await ctx.response.send_message(file=file, embed=EVENT_EMBED, ephemeral=True)


@bot.tree.command(description="Sets the current event")
@app_commands.describe(event = "Set the current event", hexcolor = "Color of embed sidebar as a hex color", imageurl = "URL of the image displayed")
@app_commands.check(is_server_owner)
async def setevent(ctx, event: str=None, hexcolor: str=None, imageurl: str=None):
    if imageurl is None:
        file = discord.File(EVENT_IMAGE_LOC, filename='eventimage.png')
    else:        
        async with aiohttp.ClientSession() as session:
            async with session.get(imageurl) as resp:
                if resp.status != 200:
                    await ctx.response.send_message("Could not download file!", ephemeral=True)
                eventimgfiledata = io.BytesIO(await resp.read())
                file = discord.File(eventimgfiledata, 'eventimage.png')
                tempf = await aiofiles.open(EVENT_IMAGE_LOC, mode='wb')
                await tempf.write(await resp.read())
                await tempf.close()
    if event is None:
        with open(EVENT_LOC, 'r') as f:
            event = f.read()
    if hexcolor is None:
        with open(EVENT_COLOR_LOC, 'r') as f:
            hexcolor = ""
            hexcolornohashtagconverted = decimal_to_hexadecimal(int(f.read()))
            for curchar in range(len(hexcolornohashtagconverted)-2):
                hexcolor = hexcolor+hexcolornohashtagconverted[curchar+2]
    else:
        hexcolor=hexcolor.replace("#","")
    SET_EVENT_EMBED=discord.Embed(title="Event", color=int(hexcolor, 16))
    SET_EVENT_EMBED.add_field(value=f"Set the current event to: **{event}** and the color to **#{hexcolor}** ||decimal: **{int(hexcolor, 16)}**||", name="Image may not work as expected.", inline=False)
    SET_EVENT_EMBED.set_thumbnail(url="attachment://eventimage.png")
    await ctx.response.send_message(file=file, embed=SET_EVENT_EMBED, ephemeral=True)
    with open(EVENT_LOC, 'w') as f:
        f.write(f'{event}')
    with open(EVENT_COLOR_LOC, 'w') as f:
        f.write(f'{int(hexcolor, 16) }')


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


# @bot.tree.command(description="Updates bot.py and restarts bot")
# @app_commands.check(is_server_owner)
# async def updatebot(ctx):
#    await ctx.response.send_message("Updating and restarting bot!", ephemeral=True)
#    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
#    await channel.send("Updating and restarting bot!")
#    await run_blocking(updateandrestartbot)
#    await ctx.edit_original_response(content="Updated? Maybe?")
   

# @updatebot.error
# async def updatebot_error(interaction: discord.Interaction, error):
#     if interaction.user.id == interaction.guild.owner_id:
#         await interaction.edit_original_response(content=f"idk what went wrong... {error}")
#     else:
#         await interaction.response.send_message(embed=PERMISSION_NOT_FOUND_EMBED, ephemeral=True)
        
@bot.tree.command(description="Restarts bot (also updates)")
@app_commands.check(is_server_owner)
async def restartbot(ctx):
   await ctx.response.send_message("Updating/restarting bot!", ephemeral=True)
   channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
   await channel.send("Updating/restarting bot!")
   await run_blocking(restartpythonscript)
   

@restartbot.error
async def restartbot_error(interaction: discord.Interaction, error):
    if interaction.user.id == interaction.guild.owner_id:
        await interaction.edit_original_response(content=f"idk what went wrong... {error}")
    else:
        await interaction.response.send_message(embed=PERMISSION_NOT_FOUND_EMBED, ephemeral=True)
        

def getnewcsv():
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
        if os.path.exists(VARS_CSV_LOC):
            print("file removed")
            os.remove(VARS_CSV_LOC)
        conn.get(SFTP_CSV_LOC, localpath=VARS_CSV_LOC)
        print("new file got")
        read = []
        with open(VARS_CSV_LOC, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                read.append(line)
            print("read new file")
        with open(VARS_CSV_LOC, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([f"Data last updated {datetime.now().month}/{datetime.now().day}/{datetime.now().year} {datetime.now().hour}:{minutefix()} (MM/DD/YYYY HH:MM CST)"])
            writer.writerows(read)
            print('written')

@bot.tree.command(description="Gets the player with the topkdr")
async def topkdr(interaction: discord.Interaction):
    topkdrresponsetimestart = time.time()
    await interaction.response.send_message('Loading... (getting variables.csv)', ephemeral=True)
    getnewcsv()
    await interaction.edit_original_response(content=f"Loading... (finding topkdr)")
    topkdrname = ''

    for row in csv.reader(open(VARS_CSV_LOC)):
        rowstr = str(row)
        if not rowstr.find("topkdrname") == -1:
            for i in range(32,len(rowstr)-2):
                #print(rowstr[i])
                topkdrname = topkdrname+rowstr[i]
    topkdrnameencode = topkdrname.encode('utf-8')
    topkdrnamefinal = hex_to_ascii(decode_encoded_string(topkdrnameencode, 'utf-8'))
    await interaction.edit_original_response(content=f"Loading... (getting {topkdrnamefinal}'s data)")
    embedout= await getkdr_nonbot(topkdrnamefinal,interaction)
    topkdrresponsetimeend = time.time()-topkdrresponsetimestart
    await interaction.edit_original_response(content=f"Time taken ≈ {topkdrresponsetimeend} seconds",embed=embedout)

@bot.tree.command(description="Gets a player's kdr")
@app_commands.describe(player = "The player to check")
async def kdr(interaction: discord.Interaction, player: str):
    kdrresponsetimestart = time.time()
    await interaction.response.send_message('Loading... (getting variables.csv)', ephemeral=True)
    # try:
    #     conn = pysftp.Connection(host=host,port=port,username=username, password=password,cnopts=cnopts)
    #     CONNWORKED = True
    #     print("connection established successfully")
    # except: 
    #     CONNWORKED = False
    #     print('failed to establish connection to targeted server')
    # if CONNWORKED is True:
    #     current_dir = conn.pwd
    #     print('our current working directory is: ',current_dir)
    #     print('available list of directories: ',conn.listdir())
    #     if os.path.exists(VARS_CSV_LOC):
    #         print("file removed")
    #         os.remove(VARS_CSV_LOC)
    #     conn.get(SFTP_CSV_LOC, localpath=VARS_CSV_LOC)
    #     print("new file got")
    #     read = []
    #     with open(VARS_CSV_LOC, 'r') as f:
    #         reader = csv.reader(f)
    #         for line in reader:
    #             read.append(line)
    #         print("read new file")
    #     with open(VARS_CSV_LOC, 'w', newline='') as f:
    #         writer = csv.writer(f)
    #         writer.writerow([f"Data last updated {datetime.now().month}/{datetime.now().day}/{datetime.now().year} {datetime.now().hour}:{minutefix()} (MM/DD/YYYY HH:MM CST)"])
    #         writer.writerows(read)
    #         print('written')
    getnewcsv()

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


    file = open(VARS_CSV_LOC)
    type(file)
    csvreader = csv.reader(file)
    #print(header)
    for row in csv.reader(open(VARS_CSV_LOC)):
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
    for row in csv.reader(open(VARS_CSV_LOC)):
        rowstr = str(row)
        if not rowstr.find(f"kills::{playeruuid}") == -1:
            print(row)
            for i in range(59,75):
                killshex=killshex+rowstr[i]
    #print(playeruuid)
    kills=hexadecimal_to_decimal(killshex)
    print(kills)

    deathshex=""
    for row in csv.reader(open(VARS_CSV_LOC)):
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
    for row in csv.reader(open(VARS_CSV_LOC)):
        if gettimestampcurrentrow == 0:
            gettimestampcurrentrow = 1
            timestamp = row[0]
            print(row)


    topkdrname = ''

    for row in csv.reader(open(VARS_CSV_LOC)):
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





async def getkdr_nonbot(player: str,input_interaction: discord.Interaction):
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


    file = open(VARS_CSV_LOC)
    type(file)
    csvreader = csv.reader(file)
    #print(header)
    for row in csv.reader(open(VARS_CSV_LOC)):
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
    for row in csv.reader(open(VARS_CSV_LOC)):
        rowstr = str(row)
        if not rowstr.find(f"kills::{playeruuid}") == -1:
            print(row)
            for i in range(59,75):
                killshex=killshex+rowstr[i]
    #print(playeruuid)
    kills=hexadecimal_to_decimal(killshex)
    print(kills)

    deathshex=""
    for row in csv.reader(open(VARS_CSV_LOC)):
        rowstr = str(row)
        if not rowstr.find(f"deaths::{playeruuid}") == -1:
            print(row)
            for i in range(60,76):
                deathshex=deathshex+rowstr[i]
    #print(playeruuid)
    deaths=hexadecimal_to_decimal(deathshex)
    print(deaths)

    await input_interaction.edit_original_response(content=f"Loading... (Finalizing)")

    timestamp = ""
    gettimestampcurrentrow = 0
    for row in csv.reader(open(VARS_CSV_LOC)):
        if gettimestampcurrentrow == 0:
            gettimestampcurrentrow = 1
            timestamp = row[0]
            print(row)


    topkdrname = ''

    for row in csv.reader(open(VARS_CSV_LOC)):
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
    return KDR_EMBED





#pestbill water freezes
#leave messages dont show up for me (maybe donkey) in discordsrv

#topkdr npc sending kdr value

#example. /kdr a. someone with name starting with a might get selected instead of nobody. (presumably fixed)

#leaderboard

#more stuff in bot-console
#non case sensitive var
#/help

bot.run(BOT_TOKEN)
