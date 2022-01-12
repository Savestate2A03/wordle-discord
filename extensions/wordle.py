import asyncio
import discord
import random
import re
from discord.ext import commands

class Wordle(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.wordlist = []
		self.games = {}

		# put word list in memory
		print('Loading word list into memory...')
		with open("./extensions/wordlist.txt", 'r') as wordlist:
			for word in wordlist:
				self.wordlist.append(word.strip())
		print('Loaded!')

	@commands.command()
	async def wordle(self, ctx, *args):
		channel = ctx.channel.id
		user    = ctx.author
		player  = user.id
		if channel not in self.games:
			await ctx.send('New wordle game started! Type `!join` to play.')
			self.games[channel] = {
				'players': {},
				'active': False,
				'word': None
			}
			await self.join(ctx, args)
		else: 
			await ctx.send(f'{user.mention} A wordle game is currently on-going! Please wait until '
						   'it\'s finished before starting a new one.')

	@commands.command()
	async def join(self, ctx, *args):
		if ctx.channel.id not in self.games:
			await ctx.send('No game is currently running! Type `!wordle` to start one.')
			return
		game   = self.games[ctx.channel.id]
		user   = ctx.author
		player = user.id
		if game['active']:
			await ctx.send(f'The game has already started! Please wait until the next.')
			return
		if player not in game['players']:
			game['players'][player] = {}
			await ctx.send(f'{user.mention} has joined! {len(game["players"])} players total.\nType `!start` to begin!')
		else:
			await ctx.send(f'{user.mention}  has already joined the game!')

	@commands.command()
	async def leave(self, ctx, *args):
		channel = ctx.channel.id
		if channel not in self.games:
			await ctx.send(f'{user.mention} No game is currently running!')
			return
		game    = self.games[channel]
		user    = ctx.author
		player  = user.id
		if player in game['players']:
			game['players'].pop(player)
			await ctx.send(f'{user.mention}  has left.')
		else:
			await ctx.send(f'{user.mention}  is already not in the game!')
		if not game['players']:
			await ctx.send(f'All players have left, stopping the game!')
			self.games.pop(channel)

	@commands.command()
	async def stop(self, ctx, *args):
		channel = ctx.channel.id
		if channel not in self.games:
			await ctx.send(f'{user.mention} No game is currently running!')
			return
		game    = self.games[channel]
		user    = ctx.author
		player  = user.id
		if game['word']:
			await ctx.send(f'The game has been stopped! The word was: ||{game["word"]}||')
		else:
			await ctx.send(f'The game has been stopped!')
		self.games.pop(channel)

	@commands.command()
	async def start(self, ctx, *args):
		channel = ctx.channel.id
		user    = ctx.author
		if channel not in self.games:
			await ctx.send(f'{user.mention} No game is currently running! Type `!wordle` to start one.')
			return
		game = self.games[channel]
		if game['active']:
			await ctx.send('A game has already started!')
			return
		if not game['players']:
			await ctx.send('At least 1 player is needed to play!')
			return
		game['word'] = random.choice(self.wordlist).lower()
		game['active'] = True
		for player in game['players']:
			game['players'][player] = {
				'name': user.display_name,
				'guesses': [],
				'prev_messages': [],
				'finished': False
			}
		await ctx.send(f'Game started with {len(game["players"])} players! Type `!guess` with your answer spoilered.')

	@commands.command()
	async def guess(self, ctx, *args):
		channel = ctx.channel.id
		user    = ctx.author
		player  = user.id
		if channel not in self.games:
			await ctx.send(f'{user.mention} No game is currently running! Type `!wordle` to start one.')
			return
		if not args:
			await ctx.send(f'{user.mention} Guess by typing in your guess spoilered (!guess ||like this||)')
			return
		guess         = args[0].lower()
		game          = self.games[channel]
		players       = game['players']
		word          = game['word'].lower()
		prev_messages = players[player]['prev_messages']
		if not game['active']:
			await ctx.send(f'{user.mention} Wait until the game has started before guessing!')
			return
		if player not in players:
			await ctx.message.delete()
			await ctx.send(f'{user.mention} You can\'t guess if you haven\'t joined!')
			return
		if game['players'][player]['finished']:
			await ctx.message.delete()
			await ctx.send(f'{user.mention} You\'ve already solved the word! Wait for others to finish.')
			return
		pattern = re.compile(r"\|\|(.+)\|\|")
		if not pattern.match(guess):
			await ctx.message.delete()
			prev_messages.append(await ctx.send(f'{user.mention} Make sure to spoiler your guess!'))
			return
		guess = pattern.match(guess).group(1)
		if len(guess) != len(word):
			await ctx.message.delete()
			prev_messages.append(await ctx.send(f'{user.mention} Your guess must be the same length as the word!'))
			return
		if guess not in self.wordlist:
			await ctx.message.delete()
			prev_messages.append(await ctx.send(f'{user.mention} Not a valid word!'))
			return
		game['players'][player]['guesses'].append(guess)
		await ctx.message.delete()
		for prev_message in prev_messages:
			await prev_message.delete()
			prev_messages.remove(prev_message)
		game['players'][player]['finished'] = (guess == word)
		if len(game['players'][player]['guesses']) >= 6:
			game['players'][player]['finished'] = True
		attached_message = user.mention
		if guess == word:
			attached_message += ' Congratulations on solving the word!'
		elif game['players'][player]['finished']:
			attached_message += f' Sorry! You\'ve run out of guesses. The word was ||`{word}`||.'
		prev_messages.append(await ctx.send(attached_message, embed=self.embed(word, game, player, user)))
		all_finished = True
		for player_i in game['players']:
			if not game['players'][player_i]['finished']:
				all_finished = False
		if all_finished:
			attached_message = f'Everyone has finished! The word was {word}. Here\'s the recap:'
			await ctx.send(attached_message, embed=self.embed_final(word, game))
			self.games.pop(channel)

	def embed(self, word, game, player, user):
		emoji_white  = "\U00002B1C"
		emoji_green  = "\U0001F7E9"
		emoji_yellow = "\U0001F7E8"
		emoji_black  = "\U00002B1B"
		keyboard = ('||``` q w e r t y u i o p\n'
					     '  a s d f g h j k l\n'
					     '   z x c v b n m```||')

		finished     = game['players'][player]['finished']
		guesses      = game['players'][player]['guesses']
		guesses_text = ''
		blocks_text  = ''
		protected_letters = []
		for i in range(6):
			compare_word = word
			if i >= len(guesses):
				if not finished:
					blocks_text += f'{(emoji_white * len(word))}\n'
				continue
			guess = guesses[i]
			guesses_text += f'{i+1}: ||`{guess}`||\n'
			# greens
			for j in range(len(word)):
				if guess[j] == compare_word[j]:
					keyboard = keyboard.replace(f' {guess[j]}', f'>{guess[j]}')
					compare_word = compare_word[:j] + ' ' + compare_word[j+1:]
					guess = guess[:j] + emoji_green + guess[j+1:]
			# yellows
			for j in range(len(word)):
				if guess[j] in compare_word:
					if guess[:(j+1)].count(guess[j]) <= compare_word.count(guess[j]):
						keyboard = keyboard.replace(f' {guess[j]}', f'>{guess[j]}')
						compare_word = compare_word.replace(guess[j], ' ', 1)
						protected_letters.append(guess[j])
						guess = guess[:j] + emoji_yellow + guess[j+1:]
					else:
						guess = guess[:j] + emoji_black + guess[j+1:]
			# blacks
			for j in range(len(word)):
				if guess[j] != emoji_green and guess[j] != emoji_yellow:
					if guess[j] not in protected_letters:
						keyboard = keyboard.replace(guess[j], f' ')
					guess = guess[:j] + emoji_black + guess[j+1:]
			blocks_text += f'{guess}\n'

		title = f"{user.display_name}'s Wordle"
		color = 0x94310a if not finished else 0x889ce1

		embed=discord.Embed(title=title, color=color)
		embed.set_thumbnail(url=user.avatar_url)
		embed.add_field(name="Block Layout", value=blocks_text, inline=True)
		embed.add_field(name="Guesses", value=guesses_text, inline=True)
		embed.add_field(name="Keyboard", value=keyboard, inline=False)
		embed.set_footer(text="Click the keyboard above to reveal it!")
		return embed

	def embed_final(self, word, game):
		emoji_white  = "\U00002B1C"
		emoji_green  = "\U0001F7E9"
		emoji_yellow = "\U0001F7E8"
		emoji_black  = "\U00002B1B"

		embed=discord.Embed(title="Wordle Recap", color=0x22aa33)

		for player in game['players']:
			finished     = game['players'][player]['finished']
			guesses      = game['players'][player]['guesses']

			embed.add_field(name=f"{game['players'][player]['name']}", value=(
				(f'Solved in {len(guesses)} guesses!') if guesses[-1] == word else (f'Did not solve ):')
			), inline=False)

			guesses_text = ''
			blocks_text  = ''
			for i in range(6):
				compare_word = word
				if i >= len(guesses):
					if not finished:
						blocks_text += f'{(emoji_white * len(word))}\n'
					continue
				guess = guesses[i]
				guesses_text += f'{i+1}: `{guess}`\n'
				# greens
				for j in range(len(word)):
					if guess[j] == compare_word[j]:
						compare_word = compare_word[:j] + ' ' + compare_word[j+1:]
						guess = guess[:j] + emoji_green + guess[j+1:]
				# yellows
				for j in range(len(word)):
					if guess[j] in compare_word:
						if guess[:(j+1)].count(guess[j]) <= compare_word.count(guess[j]):
							compare_word = compare_word.replace(guess[j], ' ', 1)
							guess = guess[:j] + emoji_yellow + guess[j+1:]
						else:
							guess = guess[:j] + emoji_black + guess[j+1:]
				# blacks
				for j in range(len(word)):
					if guess[j] != emoji_green and guess[j] != emoji_yellow:
						guess = guess[:j] + emoji_black + guess[j+1:]
				blocks_text += f'{guess}\n'

			embed.add_field(name="Block Layout", value=blocks_text, inline=True)
			embed.add_field(name="Guesses", value=guesses_text, inline=True)

		embed.set_footer(text="Wordle bot made by Savestate, thanks for playing!")
		return embed


def setup(bot):
	bot.add_cog(Wordle(bot))