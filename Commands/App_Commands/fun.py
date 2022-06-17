import asyncio
from cgitb import text
from typing import Union
import aiohttp
from discord.ext import commands
import discord
import random
from random import choice
from asyncio import sleep
from aiohttp import ClientSession
from asyncio import TimeoutError
from discord import app_commands
from discord.app_commands import Choice
from discord import ui


class EmbedFields(ui.Modal, title='Embed Field'):
    def __init__(self, number, message: discord.InteractionMessage, embed: discord.Embed):
        super().__init__()
        self.number = number
        self.message = message
        self.embed = embed

    titel = ui.TextInput(label='Title')
    description = ui.TextInput(label='Description', style=discord.TextStyle.paragraph)
    inline = ui.TextInput(label="Inline (answer (t)rue or (f)alse)", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        if self.inline in ["true", "t", "yes", "y"]: inline=True
        else: inline=False
        await self.message.edit(embed=self.embed.add_field(name=self.titel, value=self.description, inline=inline))
        await interaction.response.send_message(f"Successfully set Field {self.number}", ephemeral=True)

class button(ui.Button):
    def __init__(self, number, message: discord.InteractionMessage, embed, msg):
        self.number = number
        self.message = message
        self.embed = embed
        self.msg = msg
        super().__init__(style=discord.ButtonStyle.blurple, label=f"Field {number}")
    
    async def callback(self, interaction: discord.Interaction):
        for i in self.view.children:
            if i.label == self.label:
                self.view.children.remove(i)
                await self.msg.edit(view=self.view)
        await interaction.response.send_modal(EmbedFields(self.number, self.message, self.embed))


class view(ui.View):
    def __init__(self, number, message, embed, msg):
        super().__init__()
        self.number = number
        self.message = message
        self.embed = embed
        self.msg = msg
        for i in range(number):
            self.add_item(button((i + 1),message,embed,msg))    

class Confirm(ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=10)
        self.value = None
        self.user = user

    @ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, button: ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        await interaction.response.send_message("Confirmed!", ephemeral=True)
        self.value = True
        self.stop()
    
    @ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, button: ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        await interaction.response.send_message("Cancelled!", ephemeral=True)
        self.value = False
        self.stop()

class RPSGame(ui.View):
    def __init__(self, users: list[discord.User]):
        super().__init__(timeout=60)
        self.users = users
        self.user1 = users[0]
        self.user2 = users[1]
        self.user1choice = None
        self.user2choice = None
    
    @ui.button(emoji="🪨", style=discord.ButtonStyle.blurple)
    async def rock(self, button: ui.Button, interaction: discord.Interaction):
        if interaction.user not in self.users:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        if interaction.user == self.user1:
            if self.user1choice: return await interaction.response.send_message("You have already responded.", ephemeral=True)
            self.user1choice = "Rock"
        else:
            if self.user2choice: return await interaction.response.send_message("You have already responded.", ephemeral=True)
            self.user2choice = "Rock"
        await interaction.response.send_message("You have chosen Rock!", ephemeral=True)
        if self.user2choice and self.user1choice:
            try:await self.stop()
            except:pass
        if self.user1choice and self.user2 == interaction.client.user:
            try:await self.stop()
            except:pass

    
    @ui.button(emoji="📜", style=discord.ButtonStyle.blurple)
    async def paper(self, button: ui.Button, interaction: discord.Interaction):
        if interaction.user not in self.users:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        if interaction.user == self.user1:
            if self.user1choice: return await interaction.response.send_message("You have already responded.", ephemeral=True)
            self.user1choice = "Paper"
        else:
            if self.user2choice: return await interaction.response.send_message("You have already responded.", ephemeral=True)
            self.user2choice = "Paper"
        await interaction.response.send_message("You have chosen Paper!", ephemeral=True)
        if self.user2choice and self.user1choice:
            try:await self.stop()
            except:pass
        if self.user1choice and self.user2 == interaction.client.user:
            try:await self.stop()
            except:pass
    
    @ui.button(emoji="✂️", style=discord.ButtonStyle.blurple)
    async def scissors(self, button: ui.Button, interaction: discord.Interaction):
        if interaction.user not in self.users:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        if interaction.user == self.user1:
            if self.user1choice: return await interaction.response.send_message("You have already responded.", ephemeral=True)
            self.user1choice = "Scissors"
        else:
            if self.user2choice: return await interaction.response.send_message("You have already responded.", ephemeral=True)
            self.user2choice = "Scissors"
        await interaction.response.send_message("You have chosen Scissors!", ephemeral=True)
        if self.user2choice and self.user1choice:
            try:await self.stop()
            except:pass
        if self.user1choice and self.user2 == interaction.client.user:
            try:await self.stop()
            except:pass

class Slash_Fun(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot        

    @app_commands.command(name = "echo", description = "Copies your message")
    @app_commands.describe(text="The text for me to mimic")
    @app_commands.guilds(921230858311057418)
    async def echo(self, interaction: discord.Interaction, text: str):
        await interaction.response.send_message(f'{text} - **{interaction.user.display_name}**')


    @app_commands.command(name = "choose", description = "Chooses a random choice.")
    @app_commands.describe(first="First Choice", second="Second Choice", third="Third Choice", fourth="Fourth Choice", fifth="Fifth Choice", sixth="Sixth Choice", seventh="Seventh Choice", eighth="Eighth Choice", ninth="Ninth Choice", tenth="Tenth Choice")
    @app_commands.guilds(921230858311057418)
    async def choose(self, interaction: discord.Interaction, first: str, second: str, third: str = None, fourth: str = None, fifth: str = None, sixth: str = None, seventh: str = None, eighth: str = None, ninth: str = None, tenth: str = None):
        choices = [first,second,third,fourth,fifth,sixth,seventh,eighth,ninth,tenth]
        for i in range(10):
            try:choices.remove(None)
            except: continue
        await interaction.response.send_message(":drum: I choose... :drum:")
        await asyncio.sleep(2)
        await (await interaction.original_message()).edit(content=f":tada: I chose `{choice(choices)}`!")
    
    @app_commands.command(name = "yomama", description = "Sends a Yo Mama joke!")
    @app_commands.describe(user="The User You Want to Send a Joke to")
    @app_commands.guilds(921230858311057418)
    async def yomama(self, interaction: discord.Interaction, user: discord.User = None):
        if not user:
            user = interaction.user

        async with ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get("https://api.yomomma.info/") as res:
                res = await res.json()
                
        joke = res["joke"]
        await interaction.response.send_message(f"{user.mention} {joke}")
    
    @app_commands.command(name = "8ball", description = "Try your hand at the magic 8ball!")
    @app_commands.describe(question="The Question You Want to Ask to the Magic 8ball")
    @app_commands.guilds(921230858311057418)
    async def eightBall(self, interaction: discord.Interaction, question: str):
        response = choice(["It is certain.", "Without a doubt.", "You may rely on it.", "Yes, definitely.", "It is decidedly so.", "As I see it, yes.", "Most likely.", "Yes.", "Outlook good.", "Signs point to yes.", "Reply hazy try again.", "Better not tell you now.", "Ask again later.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "Outlook not so good.", "My sources say no.", "Very doubtful.", "My reply is no."])
        await interaction.response.send_message("https://tenor.com/view/8ball-bart-simpson-shaking-shake-magic-ball-gif-17725278")
        embed = discord.Embed(title=response, color=choice(self.bot.colorList))
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.add_field(name="Question", value=question + "?")
        embed.add_field(name="Result", value=response, inline=False)
        embed.set_thumbnail(url="https://i.imgflip.com/4/1c8tfl.jpg")
        await sleep(1)
        msg = (await interaction.original_message())
        await msg.edit(content=None, embed=embed)

    #dice roll(badly coded by darkfang), no idea if it works
    @app_commands.command(name = "rolldice", description = "Rolls a dice (or sometimes many more...)")
    @app_commands.describe(dice="Number of Dice to Roll", faces="Number of Faces per Dice", add="The Amount to Add to the End Result")
    @app_commands.guilds(921230858311057418)
    async def rolldice(self, interaction: discord.Interaction, dice: int=1, faces: int=6, add: int=0):
        if faces<32767 and dice<32767 and add<32767:
            rollresult=[random.randint(1, faces) for _ in range(dice)]
            rollresult=sum(rollresult)+add
            await interaction.response.send_message("https://tenor.com/view/quiddie-hjrpg-roll-dice-dnd-gif-13900378")
            em = discord.Embed(title = "Roll Dice",color=0x398564)
            em.add_field(name = "Rolled number", value = f"{interaction.user.mention} rolled a {rollresult}!", inline=False)
            em.add_field(name = "Dice Amount", value = dice, inline=True)
            em.add_field(name = "Sides", value = faces, inline=True)
            em.add_field(name = "Added Amount", value=add, inline=True)
            em.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
            em.set_thumbnail(url=interaction.user.avatar.url)
            await sleep(3)
            msg = await interaction.original_message()
            await msg.edit(content=None, embed=em)
        else:
            await interaction.response.send_message("Are you trying to break the bot?")
        
    #coin flip, flips a coin
    @app_commands.command(name = "coinflip", description = "Flips a coin (please don't bet skybucks with this)")
    @app_commands.guilds(921230858311057418)
    async def coinflip(self, interaction: discord.Interaction):
        flipresult = random.choice(['heads', 'tails'])
        imgurls = {"heads":"http://www.clker.com/cliparts/7/d/e/0/139362185558690588heads-md.png", "tails": "https://cdn.discordapp.com/attachments/921230858311057421/933363312022945842/iu.png"}
        await interaction.response.send_message("https://tenor.com/view/coin-flip-quarter-gif-9665789")
        em = discord.Embed(title = "Coin Flip", color=choice(self.bot.colorList))
        em.add_field(name=f"{interaction.user}'s flip", value= f"{interaction.user.mention} flipped {flipresult}!", inline=False)
        em.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        em.set_thumbnail(url=imgurls[flipresult])
        await sleep(2.5)
        msg = (await interaction.original_message())
        await msg.edit(content=None, embed=em)

    @app_commands.command(name = "numbergame", description = "Can you guess the number?")
    @app_commands.describe(max="The Maximum Number in a Number Game")
    @app_commands.guilds(921230858311057418)
    async def numbergame(self, interaction: discord.Interaction, max: int=100):
      mystnum=random.randint(1,max)
      guess='-1'
      gc=0
      players={}

      async with self.bot.db.execute("SELECT * FROM numgameChannels;") as cur: channels = await cur.fetchall()

      if interaction.channel_id in [i[0] for i in channels]:
          return await interaction.response.send_message("Sorry, a Number Game is already running inside this channel")

      em = discord.Embed(title = "Number Game Start", color=discord.Color.blue())
      em.add_field(name = "Type a number in the chat", value = f"Guess the between **1** and **{max}**", inline=False)
      em.set_footer(text = "You have 10 seconds to respond")
      em.set_thumbnail(url=interaction.user.avatar.url)
      await interaction.response.send_message(embed=em)
      await self.bot.db.execute("INSERT INTO numgameChannels VALUES (?);", (interaction.channel_id))
      async def gamei():
        nonlocal guess
        nonlocal players
        try:
          msg = await self.bot.wait_for("message", check=lambda msg: msg.channel == interaction.channel, timeout= 10)
          if (msg.content).isnumeric() and max>=int(msg.content):
            guess=int(msg.content)
            if str(msg.author) not in players:
                  players[str(msg.author)]=1
            else:
                players[str(msg.author)]=(players[str(msg.author)]+1)
            if (guess) > mystnum:
                em = discord.Embed(title = "Try Again", color=discord.Color.red())
                em.add_field(name=f"{interaction.user.display_name} Your number was too *high* try guessing *lower*", value = "waiting for a response", inline=False)
                em.set_thumbnail(url='http://www.clipartbest.com/cliparts/KTj/Xyg/KTjXyg7Tq.jpeg')
                await interaction.followup.send(embed=em, username=self.bot.user.display_name, avatar_url=self.bot.user.avatar.url)
                await gamei()
            elif (guess) < mystnum:
                em = discord.Embed(title = "Try Again", color=discord.Color.red())
                em.add_field(name=f"{interaction.user.display_name} Your number was too *low* try guessing *higher*", value = "waiting for a response", inline=False)
                em.set_thumbnail(url='http://www.clipartbest.com/cliparts/aTq/Eoz/aTqEoznTM.png')
                await interaction.followup.send(embed=em, username=self.bot.user.display_name, avatar_url=self.bot.user.avatar.url)
                await gamei()
            else:
              await self.bot.db.execute("DELETE FROM numgameChannels WHERE channelID = ?;", (interaction.channel_id))
              em = discord.Embed(title = "Number Game Results", color=discord.Color.green())
              em.add_field(name = "Winner!", value = f"{msg.author.mention} guessed the number in {players[str(msg.author)]} guesses", inline=False)
              em.set_footer(text = f"The number was {mystnum}")
              em.set_thumbnail(url=interaction.user.avatar.url)
              finalplayers=list(players.keys())
              guesses=list(players.values())
              finalfinal=""
              for i in range (0,len(finalplayers)):
                finalfinal=finalfinal+str(finalplayers[i])+': '+str(guesses[i])+'\n'
              em.add_field(name='Players:', value=finalfinal)
              await interaction.followup.send(embed=em, username=self.bot.user.display_name, avatar_url=self.bot.user.avatar.url)
          elif (msg.content in ('end', 'e', 'quit', 'stop', 'q', 'quit') and interaction.user==msg.author):
                await self.bot.db.execute("DELETE FROM numgameChannels WHERE channelID = ?;", (interaction.channel_id))
                await interaction.followup.send('Game ended', username=self.bot.user.display_name, avatar_url=self.bot.user.avatar.url)
                pass
          else:
            await gamei()
        except TimeoutError:
          await interaction.followup.send (f"No one responded in time- the number was **{mystnum}**", username=self.bot.user.display_name, avatar_url=self.bot.user.avatar.url)
      await gamei()

    @app_commands.command(name = "sendembed", description = "Sends an embed of your desire!")
    @app_commands.guilds(921230858311057418, 726776108351094844)
    @app_commands.describe(title="The Title of the Embed", description="The Description of the Embed", footer="The Footer of the Embed", thumbnail="The Image of Embed Thumbnail", fields="Number of Fields in the Embed")
    @app_commands.choices(color=[
        Choice(name="Blue", value=0),
        Choice(name="Light Blue", value=1),
        Choice(name="Red", value=2),
        Choice(name="Yellow", value=3),
        Choice(name="Purple", value=4),
        Choice(name="Cyan", value=5),
        Choice(name="White", value=6),
        Choice(name="Gold", value=7),
        Choice(name="Brown", value=8)
    ])
    async def sendembed(self, interaction: discord.Interaction, title: str, description: str = None, footer: str = None, color: Choice[int] = random.randint(0, 8), thumbnail: discord.Attachment = None, fields: app_commands.Range[int, 0, 10] = 0):
        if footer is None:
            footer = f"Requested by {interaction.user.display_name}"
        em = discord.Embed(title = "A Title", color=choice(self.bot.colorList), description="A Description")
        def c(m):
            return m.author == interaction.user and m.channel == interaction.channel

        em = discord.Embed(title = title, description = description, color=self.bot.colorList[color.value if type(color) == Choice else color])
        em.set_footer(text=footer, icon_url=interaction.user.avatar.url)
        if thumbnail:
            em.set_thumbnail(url=thumbnail.url)
        if fields != 0:
            await interaction.response.send_message("I have sent your embed." if fields == 0 else "I have sent your embed. Please click the following buttons in order to create fields.", ephemeral=True)
            msg = await interaction.original_message()
            mesg = await interaction.channel.send(embed=em)
            await interaction.edit_original_message(view=view(fields, mesg, em, msg))
        else:
            await interaction.response.send_message("I have sent your embed.", ephemeral=True)
            await interaction.channel.send(embed=em)
        
    @app_commands.command(name = "actlike", description = "Impersonate your friends, or even enemies!")
    @app_commands.describe(user="The User to Impersonate", content="Content to Impersonate With")
    @app_commands.guilds(921230858311057418, 726776108351094844)
    async def actlike(self, interaction: discord.Interaction, user: discord.User, content: str):
        webhook = await interaction.channel.create_webhook(name=user.nick or user.name, avatar=await user.avatar.read())
        await interaction.response.send_message("Done!", ephemeral=True)
        await webhook.send(content)
        await webhook.delete()

    @app_commands.command(name="rps")
    @app_commands.guilds(921230858311057418)
    async def rockpaperscissors(self, interaction: discord.Interaction, user: discord.User = None):
        if interaction.user == user: return await interaction.response.send_message("You can't play against yourself...", ephemeral=True)
        if user.bot: 
            if user == interaction.client.user:
                user = None
            else: return await interaction.response.send_message("You can't play against a bot...", ephemeral=True)
        user1content, user2content = None, None
        if not user:
            choices = ['Rock', 'Paper', 'Scissors']
            user2content = choice(choices)
            view = RPSGame([interaction.user, self.bot.user])
            await interaction.response.send_message(f"{interaction.user.mention} Choose Rock, Paper, or Scissors", view=view)
            msg = await interaction.original_message()
            await view.wait()
            for i in view.children:
                i.disabled = True
            await msg.edit(view=view)
            if not view.user1choice: return await interaction.followup.send(f"{interaction.user.mention} please choose Rock, Paper, or Scissors. Automatically cancelled the game.", ephemeral=True)
            user1content = view.user1choice
        else:
            view = Confirm(user=user)
            await interaction.response.send_message(f"{user.mention} Do you want to play Rock Paper Scissors with {interaction.user.mention}?", view=view)
            msg = await interaction.original_message()
            await view.wait()
            for i in view.children:
                i.disabled = True
            await msg.edit(view=view)
            if view.value is None:
                return await interaction.followup.send(f"No response from {user.mention}. Automatically cancelled the game.")
            elif not view.value:
                return await interaction.followup.send(f"{interaction.user.mention} did not want to play. Cancelling the game.")
            else:
                view = RPSGame([interaction.user, user])
                await interaction.followup.send(f"{interaction.user.mention} {user.mention} Choose Rock (:rock:), Paper (:scroll:), or Scissors (:scissors:)", view=view)
                await view.wait()
                if not view.user1choice: return await interaction.followup.send(f"{interaction.user.mention} did not choose Rock, Paper, or Scissors. Cancelled the game.")
                if not view.user2choice: return await interaction.followup.send(f"{user.mention} did not choose Rock, Paper, or Scissors. Cancelled the game.")
                user1content, user2content = view.user1choice, view.user2choice
        embed = discord.Embed(color=0xf0f8ff)
        if user1content.lower() in ("r", "rock"):
            if user2content.lower() in ('r', "rock"):
                embed.title = "Draw!"
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            elif user2content.lower() in ('p', "paper"):
                embed.title = f"{user.display_name if user else self.bot.user.display_name} Wins!"
                embed.set_thumbnail(url=user.avatar.url if user else self.bot.user.avatar.url)
            elif user2content.lower() in ('s', "scissors"):
                embed.title = f"{interaction.user.display_name} Wins!"
                embed.set_thumbnail(url=interaction.user.avatar.url)
            else:
                return await interaction.followup.send(f"{user.mention} Please choose Rock, Paper, or Scissors")
        elif user1content.lower() in ("p", "paper"):
            if user2content.lower() in ('r', "rock"):
                embed.title = f"{interaction.user.display_name} Wins!"
                embed.set_thumbnail(url=user.avatar.url if user else self.bot.user.avatar.url)
            elif user2content.lower() in ('p', "paper"):
                embed.title = "Draw!"
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            elif user2content.lower() in ('s', "scissors"):
                embed.title = f"{user.display_name if user else self.bot.user.display_name} Wins!"
                embed.set_thumbnail(url=user.avatar.url if user else self.bot.user.avatar.url)
            else:
                return await interaction.followup.send(f"{user.mention} Please choose Rock, Paper, or Scissors")
        elif user1content.lower() in ("s", "scissors"):
            if user2content.lower() in ('r', "rock"):
                embed.title = f"{user.display_name if user else self.bot.user.display_name} Wins!"
                embed.set_thumbnail(url=user.avatar.url if user else self.bot.user.avatar.url)
            elif user2content.lower() in ('p', "paper"):
                embed.title = f"{interaction.user.display_name} Wins!"
                embed.set_thumbnail(url=interaction.user.avatar.url)
            elif user2content.lower() in ('s', "scissors"):
                embed.title = "Draw!"
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            else:
                return await interaction.followup.send(f"{user.mention} Please choose Rock, Paper, or Scissors.")
        else:
            return await interaction.followup.send(f"{interaction.user.mention} Please choose Rock, Paper, or Scissors.")
        embed.add_field(name=f"{interaction.user.display_name}'s Choice", value=user1content)
        embed.add_field(name=f"{user.display_name if user else self.bot.user.display_name}'s Choice", value=user2content)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="addjoke",description="Add a joke to the list of jokes!")
    @app_commands.guilds(921230858311057418)
    @app_commands.describe(joke="The Joke You Want to Add")
    async def addjoke(self, interaction: discord.Interaction, joke : str):
        async with self.bot.db.execute("SELECT * FROM jokes WHERE joke = ?;",(joke,)) as cur: jokes = await cur.fetchone()
        if jokes: return await interaction.response.send_message("That joke already exists.", ephemeral=True)
        await self.bot.db.execute("INSERT INTO jokes VALUES (?,?);",(int(interaction.user.id),joke))
        embed = discord.Embed(title="Added Joke :thumbsup:",color=0x5ac18e)
        embed.add_field(name="Joke",value=joke)
        embed.add_field(name="Author",value=interaction.user.mention)
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
        await self.bot.db.commit()

    @app_commands.command(name="joke",description="choose a random joke from the list of jokes")
    @app_commands.guilds(921230858311057418)
    @app_commands.describe(user="The User to Search Jokes For")
    async def joke(self, interaction: discord.Interaction, user: discord.User = None):
        if user is not None:
            async with self.bot.db.execute("SELECT * FROM jokes WHERE id = ? ORDER BY RANDOM() LIMIT 1;",(user.id,)) as cur: joke = await cur.fetchone()
            person = user
        else:
            async with self.bot.db.execute("SELECT * FROM jokes ORDER BY RANDOM() LIMIT 1;") as cur: joke = await cur.fetchone()
            if not joke: return await interaction.response.send_message("There are no jokes.", ephemeral=True)
            person =  self.bot.get_user(joke[0]) or await self.bot.fetch_user(joke[0])
        if not joke: return await interaction.response.send_message("The user you specified has no jokes.", ephemeral=True)
        embed = discord.Embed(title="Joke",color=random.choice(self.bot.colorList),description=f"\"{joke[1]}\"")
        if hasattr(user, "avatar"): embed.set_thumbnail(url=user.avatar.url)
        else: embed.set_thumbnail(url=person.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        embed.add_field(name="Author",value=user or person)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="spam", description="Sends one message repeatedly up to 20 times! It has a pretty high cooldown though...")
    @app_commands.describe(amount="How Much I Should Spam", content="The Content I Should Spam")
    async def spam(self, interaction: discord.Interaction, amount : app_commands.Range[int, 1, 20], content: str):
        try:
            await interaction.response.send_message("Starting spamming...", ephemeral=True)
            for number in range(amount):
                await interaction.followup.send(content + f"           ({number-1} messages left)")
                try:
                    msg = await self.bot.wait_for("message", check=lambda msg: msg.author == interaction.user and msg.channel == interaction.channel, timeout= 0.5)
                    if msg.content in ("stop", "s", "end", "e", "quit", "q"):
                        number=0
                        await interaction.followup.send("Stopped spamming")
                except TimeoutError: pass
        except discord.errors.HTTPException:
            await interaction.followup.send("Please shorten your message a bit.")
    
    @app_commands.command(name="meme",description="Sends a meme.")
    @app_commands.guilds(921230858311057418)
    @app_commands.describe(category="The Category to Search In")
    @app_commands.choices(category=[
        Choice(name="Hot", value="hot"),
        Choice(name="New", value="new"),
        Choice(name="Top", value="top"),
        Choice(name="Rising", value="rising"),
    ])
    async def meme(self,interaction: discord.Interaction, category: Choice[str] = None):         
        async with ClientSession() as cs:
            async with cs.get(f'https://www.reddit.com/r/memes/new.json?sort={category.value if category else "hot"}') as r: res = await r.json()
        meme = res["data"]["children"][random.randint(0,10)]["data"]
        embed = discord.Embed(title=meme["title"], description=meme["author"],color=random.choice(self.bot.colorList))      
        
        embed.set_image(url=meme['url'])
        embed.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(Slash_Fun(client))
