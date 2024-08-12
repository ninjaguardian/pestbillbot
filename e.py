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
