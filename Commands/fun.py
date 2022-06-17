from cgitb import text
from dataclasses import field
from typing import Union
import aiohttp
from discord.ext import commands
import discord
import random
from random import choice
from asyncio import sleep
from aiohttp import ClientSession
from asyncio import TimeoutError
from discord import ui
from aiohttp import ClientSession

class Confirm(ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=10)
        self.value = None
        self.user = user

    @ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        await interaction.response.send_message("Confirmed!", ephemeral=True)
        self.value = True
        self.stop()
    
    @ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: ui.Button):
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
    async def rock(self, interaction: discord.Interaction, button: ui.Button):
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
        if self.user1choice and self.user2.bot:
            try:await self.stop()
            except:pass

    
    @ui.button(emoji="📜", style=discord.ButtonStyle.blurple)
    async def paper(self, interaction: discord.Interaction, button: ui.Button):
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
        if self.user1choice and self.user2.bot:
            try:await self.stop()
            except:pass
    
    @ui.button(emoji="✂️", style=discord.ButtonStyle.blurple)
    async def scissors(self, interaction: discord.Interaction, button: ui.Button):
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
        if self.user1choice and self.user2.bot:
            try:await self.stop()
            except:pass

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot        

    @commands.command(name = "echo", description = "Copies your message", aliases = ["cc","copycat","me", "mimic", "quote"])
    async def echo(self, ctx, *, args):
        await ctx.send(f' {args} **-{ctx.author}**')


    @commands.command(name = "choose", description = "Chooses a random choice. Separate choices using spaces or commas.", aliases = ["randomchoice", "rc", "choice"])
    async def choose(self, ctx, *, choices):
        if choices.__contains__(','): m = ','
        else: m = ' '
        e = choices.split(m)
        if len(e) == 1: raise commands.errors.UserInputError
        msg = await ctx.send(":drum: I choose... :drum:")
        await sleep(2)
        await msg.edit(content=f":tada: I chose `{choice(e).strip()}`!")


    @commands.command(name = "yomama", description = "Sends a Yo Mama joke!", aliases = ["ym", "yopapa"])
    async def yomama(self, ctx, *, user: Union[discord.User, discord.Member, int] = None):
        if not user:
            user = ctx.author
        else:
            user = self.bot.check_id(user)
        
        async with ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get("https://api.yomomma.info/") as res:
                res = await res.json()

        joke = res["joke"]
        await ctx.send(f"{user.mention} {joke}")
    
    @commands.command(name = "8ball", description = "Try your hand at the magic 8ball!")
    async def eightBall(self, ctx, *, question="Do you have a question"):
        response = choice(["It is certain.", "Without a doubt.", "You may rely on it.", "Yes, definitely.", "It is decidedly so.", "As I see it, yes.", "Most likely.", "Yes.", "Outlook good.", "Signs point to yes.", "Reply hazy try again.", "Better not tell you now.", "Ask again later.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "Outlook not so good.", "My sources say no.", "Very doubtful.", "My reply is no."])
        msg = await ctx.reply("https://tenor.com/view/8ball-bart-simpson-shaking-shake-magic-ball-gif-17725278")
        embed = discord.Embed(title=response, color=choice(self.bot.colorList))
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.add_field(name="Question", value=question + "?")
        embed.add_field(name="Result", value=response, inline=False)
        embed.set_thumbnail(url="https://i.imgflip.com/4/1c8tfl.jpg")
        await sleep(1)
        await msg.edit(content=None, embed=embed)

    #dice roll(badly coded by darkfang), no idea if it works
    @commands.command(name = "rolldice", description = "Rolls a dice (or sometimes many more...)", aliases = ["rd", "roll"])
    async def rolldice(self, ctx, diceAmt=1, faces=6, addamt=0):
        if faces<32767 and diceAmt<32767 and addamt<32767:
            rollresult=[random.randint(1, faces) for _ in range(diceAmt)]
            rollresult=sum(rollresult)+addamt
            msg = await ctx.send("https://tenor.com/view/quiddie-hjrpg-roll-dice-dnd-gif-13900378")
            em = discord.Embed(title = "Roll Dice",color=0x398564)
            em.add_field(name = "Rolled number", value = f"{ctx.author.mention} rolled a {rollresult}!", inline=False)
            em.add_field(name = "Dice Amount", value = diceAmt, inline=True)
            em.add_field(name = "Sides", value = faces, inline=True)
            em.add_field(name = "Added Amount", value=addamt, inline=True)
            em.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            em.set_thumbnail(url=ctx.author.avatar.url)
            await sleep(3)
            await msg.edit(content=None, embed=em)
        else:
            await ctx.reply ("Are you trying to break the bot?")
        
    #coin flip, flips a coin
    @commands.command(name = "coinflip", description = "Flips a coin (please don't bet skybucks with this)", aliases = ["cf", "flipcoin"])
    async def coinflip(self, ctx):
        flipresult = random.choice(['heads', 'tails'])
        imgurls = {"heads":"http://www.clker.com/cliparts/7/d/e/0/139362185558690588heads-md.png", "tails": "https://cdn.discordapp.com/attachments/921230858311057421/933363312022945842/iu.png"}
        msg = await ctx.reply("https://tenor.com/view/coin-flip-quarter-gif-9665789")
        em = discord.Embed(title = "Coin Flip", color=choice(self.bot.colorList))
        em.add_field(name=f"{ctx.author}'s flip", value= f"{ctx.author.mention} flipped {flipresult}!", inline=False)
        em.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        em.set_thumbnail(url=imgurls[flipresult])
        await sleep(2.5)
        await msg.edit(content=None, embed=em)

    @commands.command(name = "numbergame", description = "Can you guess the number?", aliases = ["ng", "guess","guessinggame"])
    async def numbergame(self, ctx, maxval=100):
      mystnum=random.randint(1,maxval)
      print(mystnum)
      guess='-1'
      gc=0
      players={}
      
      async with self.bot.db.execute("SELECT * FROM numgameChannels;") as cur: channels = await cur.fetchall()

      if ctx.channel.id in [i[0] for i in channels]:
          return await ctx.send("Sorry, a Number Game is already running inside this channel")

      em = discord.Embed(title = "Number Game Start", color=discord.Color.blue())
      em.add_field(name = "Type a number in the chat", value = f"Guess the between **1** and **{maxval}**", inline=False)
      em.set_footer(text = f"You have 10 seconds to respond")
      em.set_thumbnail(url=ctx.author.avatar.url)
      await ctx.send(embed=em)
      await self.bot.db.execute("INSERT INTO numgameChannels (channelID) VALUES (?);", (ctx.channel.id))
      async def gamei():
        nonlocal guess
        nonlocal players
        try:
          msg = await self.bot.wait_for("message", check=lambda msg: msg.channel == ctx.channel, timeout= 10)
          if (msg.content).isnumeric() and maxval>=int(msg.content):
            guess=int(msg.content)
            if str(msg.author) not in players:
                  players[str(msg.author)]=1
            else:
                players[str(msg.author)]=(players[str(msg.author)]+1)
            if (guess) > mystnum:
                em = discord.Embed(title = "Try Again", color=discord.Color.red())
                em.add_field(name=f"{ctx.author.display_name} Your number was too *high* try guessing *lower*", value = f"waiting for a response", inline=False)
                em.set_thumbnail(url='http://www.clipartbest.com/cliparts/KTj/Xyg/KTjXyg7Tq.jpeg')
                await ctx.send(embed=em)
                await gamei()
            elif (guess) < mystnum:
                em = discord.Embed(title = "Try Again", color=discord.Color.red())
                em.add_field(name=f"{ctx.author.display_name} Your number was too *low* try guessing *higher*", value = f"waiting for a response", inline=False)
                em.set_thumbnail(url='http://www.clipartbest.com/cliparts/aTq/Eoz/aTqEoznTM.png')
                await ctx.send(embed=em)
                await gamei()
            else: 
              await self.bot.db.execute("DELETE FROM numgameChannels WHERE channelID = ?;", (ctx.channel.id))
              em = discord.Embed(title = "Number Game Results", color=discord.Color.green())
              em.add_field(name = "Winner!", value = f"{msg.author.mention} guessed the number in {players[str(msg.author)]} guesses", inline=False)
              em.set_footer(text = f"The number was {mystnum}")
              em.set_thumbnail(url=ctx.author.avatar.url)
              finalplayers=list(players.keys())
              guesses=list(players.values())
              finalfinal=""
              for i in range (0,len(finalplayers)):
                finalfinal=finalfinal+str(finalplayers[i])+': '+str(guesses[i])+'\n'
              em.add_field(name='Players:', value=finalfinal)
              await ctx.send(embed=em)
          elif (msg.content in ('end', 'e', 'quit', 'stop', 'q', 'quit') and ctx.author==msg.author):
                await ctx.send('Game ended')
                await self.bot.db.execute("DELETE FROM numgameChannels WHERE channelID = ?;", (ctx.channel.id))
                pass
          else:
            await gamei()
        except TimeoutError:
          await ctx.send (f"No one responded in time- the number was **{mystnum}**")
      await gamei()

    @commands.command(name = "sendembed", description = "Sends an embed of your desire!", aliases = ["se", "embed"])
    async def sendembed(self, ctx):
        em = discord.Embed(title = "A Title", color=choice(self.bot.colorList), description="A Description")
        await ctx.reply("What's the title of the embed? Enter `quit` at any point to quit the process.")

        def c(m):
            return m.author == ctx.author and m.channel == ctx.channel

        newTitle = await self.bot.wait_for("message", check=c)
        if newTitle.content == "quit": return await ctx.send("You have quit the process.")

        await ctx.send(f"{ctx.author.mention} What's the description of the embed?")
        newDesc = await self.bot.wait_for("message", check=c)
        if newDesc.content == "quit": return await ctx.send("You have quit the process.")

        await ctx.send(f"{ctx.author.mention} What's the footer of the embed?")
        newFooter = await self.bot.wait_for("message", check=c)
        if newFooter.content == "quit": return await ctx.send("You have quit the process.")

        em = discord.Embed(title = newTitle.content, description = newDesc.content, color=choice(self.bot.colorList))
        em.set_footer(text=newFooter.content, icon_url=ctx.author.avatar.url)
        deletecount = 9

        await ctx.send(f'{ctx.author.mention} How many fields do you want')
        fieldnum = await self.bot.wait_for("message", check=c)
        if newTitle.content == "quit": return await ctx.send("You have quit the process.")
        if not fieldnum.content.isnumeric(): return await ctx.reply("Thats not a valid number.")
        if int(fieldnum.content) > 10: return await ctx.reply("Please use a smaller number under 10.")

        for i in range (0, int(fieldnum.content)):
            await ctx.send(f"{ctx.author.mention} What's the title for field {i + 1}?")
            title = await self.bot.wait_for("message", check=c)
            if newTitle.content == "quit": return await ctx.send("You have quit the process.")

            await ctx.send(f"{ctx.author.mention} What's the description for field {i + 1}")
            desc = await self.bot.wait_for("message", check=c)
            if newTitle.content == "quit": return await ctx.send("You have quit the process.")

            await ctx.send(f"{ctx.author.mention} Do you want field {i + 1} to be inline? (T)rue or (F)alse")
            inline = await self.bot.wait_for("message", check=c)
            if newTitle.content == "quit": return await ctx.send("You have quit the process.")

            if str(inline.content).lower() in ('true', 't', 'yes', 'y'): inline=True
            elif str(inline.content).lower() in ('false', 'f', 'no', 'no'): inline=False
            else: break

            em.add_field(name = (title.content), value = (desc.content), inline=bool(inline))
            deletecount+=6
        await ctx.message.channel.purge(limit=deletecount, check=lambda c: c.author == ctx.author or c.author == self.bot.user and not c.content.startswith("!sendembed"))
        await ctx.send(embed=em)

        
    @commands.command(name = "actlike", description = "Impersonate your friends, or even enemies!", aliases = ["al","impersonate"])
    async def actlike(self, ctx, user: Union[discord.Member, discord.User, int] = None,  *, content="Hi!"):
        if user:
            user = self.bot.check_id(user)
        webhook = await ctx.channel.create_webhook(name=user.nick or user.name, avatar=await user.avatar.read())
        await ctx.message.delete()
        await webhook.send(content)
        await webhook.delete()

    @commands.command(name = "rockpaperscissors", description = "Play rock paper scissors! If you're feeling lonely, you can play against the bot!", aliases = ["rps", "rockpaperscissor"])
    async def rockpaperscissors(self, ctx: commands.Context, user: discord.User = None):
        if ctx.author == user: return await ctx.reply("You can't play against yourself...")
        if user: 
            if user.bot:
                if user == self.bot.user:
                    user = None
                else: return await ctx.send("You can't play against a bot...")
        user1content, user2content = None, None
        if not user:
            choices = ['Rock', 'Paper', 'Scissors']
            user2content = choice(choices)
            view = RPSGame([ctx.author, self.bot.user])
            msg = await ctx.send(f"{ctx.author.mention} Choose Rock, Paper, or Scissors", view=view)
            await view.wait()
            for i in view.children:
                i.disabled = True
            await msg.edit(view=view)
            if not view.user1choice: return await ctx.send(f"{ctx.author.mention} please choose Rock, Paper, or Scissors. Automatically cancelled the game.")
            user1content = view.user1choice
        else:
            view = Confirm(user=user)
            msg = await ctx.send(f"{user.mention} Do you want to play Rock Paper Scissors with {ctx.author.mention}?", view=view)
            await view.wait()
            for i in view.children:
                i.disabled = True
            await msg.edit(view=view)
            if view.value == None:
                return await ctx.send(f"No response from {user.mention}. Automatically cancelled the game.")
            elif not view.value:
                return await ctx.send(f"{ctx.author.mention} did not want to play. Cancelling the game.")
            else:
                view = RPSGame([ctx.author, user])
                await ctx.send(f"{ctx.author.mention} {user.mention} Choose Rock (:rock:), Paper (:scroll:), or Scissors (:scissors:)", view=view)
                await view.wait()
                if not view.user1choice: return await ctx.send(f"{ctx.author.mention} did not choose Rock, Paper, or Scissors. Cancelled the game.")
                if not view.user2choice: return await ctx.send(f"{user.mention} did not choose Rock, Paper, or Scissors. Cancelled the game.")
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
                embed.title = f"{ctx.author.display_name} Wins!"
                embed.set_thumbnail(url=ctx.author.avatar.url)
            else:
                return await ctx.send(f"{user.mention} Please choose Rock, Paper, or Scissors")
        elif user1content.lower() in ("p", "paper"):
            if user2content.lower() in ('r', "rock"):
                embed.title = f"{ctx.author.display_name} Wins!"
                embed.set_thumbnail(url=ctx.author.avatar.url)
            elif user2content.lower() in ('p', "paper"):
                embed.title = "Draw!"
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            elif user2content.lower() in ('s', "scissors"):
                embed.title = f"{user.display_name if user else self.bot.user.display_name} Wins!"
                embed.set_thumbnail(url=user.avatar.url if user else self.bot.user.avatar.url)
            else:
                return await ctx.send(f"{user.mention} Please choose Rock, Paper, or Scissors")
        elif user1content.lower() in ("s", "scissors"):
            if user2content.lower() in ('r', "rock"):
                embed.title = f"{user.display_name if user else self.bot.user.display_name} Wins!"
                embed.set_thumbnail(url=user.avatar.url)
            elif user2content.lower() in ('p', "paper"):
                embed.title = f"{ctx.author.display_name} Wins!"
                embed.set_thumbnail(url=ctx.author.avatar.url)
            elif user2content.lower() in ('s', "scissors"):
                embed.title = "Draw!"
                embed.set_thumbnail(url=self.bot.user.avatar.url)
            else:
                return await ctx.send(f"{user.mention} Please choose Rock, Paper, or Scissors.")
        else:
            return await ctx.send(f"{ctx.author.mention} Please choose Rock, Paper, or Scissors.")
        embed.add_field(name=f"{ctx.author.display_name}'s Choice", value=user1content)
        embed.add_field(name=f"{user.display_name if user else self.bot.user.display_name}'s Choice", value=user2content)
        await ctx.send(embed=embed)

    @commands.command(name="addjoke",description="Add a joke to the list of jokes!",aliases=["createjoke","makejoke"])
    async def addjoke(self, ctx, *, joke : str):
        async with self.bot.db.execute("SELECT * FROM jokes WHERE joke = ?;",(joke,)) as cur: jokes = await cur.fetchone()
        if jokes: return await ctx.reply("That joke already exists.")
        await self.bot.db.execute("INSERT INTO jokes VALUES (?,?);",(int(ctx.author.id),joke))
        embed = discord.Embed(title="Added Joke :thumbsup:",color=0x5ac18e)
        embed.add_field(name="Joke",value=joke)
        embed.add_field(name="Author",value=ctx.author.mention)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.reply(embed=embed)
        await self.bot.db.commit()

    @commands.command(name="joke",description="choose a random joke from the list of jokes",aliases=["sayjoke"])
    async def joke(self, ctx, user : Union[discord.Member, int] = None):
        if user != None:
            user = self.bot.check_id(user)
            async with self.bot.db.execute("SELECT * FROM jokes WHERE id = ? ORDER BY RANDOM() LIMIT 1;",(user.id,)) as cur: joke = await cur.fetchone()
            person = None
        else:
            async with self.bot.db.execute("SELECT * FROM jokes ORDER BY RANDOM() LIMIT 1;") as cur: joke = await cur.fetchone()
            if not joke: return await ctx.send("The user you specified has no jokes.")
            person =  self.bot.get_user(joke[0]) or await self.bot.fetch_user(joke[0])
        if not joke: return await ctx.reply("The user you specified has no jokes.")
        embed = discord.Embed(title="Joke",color=random.choice(self.bot.colorList),description=f"\"{joke[1]}\"")
        if hasattr(user, "avatar"): embed.set_thumbnail(url=user.avatar.url)
        else: embed.set_thumbnail(url=person.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        embed.add_field(name="Author",value=user or person)
        await ctx.reply(embed=embed)

    @commands.command(name="spam", description="Sends one message repeatedly up to 20 times! It has a pretty high cooldown though...", aliases=["sapm"])
    @commands.cooldown(1, 7200.0, commands.BucketType.user)
    async def spam(self, ctx, number : str = None, *, msg : str = None):
        try:
            if ((not number.isnumeric()) or (int(number)>20)): return await ctx.send("You must enter a valid number less than 20")
            if msg == None or len(msg) == 0:
                return await ctx.reply("Please enter something for me to spam.")
            number = int(number)
            if type(number) != int: number = int(number)
            while number > 0:
                await ctx.send(msg + f"           ({number-1} messages left)")
                number -= 1
                try:
                    if type(number) != int: number = int(number)
                    mesg = await self.bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel, timeout= 0.5)
                    if mesg.content in ("stop", "s", "end", "e", "quit", "q"):
                        number=0
                        await ctx.send("Stopped spamming")
                except TimeoutError: pass
        except discord.errors.HTTPException:
            await ctx.send("Please shorten your message a bit.")
    
    @commands.command(name="meme",description="Sends a meme.")
    async def meme(self,ctx,*,category="hot"):      
        async with ClientSession() as cs:
            async with cs.get(f'https://www.reddit.com/r/memes/new.json?sort={category}') as r: res = await r.json()
        meme = res["data"]["children"][random.randint(0,10)]["data"]
        embed = discord.Embed(title=meme["title"], description=meme["author"],color=random.choice(self.bot.colorList))      
        
        embed.set_image(url=meme['url'])
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self,msg: discord.Message):
        if not msg.guild: return
        async with self.bot.db.execute("SELECT counterChnl, countedNum, highestNum, counterAuthor FROM guild WHERE guild = ?;",(msg.guild.id,)) as cur: channel = await cur.fetchone()
        if type(channel) == type(None): return
        if msg.channel.id != channel[0]: return
        if msg.content.isnumeric():
            if int(msg.content) == (channel[1] + 1) and msg.author.id != channel[3]:
                await self.bot.db.execute("UPDATE guild SET countedNum = countedNum + 1 WHERE guild = ?;",(msg.guild.id))
                await self.bot.db.execute("UPDATE guild SET counterAuthor = ? WHERE guild = ?;",(msg.author.id,msg.guild.id))
                
                if int(msg.content) > channel[2]: await self.bot.db.execute("UPDATE guild SET highestNum = highestNum + 1 WHERE guild = ?;",(msg.guild.id,))
                await msg.add_reaction("\u2705")
            else:
                await msg.delete()
    
    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        if not msg.guild: return
        async with self.bot.db.execute("SELECT counterChnl, countedNum, highestNum, counterAuthor FROM guild WHERE guild = ?;",(msg.guild.id)) as cur: channel = await cur.fetchone()
        if type(channel) == (type(None) or type(discord.DMChannel)): return
        if msg.channel.id != channel[0]: return
        if msg.content.isnumeric():
            if int(msg.content) == channel[1] and msg.author.id != channel[3]:

                await msg.channel.send()


async def setup(client):
    await client.add_cog(Fun(client))
