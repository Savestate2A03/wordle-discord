import re
import discord
import configparser
from discord.ext import commands

class BotConfig:
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.txt')
		if not self.config.sections():
			# no config available
			self.create_default()
		self.print()

	def get(self, section, key):
		return self.config[section][key]

	def create_default(self):
		# make a new config
		self.config = configparser.ConfigParser()
		self.config['Bot Settings'] = {
			'discord_token': 'INSERT_TOKEN_HERE',
			'command_prefix': '!'
		}
		with open('config.txt', 'w') as f: self.config.write(f)
		self.set()

	def set(self):
		for section in self.config:
			if section == "DEFAULT": continue
			print(f'[{section}]')
			for key in self.config[section]:
				value = input(f'{key}? ({self.config[section][key]}):')
				if value: 
					self.config[section][key] = value
		with open('config.txt', 'w') as f: self.config.write(f)

	def print(self):
		print("----------------")
		print("|    config    |")
		print("----------------")
		# print out each non default section of config
		for section in self.config:
			if section == "DEFAULT": continue
			print(f'[{section}]')
			for key in self.config[section]:
				value = self.config[section][key]
				# don't print the discord token lol
				if key == 'discord_token':
					value = f'{value[:12]}...'
				print(f'{key} = {value}')
			print('')

# setup config
config = BotConfig()

# setup bot client
client = commands.Bot(command_prefix = config.get('Bot Settings', 'command_prefix'))

# remove default help command
client.remove_command('help')

# load extensions
client.load_extension('extensions.wordle')

# ready
@client.event
async def on_ready():
	print('wordle-bot is online...')

# run
client.run(config.get('Bot Settings', 'discord_token'))