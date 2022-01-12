# wordle-discord
A simple Discord bot for group wordle.

## Setup
Run the bot with:
```
python wordle-discord.py
```
Required packages are: `discord.py`. You can install it with:
```
python -3 -m pip install -U discord.py
```

## Running
When you first run the program, it will ask you for your Discord bot token and preferred command invoker. 
Afterwards, it will save these to a `config.txt` file so you don't have to enter them in again on re-launch.

## Commands
* `!wordle` Initiates a Wordle game in the current channel.
* `!join` Joins an un-started Wordle game in the current channel.
* `!start` Starts the current Wordle game with all joined users.
* `!guess ||word||` Guess a word. Must be spoilered or it won't be recognized. Deletes the message after processed.
* `!leave` Leaves Wordle game in the current channel, started or not.
* `!giveup` Gievs up in an active Wordle game. Notably does not remove from final results recap.
* `!stop` Stops the current game in full.

## Word List
Currently using words from various sources. Many words are too weird honestly, and there's some proper nouns thrown in the mix. I'm too lazy to sift through them though. If you have a better word list you'd like to provide, feel free to submit a PR.

## Notes
Currently hardcoded to only do 6 guesses. Not too much trouble to change, but I'm leaving as is. Submit a PR if you'd like to add custom guess numbers.
