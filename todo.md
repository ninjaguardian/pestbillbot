Make a config that the uses a setup so they choose channels.
make sure all global variables are referenced with global, and all debugs are enabled.
setup debug for bot functions.
print error messages in bot console.
leaderboard.
more stuff in bot-console.
/help
pylint
Changeable encodings.
convert everything to async (including requests into aiohttp)
pydocs
Check all types (including function inputs and outputs) to see if anything can be more specific.
Custom error messages.
Better logging.
TODO tree.
shutdown/turn off message


Instate a JSON file on GitHub that lists every file and its severity level. When the bot is run, it will notify those who are set as ‘maintainers’ if there is a new update (can be disabled in config) or if it’s a security update it will ping and alert them and tell them to update. Also set up the security file on the GitHub. Additionally, let users set what updates they want to be notified about. Major #.x.x, medium (maybe call that something else) x.#.x, minor x.x.# or pre-release, beta, dev. Or maybe dev won’t be updatable, and it will be for unfinished stuff. Make a fancy way for the users to see the version history, and then they just have to run the command to update the bot.
