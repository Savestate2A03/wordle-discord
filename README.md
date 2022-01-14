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
* `!wordle` Initiates a Wordle game in the current channel
* `!join` Joins a Wordle game in the current channel
* `!guess ||word||` Guess a word. Must be spoilered or it won't be recognized. Deletes the message after processed
* `!giveup` Gives up in an active Wordle game
* `!stop` Stops the current game in full

## Visual Feedback
The board starts out spoilered, but players can click their words and keyboard for themselves. This is a trust based game, don't go clicking your opponents' boards.

> Before unspoilering
> 
> ![image](https://user-images.githubusercontent.com/22358804/149238818-08fc9507-5793-43a5-a09f-a0e6e708750c.png)

> After unspoilering
> 
> ![image](https://user-images.githubusercontent.com/22358804/149238930-2d2b66a8-4fd8-4a48-8c23-592ef7e13b14.png)

The keyboard will remove letters no longer available to you, and a right facing pointer will point to letters that have been hinted or solved by your previous guesses.

When you're finished, the game will make a nice recap showing the results of the game:

![image](https://user-images.githubusercontent.com/22358804/149239173-0a0abc75-1d93-4424-bb12-e7465d2fb4d7.png)


## Word List
Currently using words from various sources. Many words are too weird honestly, and there's some proper nouns thrown in the mix. I'm too lazy to sift through them though. If you have a better word list you'd like to provide, feel free to submit a PR.

## Notes
Currently hardcoded to only do 6 guesses. Not too much trouble to change, but I'm leaving as is. Submit a PR if you'd like to add custom guess numbers.
