import csv
import re

def hex_to_ascii(hex_string: str) -> str:
    return bytes.fromhex(hex_string).decode('ascii')

def ascii_to_hex(ascii_string: str) -> str:
    return ascii_string.encode().hex().upper()

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

def get_uuid_manual(player: str) -> str | None: #TODO: add bedrock support
    pattern = re.compile(generate_username_regex(player))
    playeruuid = None

    with open('./variables.csv') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            try:
                if not row[0].find("kdr::uuidname") == -1: # if the row contains the uuid and playerhex
                    if pattern.fullmatch(row[2]): # if the player's hex is in the string
                        playeruuid = row[0][13:] # grab the uuid
            except IndexError:
                pass # ignore things with no index
    return playeruuid

def get_uuid_api(player: str) -> str | None:
    raise NotImplementedError

playeruuid = get_uuid_manual(input("Input username\n>"))
if isinstance(playeruuid, str):
    print(f"{playeruuid}")
else:
    print("No uuid found")
