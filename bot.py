import asyncio
import traceback
from typing import Union
import aiohttp
import discord
from discord.ext import commands
import asqlite
from sys import stderr
from traceback import print_exception
from asyncio import run, TimeoutError
from random import choice
from discord import app_commands


async def pre(bot,message):
    if not message.guild: return
    async with client.db.execute("SELECT prefix FROM guild WHERE guild = ?;",(message.guild.id,)) as cur: pre = await cur.fetchone() or "!"
    async with client.db.execute("SELECT prefix FROM members WHERE memberID = ?;",(message.author.id)) as cur: 
        userpre = await cur.fetchone()
        if userpre and pre:
            if userpre[0] != "!" and not message.content.startswith(pre[0]):
                pre = userpre
    if not pre: return commands.when_mentioned_or("!")(bot,message)
    return commands.when_mentioned_or(pre[0] or "!")(bot,message)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=pre, help_command=None, case_insensitive=True, intents=discord.Intents.all(), activity=discord.Activity(type=discord.ActivityType.watching, name='LeaF take the L'))
        self.initial_extensions = ["Commands.dev", "Commands.fun", "Commands.guild", "Commands.level", "Commands.logs", "Commands.music", "Commands.skybucks", "Commands.useful", "Commands.utility", "Commands.App_Commands.dev", "Commands.App_Commands.fun", "Commands.App_Commands.guild"]
    
    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)
    
    async def close(self):
        await super().close()
    
    async def on_ready(self):
        print('Bot is Ready')
        await client.tree.sync(guild=discord.Object(id=921230858311057418))


client = MyBot()

async def db():
    client.db = await asqlite.connect("bot.db")
    await client.db.executescript("\
    CREATE TABLE IF NOT EXISTS members (memberID INT PRIMARY KEY, scb INT DEFAULT 0, level INT DEFAULT 0, xp INT DEFAULT 0, story TEXT, prefix TEXT DEFAULT \"!\");\
    CREATE TABLE IF NOT EXISTS shop (itemName TEXT, itemDesc TEXT DEFAULT 0, sellerID INT, price INT DEFAULT 10, itemID INTEGER PRIMARY KEY, inStock INT DEFAULT 0);\
    CREATE TABLE IF NOT EXISTS muted (id INT, guild INT, roles INT, reason TEXT);\
    CREATE TABLE IF NOT EXISTS jokes (id INT, joke TEXT PRIMARY KEY);\
    CREATE TABLE IF NOT EXISTS reaction (msg INT, emoji TEXT, role INT);\
    CREATE TABLE IF NOT EXISTS guild (guild INT PRIMARY KEY, lsRole INT, counterChnl INT, unverified INT, prefix TEXT DEFAULT \"!\", scGuild INT DEFAULT 0, countedNum INT DEFAULT 0, xpMulti DEFAULT 1, highestNum INT DEFAULT 0, counterAuthor INT, ads INT DEFAULT 1);\
    CREATE TABLE IF NOT EXISTS bannedWords (word TEXT, guild INT);\
    CREATE TABLE IF NOT EXISTS tags (name TEXT PRIMARY KEY, desc TEXT, user INT, status INT);\
    CREATE TABLE IF NOT EXISTS ads (title TEXT PRIMARY KEY, desc TEXT, organization TEXT);\
    CREATE TABLE IF NOT EXISTS numgameChannels (channelID int);")
    await client.db.commit()

client.colorList = [0x5d8aa8, 0xf0f8ff, 0xe32636, 0xffbf00, 0x9966cc, 0xa4c639, 0xf2f3f4, 0xcd9575, 0x915c83]

def from_id(id: int):
    try: 
        user = client.get_user(id)
        if type(user) != discord.User:
            raise Exception
        return user
    except: return

def check_id(thing) -> Union[discord.Member, discord.User]:
    if type(thing) == int:
        id = from_id(thing)
        return id
    else: 
        return thing

client.from_id = from_id
client.check_id = check_id

class HelpCMD(commands.HelpCommand):
    def __init__(self):
        self.verify_checks = True
        self.show_hidden = False
        super().__init__()

    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        r = []
        embed = discord.Embed(title="Bot commands", colour=choice(client.colorList))
        description = (
            self.context.bot.description
            + "\n\nTo view help for a specific command, please type `!help [command]`\nTo view help for all categories and commands, please type `!help`"
        )
        if description:
            embed.description = description

        for cog, commands in mapping.items():
            if not cog:
                continue
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                value = ",\t".join(f"`{i.name}`" for i in commands)
                embed.add_field(name = cog.qualified_name, value = value)
        embed.add_field(name = "Uncategorized", value = "`help`, `ping`")
         
        embed.set_footer(text = f"Requested by {self.context.author}", icon_url = self.context.author.avatar.url)
        channel = self.get_destination()
        mesg = await channel.send(embed=embed)
        await mesg.add_reaction("❌")
        try:
            reaction, user = await self.context.bot.wait_for(
                "reaction_add",
                timeout=60.0,
                check=lambda reaction, user: user == self.context.message.author
                and str(reaction.emoji) == "❌",
            )
        except TimeoutError:
            await mesg.clear_reactions()
        else:
            await mesg.delete()

    async def send_command_help(self, command: commands.Command):
        if not await command.can_run(self.context):
            return await (self.get_destination()).send("That Command is not accessible with your current permissions.")
        embed = discord.Embed(title=self.get_command_signature(command), color =    choice(client.colorList))
        desc = str(command.description)
        if len(desc) == 0:
            desc = "No description added"
        embed.add_field(name="Description", value=desc)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        a = "No Category"
        if command.cog:
            a = command.cog.qualified_name
        embed.add_field(name="Category", value=a, inline=False)
        embed.description = "To view help for all categories and commands, please type `!help`\nTo view help for a category, please type `!help [category]`"
        embed.set_footer(text = f"Requested by {self.context.author}", icon_url = self.context.author.avatar.url)
        channel = self.get_destination()
        mesg = await channel.send(embed=embed)
        await mesg.add_reaction("❌")
        try:
            reaction, user = await self.context.bot.wait_for(
                "reaction_add",
                timeout=60.0,
                check=lambda reaction, user: user == self.context.message.author
                and str(reaction.emoji) == "❌",
            )
        except TimeoutError:
            await mesg.clear_reactions()
        else:
            await mesg.delete()

    async def send_error_message(self, error):
        e = self.context.message.content.split(" ")
        a = e[1]
        channel = self.get_destination()
        mesg = await channel.send(
            f"There was no command or category named `'{a}'`. View `!help` in order to look at all commands and categories."
        )

    async def send_cog_help(self, cog: commands.Cog):
        a = []
        for c in cog.get_commands():
            if not (await c.can_run(ctx=self.context)):
                continue
        embed = discord.Embed(title=cog.qualified_name, color = choice(client.colorList))
        embed.add_field(name="Commands", value='`' + '` `'.join(a) + '`')
        embed.description = "To view help for a specific command, please type `!help [command]`\nTo view help for all categories and commands, please type `!help`"
        embed.set_footer(text = f"Requested by {self.context.author}", icon_url = self.context.author.avatar.url)
        channel = self.get_destination()
        mesg = await channel.send(embed=embed)
        await mesg.add_reaction("❌")
        try:
            reaction, user = await self.context.bot.wait_for(
                "reaction_add",
                timeout=60.0,
                check=lambda reaction, user: user == self.context.message.author
                and str(reaction.emoji) == "❌",
            )
        except TimeoutError:
            await mesg.clear_reactions()
        else:
            await mesg.delete()


client.help_command = HelpCMD()


async def role(role, guild):
    async with client.db.execute(
        f"SELECT {role} FROM guild WHERE guild = ?;", (guild,)
    ) as cur:
        roleid = await cur.fetchone()
    role = client.get_guild(guild).get_role(roleid[0])
    return role

@client.event 
async def on_member_join(user : discord.Member):
    if user.id in [897208996824485949]: return await user.ban(delete_message_days=7, reason="ur a trator")
    print(f'{user} has joined the server')
    unvertified = discord.utils.get(user.guild.roles, name="Unverified") or await role("unverified",user.guild)
    await user.add_roles(unvertified)
    chnl = discord.utils.get(user.guild.channels, name="😈⌈unverified-chat⌋")
    embed = discord.Embed(title=f"Hi {user.display_name}!", color=choice(client.colorList), description="Welcome to the Official SkyClan Discord!\n While you wait for your verification, please take this time to read our rules. Failure to abide by the rules will result in a punishment, so make sure you are familiar with the rules.")
    embed.set_footer(text=f"New User: {user.display_name}", icon_url=user.avatar.url)
    await chnl.send(embed=embed)
    msg = await chnl.send("@everyone")
    await msg.delete()


@client.event
async def on_member_remove(user: discord.Member):
    print(f"{user} has left the server")


@client.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'): return
    if ctx.cog: 
        if ctx.cog._get_overridden_method(ctx.cog.cog_command_error): return

    error = getattr(error, 'original', error)

    if isinstance(error, (commands.CommandNotFound,)): return
    elif isinstance(error, commands.MissingPermissions): return await ctx.send(f"You are missing the permission `{error.missing_permissions[0]}`" if len(error.missing_permissions) == 1 else f"You are missing the following permissions: `{', '.join(error.missing_permissions)}`")
    elif isinstance(error, commands.MissingRole): return await ctx.send("You are missing a role.")
    elif isinstance(error, commands.DisabledCommand): return await ctx.send(f'{ctx.command} has been disabled.')
    elif isinstance(error, commands.NoPrivateMessage):
        try: await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except Exception: pass
        return
    if ctx.cog:
        if ctx.cog._get_overridden_method(ctx.cog.cog_command_error):
            return

    error = getattr(error, "original", error)

    if isinstance(error, (commands.CommandNotFound,)):
        return
    elif isinstance(error, commands.MissingPermissions):
        return await ctx.send("You are missing permissions.")
    elif isinstance(error, commands.MissingRole):
        return await ctx.send("You are missing a role.")
    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send(f"{ctx.command} has been disabled.")
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f"{ctx.command} can not be used in Private Messages.")
        except Exception:
            pass
        return
    elif isinstance(error, commands.MessageNotFound):
        return await ctx.send("That message doesn't exist.")
    elif isinstance(error, OverflowError):
        return await ctx.send("That's too big of a number!")
    elif isinstance(error, commands.GuildNotFound):
        return await ctx.send("That guild doesn't exist.")
    elif isinstance(error, commands.UserNotFound):
        return await ctx.send("That user doesn't exist.")
    elif isinstance(error, commands.NoPrivateMessage):
        return await ctx.send("This command cannot be used in `Private Messages`.")
    elif isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(
            f"This command is on cooldown for {int(ctx.command.get_cooldown_retry_after(ctx))} seconds."
        )
    elif isinstance(error, (commands.UserInputError, commands.BadArgument)):
        return await ctx.send_help(ctx.command.qualified_name)
    elif (
        (len(str(ctx.message.embeds)) >= 1 and len(str(ctx.message)) >= 1000)
        or (len(str(ctx.message)) >= 2000 and not ctx.author.premium)
        or len(str(ctx.message)) >= 4000
    ):
        return await ctx.send("That message is too long!")

    msg = await ctx.send("An internal error occurred.")
    print(f"Ignoring exception in command {ctx.command}:", file=stderr)
    print_exception(type(error), error, error.__traceback__, file=stderr)
    exc = traceback.format_exception(type(error), error, error.__traceback__)
    c = ""
    for i in exc:
        c += i
    await msg.add_reaction("❔")
    try: reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: str(reaction.emoji) == "❔" and user != client.user, timeout=60)
    except TimeoutError: return await msg.clear_reactions()
    else: await msg.edit(content=f"```{c}```")

@client.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if hasattr(interaction.command, 'on_error'): return

    error = getattr(error, 'original', error)

    if isinstance(error, app_commands.CommandNotFound): return



@client.command(name="ping", description="Pings the bot to check its latency")
async def ping(ctx):
    await ctx.send(f":ping_pong: Pong! `{client.latency*1000} ms`")


@client.tree.command(name="ping", description="Pings the bot to check its latency", guild=discord.Object(id=921230858311057418))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f':ping_pong: Pong! `{client.latency*1000} ms`')

with open("token.txt","r") as f: token = f.read()

async def main():
    async with client:
        client.loop.create_task(db())
        await client.start(token)

asyncio.run(main())

run(client.db.commit())
run(client.db.close())
