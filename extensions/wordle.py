import asyncio
import discord
import random
import re
from discord.ext import commands

class Wordle(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.wordlist = []
        self.guesslist = []
		self.games = {}

		# put word list in memory
		print('Loading word list into memory...')
		with open("./extensions/wordlist.txt", 'r') as wordlist:
			for word in wordlist:
				self.wordlist.append(word.strip())
		with open("./extensions/guesslist.txt", 'r') as guesslist:
			for word in guesslist:
				self.guesslist.append(word.strip())
		print('Loaded!')

	@commands.command()
	async def wordle(self, ctx, *args):
		channel = ctx.channel.id
		user    = ctx.author
		player  = user.id
		if channel not in self.games:
			await ctx.send('New wordle game started! Type `!join` to play.')
			# game context per channel
			self.games[channel] = {
				'players': {},
				'word': random.choice(self.wordlist).lower()
			}
			await self.join(ctx, args)
			await ctx.send(f'Game started! Type `!guess` with your answer spoilered. Alternatively, type in `!giveup` to forfeit.')
		else:
			await ctx.send(f'{user.mention} A wordle game is currently on-going! Please wait until '
						   'it\'s finished before starting a new one.')

	@commands.command()
	async def join(self, ctx, *args):
		# allows a user to join a game
		if ctx.channel.id not in self.games:
			await ctx.send('No game is currently running! Type `!wordle` to start one.')
			return
		game   = self.games[ctx.channel.id]
		user   = ctx.author
		player = user.id
		if player not in game['players']:
			# initial player context
			game['players'][player] = {
				'name': user.display_name,
				'guesses': [],
				'prev_messages': [],
				'finished': False
			}
			await ctx.send(f'{user.mention} has joined! {len(game["players"])} players total.')
		else:
			await ctx.send(f'{user.mention}  has already joined the game!')

	@commands.command()
	async def giveup(self, ctx, *args):
		# deletes player context from game.
		channel = ctx.channel.id
		if channel not in self.games:
			await ctx.send(f'{user.mention} No game is currently running!')
			return
		game    = self.games[channel]
		user    = ctx.author
		player  = user.id
		if player in game['players']:
			# all info for a player is contained in
			# this context so it's fine to delete one mid-game.
			if not game['players'][player]['finished']:
				game['players'][player]['finished'] = True
				await ctx.send(f'{user.mention} has given up.')
				await self.check_finish(ctx)
			else: 
				await ctx.send(f'{user.mention} is already finished!')
		else:
			await ctx.send(f'{user.mention}  is not in the game!')

	@commands.command()
	async def stop(self, ctx, *args):
		# stops the current game. currently not
		# role limited. if someone is stopping 
		# your game to troll, kick them (:
		channel = ctx.channel.id
		if channel not in self.games:
			await ctx.send(f'{user.mention} No game is currently running!')
			return
		game    = self.games[channel]
		user    = ctx.author
		player  = user.id
		await self.check_finish(ctx, forced=True)

	@commands.command()
	async def guess(self, ctx, *args):
		# can probably be split up into multiple parts. oh well lol
		channel = ctx.channel.id
		user    = ctx.author
		player  = user.id
		# basic integrity checks
		if channel not in self.games:
			await ctx.send(f'{user.mention} No game is currently running! Type `!wordle` to start one.')
			return
		# first argument required, its the gussed word
		if not args:
			await ctx.send(f'{user.mention} Guess by typing in your guess spoilered (!guess ||like this||)')
			return
		# setting up some useful variables
		guess         = args[0].lower()
		game          = self.games[channel]
		players       = game['players']
		word          = game['word'].lower()
		prev_messages = players[player]['prev_messages']
		# context checking
		if player not in players:
			await ctx.message.delete()
			await ctx.send(f'{user.mention} You can\'t guess if you haven\'t joined!')
			return
		if game['players'][player]['finished']:
			await ctx.message.delete()
			await ctx.send(f'{user.mention} You\'ve already solved the word! Wait for others to finish.')
			return
		# make sure guess is spoilered with regex matching
		pattern = re.compile(r"\|\|(.+)\|\|")
		if not pattern.match(guess):
			await ctx.message.delete()
			prev_messages.append(await ctx.send(f'{user.mention} Make sure to spoiler your guess!'))
			return
		# extract guess and do checks on it
		guess = pattern.match(guess).group(1)
		if len(guess) != len(word):
			await ctx.message.delete()
			prev_messages.append(await ctx.send(f'{user.mention} Your guess must be the same length as the word!'))
			return
		if guess not in self.guesslist:
			await ctx.message.delete()
			prev_messages.append(await ctx.send(f'{user.mention} Not a valid word!'))
			return
		# guess passes checks, add to player's word list
		players[player]['guesses'].append(guess)
		# then delete their guess for good measure
		await ctx.message.delete()
		# delete all pending messages for user as well to clean up board
		for prev_message in prev_messages:
			await prev_message.delete()
			prev_messages.remove(prev_message)
		# mark player's context as finished if guessed correctly
		players[player]['finished'] = (guess == word)
		# limit to 6 guesses as per official Wordle
		if len(game['players'][player]['guesses']) >= 6:
			players[player]['finished'] = True
		# default message mentions user, add more past that
		attached_message = user.mention
		if guess == word:
			attached_message += ' Congratulations on solving the word!'
		elif players[player]['finished']:
			attached_message += f' Sorry! You\'ve run out of guesses. The word was ||`{word}`||.'
		# send a message containing the attached message and
		# an embed generated by the Wordle embed generator.
		prev_messages.append(await ctx.send(attached_message, embed=self.embed(word, game, player, user)))
		await self.check_finish(ctx)

	async def check_finish(self, ctx, forced=False):
		channel = ctx.channel.id
		game    = self.games[channel]
		word    = game['word']
		players = game['players']
		# if all players are finished, wrap up and call the final embed.
		all_finished = True
		for player_i in players:
			if not players[player_i]['finished']:
				all_finished = False
		if all_finished or forced:
			# delete any remaining pending messages
			for player_i in players:
				for prev_message in players[player_i]['prev_messages']:
					await prev_message.delete()
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
		# loop through all 6 guessed words (if they exist)
		for i in range(6):
			# we modify the word as a part of the
			# checking process, so we store it to
			# a temporary variable that we modify
			compare_word = word
			if i >= len(guesses):
				if not finished:
					# only draw white squares if the player isn't finished
					blocks_text += f'{(emoji_white * len(word))}\n'
				continue
			# get the current guess and add it to the guesses embed text
			guess = guesses[i]
			guesses_text += f'{i+1}: ||`{guess}`||\n'
			# greens checking
			for j in range(len(word)):
				# if the current character is the same as the word...
				if guess[j] == compare_word[j]:
					# mark it on the keyboard
					keyboard = keyboard.replace(f' {guess[j]}', f'>{guess[j]}')
					# remove it from the word we're comparing to
					compare_word = compare_word[:j] + ' ' + compare_word[j+1:]
					# add it to the protected characters list to prevent
					# it from being removed during the black square check
					protected_letters.append(guess[j])
					# and replace the character itself with a green square emoji
					guess = guess[:j] + emoji_green + guess[j+1:]
			# yellows
			for j in range(len(word)):
				# if the current character is in the word...
				if guess[j] in compare_word:
					# don't recall if this comparison is redunant now with the
					# character replacement tech. too lazy to bug check it so
					# i'm leaving it in. 
					if guess[:(j+1)].count(guess[j]) <= compare_word.count(guess[j]):
						# mark it on the keyboard
						keyboard = keyboard.replace(f' {guess[j]}', f'>{guess[j]}')
						# remove it from the word we're comparing to
						compare_word = compare_word.replace(guess[j], ' ', 1)
						# add it to the protected characters list to prevent
						# it from being removed during the black square check
						protected_letters.append(guess[j])
						# and replace the character itself with a yellow square emoji
						guess = guess[:j] + emoji_yellow + guess[j+1:]
					else:
						guess = guess[:j] + emoji_black + guess[j+1:]
			# blacks
			for j in range(len(word)):
				# if the current character is in the word was not
				# replaced by a green or yellow square emoji...
				if guess[j] != emoji_green and guess[j] != emoji_yellow:
					# AND it's not in the protected letters list...
					if guess[j] not in protected_letters:
						# remove it from the visible keyboard
						keyboard = keyboard.replace(guess[j], f' ')
					# regardless, replace it with a black square emoji in the guess
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
		# this is pretty much a watered down version of the
		# above function. read it if you need help understanding 
		# what is going on.

		if not game['players']:
			return None

		emoji_white  = "\U00002B1C"
		emoji_green  = "\U0001F7E9"
		emoji_yellow = "\U0001F7E8"
		emoji_black  = "\U00002B1B"

		embed=discord.Embed(title="Wordle Recap", color=0x22aa33)

		for player in game['players']:
			finished     = game['players'][player]['finished']
			guesses      = game['players'][player]['guesses']

			if len(guesses) <= 0:
				continue

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