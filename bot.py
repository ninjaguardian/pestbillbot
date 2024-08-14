#VERSION - 2.0.0.dev.7

# This work is licensed under CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/deed.en
# By ninjaguardian on GitHub

import logging
import traceback
# import asyncio

from github import Github
from github.ContentFile import ContentFile
from packaging.version import Version, parse
from sys import argv, executable

from os import path as os_path
from os import execv as os_execv
from os import remove as os_remove
from typing import Callable, Tuple, Any, NoReturn, Optional, IO, LiteralString, SupportsIndex
from pydantic import BaseModel
from re import compile as regex_compile
from requests import get as get_request
from pydantic_core._pydantic_core import ValidationError
from requests.exceptions import Timeout as RequestTimeoutError
from PIL._typing import StrOrBytesPath
from PIL import Image, ImageDraw

from time import time
from discord.ext import commands
from discord import app_commands
import discord
from discord.channel import VoiceChannel, StageChannel, TextChannel
from discord.threads import Thread
from datetime import datetime
from csv import reader as csv_reader
from csv import writer as csv_writer
import pysftp
from io import BytesIO
from aiohttp import ClientSession
from aiofiles import open as open_async
from functools import partial

# logging.basicConfig(level=logging.INFO, format='''[{asctime}] [{levelname:<8}] {name}: {message}''',datefmt='%Y-%m-%d %H:%M:%S',style='{')
logger = logging.getLogger()
filehandler = logging.FileHandler(filename=f'./bot_logs/discord_{datetime.now().strftime('%Y-%m-%d_%H.%M.%S')}.log', encoding='utf-8', mode='w')
filehandler.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
logger.addHandler(filehandler)
discord.utils.setup_logging()

_EVENT_IMAGE_LOC = './eventimage.png'
_VARS_CSV_LOC = './variables.csv'
_EVENT_COLOR_LOC = './eventembedcolor.txt'
_EVENT_LOC = './event.txt'
_DISCORD_BOT_TOKEN_LOC = './BOTTOKEN.txt'
_SFTP_PASS_LOC = './sftpPASS.txt'
_SFTP_USER_LOC = './sftpUSER.txt'
_SFTP_HOST_LOC = './sftpHOST.txt'
_SFTP_PORT_LOC = './sftpPORT.txt'
_GITHUB_TOKEN_LOC = './GITTOKEN.txt'
_SFTP_CSV_LOC = '/server/plugins/Skript/variables.csv'
_VER_OFFSET = 11
type _VERSION_PARSER = Callable[[str,int],Version]
type _ENCODING = str | None
type SENDABLE_CHANNEL = VoiceChannel | StageChannel | TextChannel  | Thread


#--------------------------------------------------------------------------------------------------
def get_file_version(version_line: str, OFFSET: int) -> Version:
    """
    Converts a string into a version.

    Args:
        version_line (str): The line the version is on.
        OFFSET (int): How many charecters before the version starts.

    Returns:
        Version: The converted version.
    """
    VERSION = ''
    for current_char in range(len(version_line)-OFFSET):
        VERSION += version_line[current_char+OFFSET]
    return parse(VERSION)

def get_current_file_version(OFFSET: int, encoding: _ENCODING = None, version_parser: _VERSION_PARSER = get_file_version) -> Version:
    """
    Gets the version from the current file.

    Args:
        OFFSET (int): The offset to pass to version_parser.
        encoding (_ENCODING, optional): The encoding the file uses. EXAMPLE: 'utf-8'. Defaults to None.
        version_parser (_VERSION_PARSER, optional): Turns the str into a Version. Defaults to get_file_version.
        debug (bool, optional): Enable debug outputs? Defaults to False.

    Returns:
        Version: The file version.
    """
    logger = logging.getLogger()
    with open(__file__, 'r', encoding=encoding) as f:
        current_line = f.readline().replace('\n','')
    current_version = version_parser(current_line, OFFSET)
    logger.debug("Current:", current_version)
    return current_version

def get_latest_file_contents(GIT_TOKEN_LOC: str, REPO_LOC: str, FILE_NAME: str, encoding: _ENCODING = None) -> bytes:
    """
    Gets the latest FILE_NAME from the repo REPO_LOC.

    Args:
        GIT_TOKEN_LOC (str): The path to the file that has the GitHub token.
        REPO_LOC (str): The repo where FILE_NAME is stored. EXAMPLE: 'ninjaguardian/pestbillbot'.
        FILE_NAME (str): The file name and extention of the file to get. EXAMPLE: 'bot.py'.
        encoding (_ENCODING, optional): The encoding the file uses. EXAMPLE: 'utf-8'. Defaults to None.

    Returns:
        bytes: The returned file.
    """
    with open(GIT_TOKEN_LOC, 'r', encoding=encoding) as f:
        g = Github(f.read())
    repo = g.get_repo(REPO_LOC)
    contents = repo.get_contents(FILE_NAME)
    assert isinstance(contents, ContentFile)
    return contents.decoded_content

def get_latest_file_version(bytes_file: bytes, OFFSET: int, version_parser: _VERSION_PARSER = get_file_version) -> Version:
    """
    Gets the lates file version from GitHub.

    Args:
        bytes_file (bytes): The file that has the version at the top.
        OFFSET (int): The offset to pass to version_parser
        version_parser (_VERSION_PARSER, optional): Turns the str into a Version. Defaults to get_file_version.
        debug (bool, optional): Enable debug outputs? Defaults to False.

    Returns:
        Version: The file version from GitHub.
    """
    logger = logging.getLogger()
    decoded_str = bytes_file.decode("UTF-8")
    decoded_firstline = decoded_str.splitlines()[0]
    latest_version = version_parser(decoded_firstline, OFFSET)
    logger.debug("GitHub:", latest_version)
    return latest_version

def restartpythonscript() -> NoReturn:
    """
    Restarts the python file. (WARNING: EXITS THE FILE)

    Args:
        debug (bool, optional): Enable debug outputs? Defaults to False.

    Returns:
        NoReturn: Uses sys_exit
    """
    logger = logging.getLogger()
    logger.debug("argv was",argv)
    logger.debug(f"sys.executable was {executable}")
    logger.info("Shutting down by restart")
    os_execv(__file__, argv)
    # call_subprocess(["python", os_path.join(sys.path[0], __file__)] + argv[1:])
    # sys.exit(f"New version ran ({_latest_version})")

def update_and_restart(GIT_TOKEN_LOC: str, REPO_LOC: str, FILE_NAME: str, OFFSET: int, encoding: _ENCODING, current_version_retriever: Callable[[int, _ENCODING, _VERSION_PARSER], Version] = get_current_file_version, latest_version_retriever: Callable[[bytes, int, _VERSION_PARSER], Version] = get_latest_file_version, latest_content_retriever: Callable[[str, str, str, _ENCODING], bytes] = get_latest_file_contents, version_parser: _VERSION_PARSER = get_file_version) -> Tuple[Version,Version] | NoReturn:
    logger = logging.getLogger()
    current_version = current_version_retriever(OFFSET, encoding, version_parser) #Local
    latest_content = latest_content_retriever(GIT_TOKEN_LOC, REPO_LOC, FILE_NAME, encoding)
    latest_version = latest_version_retriever(latest_content, OFFSET, version_parser) #GitHub
    if latest_version>current_version:
        logger.debug(f"Downloading.... (Found: {latest_version})")
        with open(__file__, 'wb') as f:
            f.write(latest_content)
        logger.debug(f"Downloaded and restarting. {latest_version}>{current_version}")
        restartpythonscript()
    elif current_version>=latest_version:
        logger.debug(f"No new version found ||GitHub: {latest_version}   Current: {current_version}||")
        return (current_version,latest_version)
    else:
        raise ValueError("Error getting version")

#--------------------------------------------------------------------------------------------------
with open(_SFTP_HOST_LOC, 'r') as f:
    _SFTP_HOST = f.read()
with open(_SFTP_PORT_LOC, 'r') as f:
    _SFTP_PORT = int(f.read())
with open(_SFTP_USER_LOC, 'r') as f:
    _SFTP_USERNAME = f.read()
with open(_SFTP_PASS_LOC, 'r') as f:
    _SFTP_PASSWORD = f.read()

_CnOpts = pysftp.CnOpts('') #WARNING:All hosts are considered 'safe'
_CnOpts.hostkeys = None

with open(_DISCORD_BOT_TOKEN_LOC, 'r') as f:
    BOT_TOKEN = f.read()

class Bot(commands.Bot):
    async def async_cleanup(self, alert_channel: SENDABLE_CHANNEL | None = None) -> None:
        logger = logging.getLogger()
        if alert_channel is not None:
            await alert_channel.send("Shutting down bot!")
        logger.info('Shutting down bot!')
    async def close(self, alert_channel: SENDABLE_CHANNEL | None = None) -> None:
        await self.async_cleanup(alert_channel)
        return await super().close()
    def setup_channels(self):
        self.channels = self._channels()

    class _channels:
        def __init__(self) -> None:
            self._channel_ids: dict[str,int] = {}
        def __getattribute__(self, name: str) -> Any:
            if name == '_channel_ids':
                raise AttributeError("To get _channel_ids, run get_channel_id_dict().")
            else:
                return super().__getattribute__(name)
        def get_channel_id(self, nickname: str) -> int | None:
            if self.if_nickname_exists(nickname):
                return self._channel_ids[nickname]
            return None
        def save_channel_id(self, nickname: str, id: int) -> None:
            self._channel_ids[nickname] = id
        def get_channel_id_dict(self) -> dict[str,int]:
            return self._channel_ids
        def if_id_exists(self, id: int) -> bool:
            return id in self._channel_ids.values()
        def if_nickname_exists(self, nickname: str) -> bool:
            return nickname in self._channel_ids.keys()

bot = Bot(command_prefix="!", intents=discord.Intents.all())

_PERMISSION_NOT_FOUND_EMBED = discord.Embed()
_PERMISSION_NOT_FOUND_EMBED.add_field(name="**HEY!**",value=str("""```ansi
[2;31m[2;31mYou do not have permission to do that![0m[2;31m[0m
```"""))


def decimal_to_hexadecimal(decimal_num: int) -> str:
    return hex(decimal_num)

def hexadecimal_to_decimal(hexadecimal_str: str) -> int:
    return int(hexadecimal_str, 16)

def hex_to_ascii(hex_string: str) -> str:
    return bytes.fromhex(hex_string).decode('ascii')

def ascii_to_hex(ascii_string: str) -> str:
    return ascii_string.encode().hex().upper()

def is_server_owner(interaction: discord.Interaction) -> bool:
    if interaction.guild is not None:
        if interaction.user.id == interaction.guild.owner_id:
            return True
    return False

def generate_username_regex(username: str) -> str:
    hex_pattern_parts = []
    for char in username:
        if char.isalpha():
            hex_upper = ascii_to_hex(char.upper()).upper().zfill(2)
            hex_lower = ascii_to_hex(char.lower()).upper().zfill(2)
            hex_pattern_parts.append(f'({hex_upper}|{hex_lower})')
        else:
            hex_pattern_parts.append(f'{ascii_to_hex(char)}')
    hex_pattern = ''.join(hex_pattern_parts)
    return f'^ ....{hex_pattern}$'

def get_uuid_manual(player: str) -> str | None:
    pattern = regex_compile(generate_username_regex(player))
    playeruuid = None

    with open('./variables.csv') as file:
        csvreader = csv_reader(file)
        for row in csvreader:
            try:
                if not row[0].find("kdr::uuidname") == -1: # if the row contains the uuid and playerhex
                    if pattern.fullmatch(row[2]): # if the player's hex is in the string
                        playeruuid = row[0][13:] # grab the uuid
            except IndexError:
                pass # ignore things with no index
    return playeruuid

def uuid_to_name_manual(uuid: str) -> str | None:
    with open('./variables.csv') as file:
        csvreader = csv_reader(file)
        for row in csvreader:
            try:
                if row[0] == f"kdr::uuidname{uuid}": # if the row contains the uuid and playerhex
                    return hex_to_ascii(row[2][5:])
            except IndexError:
                pass # ignore things with no index
    return None

class BedrockApiResponse(BaseModel):
    gamertag: str
    xuid: str
    floodgateuid: str
    icon: str
    gamescore: str
    accounttier: str
    textureid: Optional[str] = None
    skin: Optional[str]
    linked: bool
    java_uuid: Optional[str] = None
    java_name: Optional[str] = None

class JavaApiResponse(BaseModel):
    username: str
    uuid: str
    skin: str
    cape: Optional[str]
    linked: bool
    bedrock_gamertag: Optional[str] = None
    bedrock_xuid: Optional[int] = None
    bedrock_fuid: Optional[str] = None

def get_data_api(player: str) -> BedrockApiResponse | JavaApiResponse | RequestTimeoutError | ValidationError:
    with open('./mcprofilekey.txt') as file:
        API_KEY = file.read()
    bedrock = player[0] == '.'
    data: JavaApiResponse | BedrockApiResponse
    try:
        if bedrock:
            response = get_request(f'https://mcprofile.io/api/v1/bedrock/gamertag/{player[1:]}', headers={'x-api-key':API_KEY}, timeout=20)
            bedrock_contents: dict[str,str|bool] = response.json()
            data = BedrockApiResponse.model_validate(bedrock_contents)
        else:
            response = get_request(f'https://mcprofile.io/api/v1/java/username/{player}', headers={'x-api-key':API_KEY}, timeout=20)
            java_contents: dict[str,str|bool|int] = response.json()
            data = JavaApiResponse.model_validate(java_contents)
    except RequestTimeoutError as eTimeoutError:
        return eTimeoutError
    except ValidationError as eValidationError:
        return eValidationError
    return data

def minutefix() -> str:
    if len(str(datetime.now().minute)) == 1:
        return "0"+str(datetime.now().minute)
    else:
        return str(datetime.now().minute)

async def run_blocking(blocking_func: Callable, bot: commands.Bot) -> Any: #TODO: should it not be any?
    """Runs a blocking function in a non-blocking way"""
    func = partial(blocking_func) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)


def getnewcsv(SFTP_HOST: str, SFTP_PORT: int, SFTP_USERNAME: str, SFTP_PASSWORD: str, CnOpts: pysftp.CnOpts, VARS_CSV_LOC: str, SFTP_CSV_LOC: str, debug: bool = False) -> None:
    try:
        with pysftp.Connection(host=SFTP_HOST,port=SFTP_PORT,username=SFTP_USERNAME, password=SFTP_PASSWORD,cnopts=CnOpts) as conn:
            if debug:
                print("connection established successfully")
                current_dir = conn.pwd
                print('our current working directory is: ',current_dir)
                print('available list of directories: ',conn.listdir())
            if os_path.exists(VARS_CSV_LOC):
                if debug:
                    print("file removed")
                os_remove(VARS_CSV_LOC)
            conn.get(SFTP_CSV_LOC, localpath=VARS_CSV_LOC)
            if debug:
                print("new file got")
            read = []
            with open(VARS_CSV_LOC, 'r') as f:
                reader = csv_reader(f)
                for line in reader:
                    read.append(line)
                if debug:
                    print("read new file")
            with open(VARS_CSV_LOC, 'w', newline='') as f:
                writer = csv_writer(f)
                writer.writerow([f"Data last updated {datetime.now().month}/{datetime.now().day}/{datetime.now().year} {datetime.now().hour}:{minutefix()} (MM/DD/YYYY HH:MM CST)"])
                writer.writerows(read)
                if debug:
                    print('written')
    except (pysftp.AuthenticationException, pysftp.ConnectionException):
        if debug:
            print('failed to establish connection to targeted server')

def split_without_remove(string: LiteralString | str, sep: LiteralString | str | None = None, maxsplit: SupportsIndex = -1, beforesplit: bool = True) -> list[LiteralString | str]: #FIXME: sometimes it outputs an empty string at the end. should it?
    split_string = string.split(sep=sep,maxsplit=maxsplit) #TODO: add rsplit version
    for loop_idx,_ in enumerate(split_string):
        if not loop_idx == len(split_string)-1:
            if sep is None:
                raise NotImplementedError("I was to lazy. Thy must set sep.") #TODO: Code this
            else:
                if beforesplit:
                    split_string[loop_idx] += sep
                else:
                    split_string[loop_idx+1] = sep + split_string[loop_idx+1]
    return split_string

class Overlay:
    NONE = 0
    HEAD = 1
    BODY = 2
    BOTH = 3

def get_head(img_path: StrOrBytesPath | IO[bytes], show_body: bool = True, overlay: int = Overlay.BOTH) -> Image.Image:
    if not overlay == Overlay.NONE and not overlay == Overlay.HEAD and not overlay == Overlay.BODY and not overlay == Overlay.BOTH:
        raise ValueError("Overlay must be one of: Overlay.NONE, Overlay.HEAD, Overlay.BODY, Overlay.BOTH")
    with Image.open(img_path) as image:
        cropped_image = image.crop((8, 8, 16, 16)) # get the head
        if overlay == Overlay.HEAD or overlay == Overlay.BOTH:
            region = image.crop((40, 8, 48, 16)) # get the overlay
            cropped_image.paste(region, (0,0), region) # combine jead and overlay

        cropped_image = cropped_image.resize((60, 60), Image.Resampling.NEAREST)  # Resize to 60x60

        if show_body:
            draw = ImageDraw.Draw(cropped_image) # initialize drawing

            body_type_pixel = image.getpixel((43,48)) # Get a pixel that will have alpha channel == 0 when slim
            assert isinstance(body_type_pixel,tuple) # make sure getpixel outputs a tuple

            if body_type_pixel[3] == 0: #NOTE: SLIM (ALEX)
                draw.rectangle([46, 25, 55, 58], outline="white", fill="white")
                draw.rectangle([43, 33, 58, 46], outline="white", fill="white")

                regions = [
                    ((8, 8, 16, 16), (47, 26)), #NOTE: head
                    ((40, 8, 48, 16), (47, 26)), #NOTE: head overlay
                    ((20, 20, 28, 32), (47, 34)), #NOTE: torso
                    ((20, 36, 28, 48), (47, 34)), #NOTE: torso overlay
                    ((44, 20, 47, 32), (44, 34)), #NOTE: left arm
                    ((44, 36, 47, 48), (44, 34)), #NOTE: left arm overlay
                    ((36, 52, 39, 64), (55, 34)), #NOTE: right arm
                    ((52, 52, 55, 64), (55, 34)), #NOTE: right arm overlay
                    ((20, 52, 24, 64), (51, 46)), #NOTE: right leg
                    ((4, 52, 8, 64), (51, 46)), #NOTE: right leg overlay
                    ((4, 20, 8, 32), (47, 46)), #NOTE: left leg
                    ((4, 36, 8, 48), (47, 46)) #NOTE: left leg overlay
                ]

            else: #NOTE: THICK (STEVE)
                draw.rectangle([45, 25, 54, 58], outline="white", fill="white")
                draw.rectangle([41, 33, 58, 46], outline="white", fill="white")

                regions = [
                    ((8, 8, 16, 16), (46, 26)), #NOTE: head
                    ((40, 8, 48, 16), (46, 26)), #NOTE: head overlay
                    ((20, 20, 28, 32), (46, 34)), #NOTE: torso
                    ((20, 36, 28, 48), (46, 34)), #NOTE: torso overlay
                    ((44, 20, 48, 32), (42, 34)), #NOTE: left arm
                    ((44, 36, 48, 48), (42, 34)), #NOTE: left arm overlay
                    ((36, 52, 40, 64), (54, 34)), #NOTE: right arm
                    ((52, 52, 56, 64), (54, 34)), #NOTE: right arm overlay
                    ((20, 52, 24, 64), (50, 46)), #NOTE: right leg
                    ((4, 52, 8, 64), (50, 46)), #NOTE: right leg overlay
                    ((4, 20, 8, 32), (46, 46)), #NOTE: left leg
                    ((4, 36, 8, 48), (46, 46)) #NOTE: left leg overlay
                ]

            for idx, (original_box, new_pos) in enumerate(regions):
                if overlay == Overlay.BODY or overlay == Overlay.BOTH:
                    region = image.crop(original_box)
                    cropped_image.paste(region, new_pos, region)
                else:
                    if idx % 2 == 0:
                        region = image.crop(original_box)
                        cropped_image.paste(region, new_pos, region)

    return cropped_image

def fetch_pronouns(uuid: str) -> list[str]:
    try:
        request = get_request(f'https://pronoundb.org/api/v2/lookup?platform=minecraft&ids={uuid}',timeout=20)
        data: list[str] = request.json()[uuid]['sets']['en']
        return data
    except RequestTimeoutError:
        return []

class ParsedPronoun(BaseModel):
    subjective: str
    objective: str
    possessive: str

def parse_pronoun(pronoun: str) -> ParsedPronoun:
    if pronoun == 'he':
        return ParsedPronoun.model_validate({'subjective':'he','objective':'him','possessive':'his'})
    elif pronoun == 'it':
        return ParsedPronoun.model_validate({'subjective':'it','objective':'it','possessive':'its'})
    elif pronoun == 'she':
        return ParsedPronoun.model_validate({'subjective':'she','objective':'her','possessive':'hers'})
    elif pronoun == 'they':
        return ParsedPronoun.model_validate({'subjective':'they','objective':'them','possessive':'theirs'})
    else:
        return ParsedPronoun.model_validate({'subjective': pronoun,'objective': pronoun,'possessive': pronoun})


class ExplainErrorButton(discord.ui.View):
    def __init__(self, stacktrace_list: list[str], *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.stacktrace_list = stacktrace_list

    @discord.ui.button(label='Send Stacktrace', style=discord.ButtonStyle.blurple)
    async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for idx, loop_stacktrace in enumerate(self.stacktrace_list):
            button_message = f'''# Stacktrace p{idx+1}\n```py
{loop_stacktrace}
```'''
            if idx == 0:
                await interaction.response.send_message(button_message)
            else:
                await interaction.followup.send(button_message)

    @discord.ui.button(label='Send Stacktrace Embed', style=discord.ButtonStyle.green)
    async def button_embed(self, interaction: discord.Interaction, button: discord.ui.Button): #TODO: combine if < 1000
        EMBED=discord.Embed(title="Stacktrace", color=int('0a63f2', 16))
        for idx, loop_stacktrace in enumerate(self.stacktrace_list):
            if len(loop_stacktrace) > 1000:
                raise NotImplementedError #TODO: NotImplementedError stacktrace>1000
            else:
                EMBED.add_field(value=f'''```py
{loop_stacktrace}
```''', name=f"Stacktrace p{idx+1}", inline=False)
        await interaction.response.send_message(embed=EMBED)

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.errors.AppCommandError, /) -> None:
    global bot
    global MOD_ONLY_CHANNEL_ID
    logger = logging.getLogger()
    logger.error(f'''\x1b[31;1mCommand error\x1b[0m
\x1b[35m--------------------------------\x1b[34m
user: <@{interaction.user.id}> ({interaction.user})
namespace: {interaction.namespace}
type: {interaction.type}{'\nmessage: '+str(interaction.message) if interaction.type == discord.InteractionType.component else ''}
data:
{interaction.data}
\x1b[35m--------------------------------
\x1b[31m'''+traceback.format_exc()+'\x1b[0m')



    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    assert not isinstance(channel,discord.abc.PrivateChannel)
    assert not isinstance(channel,discord.ForumChannel)
    assert not isinstance(channel,discord.CategoryChannel)
    assert channel is not None

    KDR_EMBED_ALERT=discord.Embed(title="Someone had an error!!", color=int('fa2d1e', 16))
    KDR_EMBED_ALERT.add_field(value=f'''
user: <@{interaction.user.id}> ({interaction.user})
namespace: {interaction.namespace}
interaction type: {interaction.type}{'\nmessage: '+str(interaction.message) if interaction.type == discord.InteractionType.component else ''}
''', name="Helful info", inline=False)
    KDR_EMBED_ALERT.add_field(value=f'''
```py
{interaction.data}
```
''', name="Data", inline=False)
    error_stacktrace = traceback.format_exc().replace(r'C:\Users\carte','[user]') #TODO: change to regex
    stacktrace_list = split_without_remove(error_stacktrace,'Traceback (most recent call last):',beforesplit=False)[1:]
    await channel.send(content="",embed=KDR_EMBED_ALERT, view=ExplainErrorButton(stacktrace_list))

#Boot message
@bot.event
async def on_ready() -> None:
    global MOD_ONLY_CHANNEL_ID
    global _current_version
    global bot

    bot.setup_channels()
    print(f"Bot is ready ({_current_version})")
    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    assert not isinstance(channel,discord.abc.PrivateChannel)
    assert not isinstance(channel,discord.ForumChannel)
    assert not isinstance(channel,discord.CategoryChannel)
    assert channel is not None
    await channel.send(f"Bot is ready ({_current_version})")
    await channel.send(f"Online version ({_latest_version})")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        await channel.send(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(str(e))
        await channel.send(str(e))

#off message
@bot.event
async def on_disconnect() -> None:
    print("Turning bot off...")

@bot.tree.command(description="Shows the bot latency")
async def ping(ctx: discord.interactions.Interaction) -> None:
    global bot
    global _latest_version
    global _current_version
    SET_PING_EMBED=discord.Embed(title="Ping", color=int('1e63d4', 16))
    if is_server_owner(ctx):
        SET_PING_EMBED.add_field(name="",value=f'''The bot's ping is: {bot.latency}ms
The bot is running v{_current_version}
The GitHub shows v{_latest_version}''',inline=False)
    else:
        SET_PING_EMBED.add_field(name="",value=f'''The bot's ping is: {bot.latency}ms''',inline=False)
    await ctx.response.send_message(embed=SET_PING_EMBED, ephemeral=True)

@bot.tree.command(description="Gets the current pestbill event")
async def event(ctx: discord.interactions.Interaction) -> None:
    global _EVENT_IMAGE_LOC
    global _EVENT_COLOR_LOC
    global _EVENT_LOC
    file = discord.File(_EVENT_IMAGE_LOC, filename='eventimage.png')
    with open(_EVENT_COLOR_LOC, 'r') as f:
        EVENT_EMBED=discord.Embed(title="Event", color=int(f.read()))
    with open(_EVENT_LOC, 'r') as f:
        EVENT_EMBED.add_field(name="",value=f"The current event is **{f.read()}**!", inline=False)
    EVENT_EMBED.set_thumbnail(url="attachment://eventimage.png")

    await ctx.response.send_message(file=file, embed=EVENT_EMBED, ephemeral=True)


@bot.tree.command(description="Sets the current event")
@app_commands.describe(event = "Set the current event", hexcolor = "Color of embed sidebar as a hex color", imageurl = "URL of the image displayed")
@app_commands.check(is_server_owner)
async def setevent(ctx: discord.interactions.Interaction, event: str|None=None, hexcolor: str|None=None, imageurl: str|None=None) -> None:
    global _EVENT_IMAGE_LOC
    global _EVENT_LOC
    global _EVENT_COLOR_LOC
    if imageurl is None:
        file = discord.File(_EVENT_IMAGE_LOC, filename='eventimage.png')
    else:
        async with ClientSession() as session:
            async with session.get(imageurl) as resp:
                if resp.status != 200:
                    await ctx.response.send_message("Could not download file!", ephemeral=True)
                eventimgfiledata = BytesIO(await resp.read())
                file = discord.File(eventimgfiledata, 'eventimage.png')
                async with open_async(_EVENT_IMAGE_LOC, mode='wb') as tempf:
                    timed = await resp.read()
                    await tempf.write(timed)
    if event is None:
        with open(_EVENT_LOC, 'r') as f:
            event = f.read()
    if hexcolor is None:
        with open(_EVENT_COLOR_LOC, 'r') as f:
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
    with open(_EVENT_LOC, 'w') as f:
        f.write(f'{event}')
    with open(_EVENT_COLOR_LOC, 'w') as f:
        f.write(f'{int(hexcolor, 16) }')


@setevent.error
async def setevent_error(interaction: discord.Interaction, error: app_commands.errors.AppCommandError) -> None:
    global _PERMISSION_NOT_FOUND_EMBED
    if is_server_owner(interaction):
        await interaction.response.send_message(f"Don't add a #, add one of the https:// things. Check logs for more info. | {error}", ephemeral=True)
    else:
        await interaction.response.send_message(embed=_PERMISSION_NOT_FOUND_EMBED, ephemeral=True)

@bot.tree.command(description="Turns bot off")
@app_commands.check(is_server_owner)
async def shutdown(ctx: discord.interactions.Interaction) -> None:
    global MOD_ONLY_CHANNEL_ID
    global bot
    global logger
    await ctx.response.send_message("Bot is being shut down...", ephemeral=True)
    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    assert not isinstance(channel,discord.abc.PrivateChannel)
    assert not isinstance(channel,discord.ForumChannel)
    assert not isinstance(channel,discord.CategoryChannel)
    assert channel is not None
    await channel.send("Recived shutdown command!")
    logger.info("Recived shutdown command")
    await bot.close()

@shutdown.error
async def shutdown_error(interaction: discord.Interaction, error: app_commands.errors.AppCommandError) -> None:
    global _PERMISSION_NOT_FOUND_EMBED
    if is_server_owner(interaction):
        await interaction.response.send_message(f"idk what went wrong... Check logs for more info. {error}", ephemeral=True)
    else:
        await interaction.response.send_message(embed=_PERMISSION_NOT_FOUND_EMBED, ephemeral=True)


@bot.tree.command(description="Restarts bot (also updates)")
@app_commands.check(is_server_owner)
async def restartbot(ctx: discord.interactions.Interaction) -> NoReturn:
    global MOD_ONLY_CHANNEL_ID
    global bot
    global logger
    global _latest_version
    await ctx.response.send_message(f"Recived restart command. Running {_latest_version}", ephemeral=True)
    channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    assert not isinstance(channel,discord.abc.PrivateChannel)
    assert not isinstance(channel,discord.ForumChannel)
    assert not isinstance(channel,discord.CategoryChannel)
    assert channel is not None
    await channel.send(f"Recived restart command. Running {_latest_version}")
    logger.info(f"Recived restart command. Running {_latest_version}")
    await bot.close()
    restartpythonscript()

@restartbot.error
async def restartbot_error(interaction: discord.Interaction, error: app_commands.errors.AppCommandError) -> None:
    global _PERMISSION_NOT_FOUND_EMBED
    if is_server_owner(interaction):
        await interaction.edit_original_response(content=f"idk what went wrong... Check logs for more info. {error}")
    else:
        await interaction.response.send_message(embed=_PERMISSION_NOT_FOUND_EMBED, ephemeral=True)

@bot.tree.command(description="Gets the player with the topkdr")
async def topkdr(interaction: discord.Interaction) -> None:
    global _SFTP_HOST,_SFTP_PORT,_SFTP_USERNAME,_SFTP_PASSWORD,_CnOpts,_VARS_CSV_LOC,_SFTP_CSV_LOC
    topkdrresponsetimestart = time()
    await interaction.response.send_message('Loading... (getting variables.csv)', ephemeral=True)
    getnewcsv(_SFTP_HOST,_SFTP_PORT,_SFTP_USERNAME,_SFTP_PASSWORD,_CnOpts,_VARS_CSV_LOC,_SFTP_CSV_LOC)
    await interaction.edit_original_response(content="Loading... (finding topkdr)")
    topkdrname = ''

    with open(_VARS_CSV_LOC) as file:
        for row in csv_reader(file):
            try:
                if row[0] == "topkdrname":
                        topkdrname = hex_to_ascii(row[2][5:])
            except IndexError:
                pass # ignore things with no index
    await interaction.edit_original_response(content=f"Loading... (getting {topkdrname}'s data)")
    await getkdr_nonbot(topkdrname,interaction,topkdrresponsetimestart)

@bot.tree.command(description="Gets a player's kdr")
@app_commands.describe(player = "The player to check")
async def kdr(interaction: discord.Interaction, player: str) -> None:
    await interaction.response.send_message('Loading... (starting up)', ephemeral=True)
    await getkdr_nonbot(player,interaction,time())

@kdr.error
async def kdr_error(interaction: discord.Interaction, error: app_commands.errors.AppCommandError) -> None:
    global bot
    global MOD_ONLY_CHANNEL_ID
#     global logger

#     logger.error(f'''\x1b[31;1mKDR error\x1b[0m
# \x1b[35m--------------------------------\x1b[34m
# user: <@{interaction.user.id}> ({interaction.user})
# namespace: {interaction.namespace}
# interaction type: {interaction.type}{'\nmessage: '+str(interaction.message) if interaction.type == discord.InteractionType.component else ''}
# data:
# {interaction.data}
# \x1b[35m--------------------------------
# \x1b[31m'''+traceback.format_exc()+'\x1b[0m')

    # if is_server_owner(interaction):
    #     await interaction.edit_original_response(content=f"Hello owner! This is the error: {error}")
    # else:
    KDR_EMBED_ERROR=discord.Embed(title="ERROR WHILE FETCHING KDR!", color=int('fa2d1e', 16))
    KDR_EMBED_ERROR.add_field(value='''> The player's name may violate naming rules.
> The player may have had their stats wiped due to them being low.
> The player may have not joined the game before.
> There may have been some bug that occured.
> Report the bug in <#1170117676518101013>
> DM <@733487800124571679> for more help!''', name="Common mistakes", inline=False)


    # channel = bot.get_channel(MOD_ONLY_CHANNEL_ID)
    # assert not isinstance(channel,discord.abc.PrivateChannel)
    # assert not isinstance(channel,discord.ForumChannel)
    # assert not isinstance(channel,discord.CategoryChannel)
    # assert channel is not None

    # KDR_EMBED_ALERT=discord.Embed(title="Someone had a kdr error!!", color=int('fa2d1e', 16))
    # KDR_EMBED_ALERT.add_field(value=f'''
# user: <@{interaction.user.id}> ({interaction.user})
# namespace: {interaction.namespace}
# interaction type: {interaction.type}{'\nmessage: '+str(interaction.message) if interaction.type == discord.InteractionType.component else ''}
# ''', name="Helful info", inline=False)
    # KDR_EMBED_ALERT.add_field(value=f'''
# ```py
# {interaction.data}
# ```
# ''', name="Data", inline=False)
    # error_stacktrace = traceback.format_exc().replace(r'C:\Users\carte','[user]') #FIXME: change to regex
    # stacktrace_list = split_without_remove(error_stacktrace,'Traceback (most recent call last):',beforesplit=False)[1:]
    # await channel.send(content="",embed=KDR_EMBED_ALERT, view=ExplainErrorButton(stacktrace_list))
    await interaction.edit_original_response(content="",embed=KDR_EMBED_ERROR)




async def getkdr_nonbot(player: str, interaction: discord.Interaction, kdrresponsetimestart: float) -> None: #WARNING:may not work with names that have spaces
    global _SFTP_HOST,_SFTP_PORT,_SFTP_USERNAME,_SFTP_PASSWORD,_CnOpts,_VARS_CSV_LOC,_SFTP_CSV_LOC,JavaApiResponse,BedrockApiResponse
    await interaction.edit_original_response(content='Loading... (getting variables.csv)')
    getnewcsv(_SFTP_HOST,_SFTP_PORT,_SFTP_USERNAME,_SFTP_PASSWORD,_CnOpts,_VARS_CSV_LOC,_SFTP_CSV_LOC)
    await interaction.edit_original_response(content=f"Loading... (getting {player}'s data)")
    player_data = get_data_api(player)
    if isinstance(player_data,JavaApiResponse): #This and the next few lines parse the player_data or do it manualy if needed
        player_uuid = player_data.uuid
        player_skin: str | None = player_data.skin
        player_spelled = player_data.username
    elif isinstance(player_data,BedrockApiResponse):
        player_uuid = player_data.floodgateuid
        player_skin = player_data.skin
        player_spelled = player_data.gamertag
    elif isinstance(player_data,RequestTimeoutError):
        await interaction.edit_original_response(content="Loading... (Error: Can't access API. Falling back to manual.)")
        manual_uuid = get_uuid_manual(player)
        if manual_uuid is None:
            raise NotImplementedError("Player is not registered") #FIXME: NotImplementedError("Player is not registered")
        else:
            player_uuid = manual_uuid
            player_skin = None
            temp_name = uuid_to_name_manual(player_uuid)
            if temp_name is None:
                player_spelled = player
            else:
                player_spelled = temp_name
    elif isinstance(player_data,ValidationError):
        raise NotImplementedError("Player does not exist") #FIXME: NotImplementedError("Player does not exist")
    else:
        raise ValueError("player_data uknown type")

    await interaction.edit_original_response(content="Loading... (Parsing data)")

    timestamp = ''
    kills = 0
    deaths = 1
    topkdrname = ''
    player_exists = False

    with open(_VARS_CSV_LOC) as file:
        for idx,row in enumerate(csv_reader(file)):
            try:
                if idx == 0:
                    timestamp = row[0]
                if row[0] == f"kills::{player_uuid}":
                    kills=hexadecimal_to_decimal(row[2])
                    player_exists = True
                if row[0] == f"deaths::{player_uuid}":
                    deaths=hexadecimal_to_decimal(row[2])
                    player_exists = True
                if row[0] == "topkdrname":
                    topkdrname=hex_to_ascii(row[2][5:])
            except IndexError:
                pass # ignore things with no index

    await interaction.edit_original_response(content="Loading... (Finalizing)")

    if player_exists:

        if player_skin is None:
            head_img: str | Image.Image = f'https://mc-heads.net/combo/{player}'
            attachment_file = None
        else:
            try:
                response = get_request(player_skin,timeout=20)
                head_img = get_head(BytesIO(response.content))
                head_img.save('./head.png')
                attachment_file = discord.File('./head.png')
            except RequestTimeoutError:
                head_img = f'https://mc-heads.net/combo/{player}'
                attachment_file = None

        if topkdrname.lower() == player.lower():
            await interaction.edit_original_response(content="Loading... (Getting pronouns)")
            KDR_EMBED=discord.Embed(title=f"{player_spelled}'s KDR", color=int('e0bd00', 16))
            pronouns = fetch_pronouns(player_uuid)
            if len(pronouns) == 0:
                pronouns = ['they']
            match pronouns[0]:
                case 'he':
                    subjective_pronoun = parse_pronoun(pronouns[0]).subjective.capitalize()
                    has_or_have = 'has'
                case 'it':
                    subjective_pronoun = parse_pronoun(pronouns[0]).subjective.capitalize()
                    has_or_have = 'has'
                case 'she':
                    subjective_pronoun = parse_pronoun(pronouns[0]).subjective.capitalize()
                    has_or_have = 'has'
                case 'avoid':
                    subjective_pronoun = player_spelled
                    has_or_have = 'has'
                case 'they':
                    subjective_pronoun = parse_pronoun(pronouns[0]).subjective.capitalize()
                    has_or_have = 'have'
                case _:
                    match pronouns[1]:
                        case 'he':
                            subjective_pronoun = parse_pronoun(pronouns[1]).subjective.capitalize()
                            has_or_have = 'has'
                        case 'it':
                            subjective_pronoun = parse_pronoun(pronouns[1]).subjective.capitalize()
                            has_or_have = 'has'
                        case 'she':
                            subjective_pronoun = parse_pronoun(pronouns[1]).subjective.capitalize()
                            has_or_have = 'has'
                        case 'avoid':
                            subjective_pronoun = player_spelled
                            has_or_have = 'has'
                        case _:
                            subjective_pronoun = parse_pronoun('they').subjective.capitalize()
                            has_or_have = 'have'

            KDR_EMBED.add_field(value=f'''{player_spelled}'s KDR is {round(kills/deaths,2)}!
{subjective_pronoun} also {has_or_have} the **top kdr**!''', name="KDR", inline=False)
        else:
            KDR_EMBED=discord.Embed(title=f"{player_spelled}'s KDR", color=int('fa2d1e', 16))
            KDR_EMBED.add_field(value=f"{player_spelled}'s KDR is {round(kills/deaths,2)}!", name="KDR", inline=False)
        await interaction.edit_original_response(content="Loading... (Sending)")
        KDR_EMBED.add_field(value=f"{player_spelled}'s has {kills} kills!", name="Kills", inline=False)
        KDR_EMBED.add_field(value=f'''{player_spelled}'s has {deaths} deaths!''', name="Deaths", inline=False)
        KDR_EMBED.set_thumbnail(url='attachment://head.png')
        KDR_EMBED.set_footer(text=f'''{timestamp}
Even if the stats file was recently downloaded, new stats are only added after a restart.''')
        kdrresponsetimeend = time()
        kdrresponsetime = kdrresponsetimeend-kdrresponsetimestart
        if attachment_file is None:
            await interaction.edit_original_response(content=f"Time taken ≈ {kdrresponsetime} seconds",embed=KDR_EMBED)
        else:
            await interaction.edit_original_response(content=f"Time taken ≈ {kdrresponsetime} seconds",embed=KDR_EMBED,attachments=[attachment_file])
    else:
        KDR_EMBED_ERROR=discord.Embed(title="ERROR WHILE FETCHING KDR!", color=int('fa2d1e', 16))
        KDR_EMBED_ERROR.add_field(value='''> The player's name may violate naming rules.
> The player may have had their stats wiped due to them being low.
> The player may have not joined the game before.
> There may have been some bug that occured.
> Report the bug in <#1170117676518101013>
> DM <@733487800124571679> for more help!''', name="Common mistakes", inline=False)
        KDR_EMBED_ERROR.set_footer(text=f'''{timestamp}
Even if the stats file was recently downloaded, new stats are only added after a restart.''')
        kdrresponsetimeend = time()
        kdrresponsetime = kdrresponsetimeend-kdrresponsetimestart
        await interaction.edit_original_response(content=f"Time taken ≈ {kdrresponsetime} seconds",embed=KDR_EMBED_ERROR)




if __name__ == "__main__":
    _current_version, _latest_version = update_and_restart(_GITHUB_TOKEN_LOC,"ninjaguardian/pestbillbot",'bot.py',_VER_OFFSET,'utf-8')


    CHANNEL_ID = 1139304414885183658
    MOD_ONLY_CHANNEL_ID = 1182685204775714887
    BYPASS_ROLE = 1139294768090853536
    PESTBILL_ID = 1139292425353973790

    bot.run(BOT_TOKEN,log_handler=None)

#FIXME: paramiko.transport Authentication (password) failed. occurs in all http requests
