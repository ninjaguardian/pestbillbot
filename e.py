import csv
import re

def create_regex_pattern(input_string: str) -> str:
    pattern = ''.join([f'[{char.upper()}{char.lower()}]' if char.isalpha() else char for char in input_string])
    return pattern

playerhex = "Ninjaguardian68".encode('utf-8').hex()
pattern = re.compile(playerhex)
print(playerhex)
file = open('./variables.csv')
type(file)
csvreader = csv.reader(file)
#print(header)
for row in csvreader:
    rowstr = str(row)
    if not rowstr.find("kdr::uuidname") == -1:
        if not rowstr.find(playerhex.upper()) == -1:
            if not rowstr.find("]", 0, len(playerhex)+73) == -1: # makes sure it's an exact match
                playeruuid = ""
                for i in range(15,51):
                    playeruuid = playeruuid+rowstr[i]

# # file = open('./variables.csv')
# # type(file)
# # csvreader = csv.reader(file)
# # #print(header)
# # for row in csv.reader(open('./variables.csv')):
# #     rowstr = str(row)
# #     if not rowstr.find("kdr::uuidname") == -1:
# #             for row in csvreader:
# #                 rowstr = str(row)
# #                 if not rowstr.find("kdr::uuidname") == -1:
# #                     if not rowstr.find(playerhex.upper()) == -1:
# #                         if not rowstr.find("]", 0, len(playerhex)+73) == -1:
# #                             playeruuid = ""
# #                             for i in range(15,51):
# #                                 playeruuid = playeruuid+rowstr[i]

# # with open('./variables.csv') as file:
# #     for row in csv.reader(file):
# #         rowstr = str(row)
# #         if not rowstr.find("kdr::uuidname") == -1:
# #                 for row in csv.reader(file):
# #                     rowstr = str(row)
# #                     if not rowstr.find("kdr::uuidname") == -1:
# #                         if not rowstr.find(playerhex.upper()) == -1:
# #                             if not rowstr.find("]", 0, len(playerhex)+73) == -1:
# #                                 playeruuid = ""
# #                                 for i in range(15,51):
# #                                     playeruuid = playeruuid+rowstr[i]


# print(playeruuid)




def generate_hex_pattern(s):
    hex_pattern_parts = []

    for char in s:
        if char.isdigit():
            # Convert digit to hex and format as (##)
            hex_value = format(int(char), 'x').upper()
            hex_pattern_parts.append(f'3{hex_value}')
        elif char.isalpha():
            # Convert letter to hex for both uppercase and lowercase
            hex_upper = format(ord(char.upper()), 'x').upper()
            hex_lower = format(ord(char.lower()), 'x').upper()
            # Ensure two-digit format
            hex_upper = hex_upper.zfill(2)
            hex_lower = hex_lower.zfill(2)
            hex_pattern_parts.append(f'({hex_upper}|{hex_lower})')

    # Join all parts with an empty string to form the full regex pattern
    hex_pattern = ''.join(hex_pattern_parts)
    
    # Return the regex pattern with anchors for start (^) and end ($)
    return f'^{hex_pattern}$'

# Example usage
pattern = generate_hex_pattern("ninjaguardian68")
print(pattern)
