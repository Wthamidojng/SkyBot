from random import choice
import discord
from discord.ext import commands

class Guild(commands.Cog):
    def __init__(self,bot): #guild INT PRIMARY KEY, lsRole INT, counterChnl INT, unverified INT, prefix TEXT DEFAULT \"!\", scGuild INT, countedNum INT DEFAULT 0, xpMulti DEFAULT 1
        self.bot : commands.Bot = bot
    
    async def role(self, role, guild):
        async with self.bot.db.execute(f"SELECT {role} FROM guild WHERE guild = ?;",(guild,)) as cur: roleid = await cur.fetchone()
        role = self.bot.get_guild(guild).get_role(roleid[0])
        return role

    async def power(self,user):
        await self.bot.wait_until_ready()
        async with self.bot.db.execute("SELECT guild FROM guild WhERE scGuild = 1;") as cur: guilds = await cur.fetchall()
        for r in guilds:
            guild = self.bot.get_guild(r[0])
            leadership = discord.utils.get(guild.roles, name="Leadership_Roles") or await self.role("lsRole",guild)
            if leadership in user.roles: return True
        return False

    @commands.command(name="set",description="Set a specific item to your choice. The current items are leadership roles, counting channel, unverified role, prefix, and whether it is an official skyclan guild or not.")
    async def set(self, ctx, *, item):
        await ctx.send("Type what to set it to. (if it is True/False True is 1 and False is 0)")
        to = await self.bot.wait_for("message",check = lambda msg: msg.channel == ctx.channel and msg.author == ctx.author)
        if item.lower() in ["leadership role","lsrole","leadership","leadershiprole","leadership roles"]: column = "lsRole"
        elif item.lower() in ["counterchnl","counting channel","countingchannel","countrchannel"]: column = "counterChnl"
        elif item.lower() in ["unverified","unverified role","unverifiedrole"]: column = "unverified"
        elif item.lower() in ["prefix","official prefix"]: column = "prefix"
        elif item.lower() in ["ads", "ad", "postads"]: column = "ads"
        elif item.lower() in ["skyclan guild","skyclanguild","sky clan guild","scguild","sc guild","osd"]: column = "scGuild" 
        else: return await ctx.send("The options are `lsRole` `counterChnl` `unverified` `prefix` `ads` or `scGuild`")
        
        if column == "scGuild" and not (await self.power(ctx.author) or await self.role("lsRole", ctx.guild.id)):
          return await ctx.send(f"{ctx.author.mention}, you don't have the permissions for that.")

        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(f"{ctx.author.mention}, you need administrator to perform this action.")
            
        await self.bot.db.execute(f"UPDATE guild SET {column} = ? WHERE guild = ?;",(to.content,ctx.guild.id))
        embed = discord.Embed(title=f"Set {column} to `{to.content if not to.content.isnumeric and not len(to.content) == 1 else bool(to.content)}`", color=choice(self.bot.colorList))
        embed.set_thumbnail(url=ctx.guild.icon.url)
        async with self.bot.db.execute("SELECT * FROM guild WHERE guild = ?", (ctx.guild.id)) as cur: items = await cur.fetchall()
        for i in items:
            for r in i:
                print(r)
        embed.add_field(name=column, value=to.content if not to.content.isnumeric and not len(to.content) == 1 else bool(to.content))
        return await ctx.send(embed=embed)




    @commands.command(name="serversetup",description="Sets up the server! This command should be run first",aliases=["ssetup","setup"])
    async def ssetup(self, ctx):
        await ctx.send("This will reset all your current data. However, you can type `None` if you would not like to change the defaults. Mention the correct role/channel after each message!")
        try: await self.bot.db.execute("INSERT INTO guild (guild) VALUES (?);",(ctx.guild.id,))
        except Exception: pass

        await ctx.send("Leadership Role")
        msg = await self.bot.wait_for("message",check = lambda msg: msg.channel == ctx.channel and msg.author == ctx.author)
        item = await commands.RoleConverter().convert(ctx, msg.content)
        if not "none" in msg.content.lower(): await self.bot.db.execute("UPDATE guild SET lsRole = ? WHERE guild = ?;",(item.id,ctx.guild.id))

        await ctx.send("Counting Channel")
        msg = await self.bot.wait_for("message",check = lambda msg: msg.channel == ctx.channel and msg.author == ctx.author)
        item = await commands.TextChannelConverter().convert(ctx, msg.content)
        if not "none" in msg.content.lower(): await self.bot.db.execute("UPDATE guild SET counterChnl = ? WHERE guild = ?;",(item.id,ctx.guild.id))

        await ctx.send("Unverified Role")
        msg = await self.bot.wait_for("message",check = lambda msg: msg.channel == ctx.channel and msg.author == ctx.author)
        item = await commands.RoleConverter().convert(ctx, msg.content)
        if not "none" in msg.content.lower(): await self.bot.db.execute("UPDATE guild SET unverified = ? WHERE guild = ?;",(item.id,ctx.guild.id))

        await ctx.send("Prefix")
        msg = await self.bot.wait_for("message",check = lambda msg: msg.channel == ctx.channel and msg.author == ctx.author)
        if not "none" in msg.content.lower(): await self.bot.db.execute("UPDATE guild SET prefix = ? WHERE guild = ?;",(msg.content,ctx.guild.id))

        await ctx.send("Ads (1 for True, 0 for False)")
        msg = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
        if not "none" in msg.content.lower(): await self.bot.db.execute("UPDATE guild SET ads = ? WHERE guild = ?;",(int(msg.content), ctx.guild.id)) 

        async with self.bot.db.execute("SELECT lsRole, counterChnl, unverified, prefix, ads FROM guild WHERE guild = ?;",(ctx.guild.id,)) as cur: stuff = await cur.fetchone()
        embed = discord.Embed(title="Server Successfully Set up!",color=0x134E41)
        embed.add_field(name="Leadership Role",value=ctx.guild.get_role(stuff[0]))
        embed.add_field(name="Counting channel",value=ctx.guild.get_channel(stuff[2]))
        embed.add_field(name="Unverified Role",value=ctx.guild.get_role(stuff[3]),inline=False)
        embed.add_field(name="Prefix",value=stuff[3])
        embed.add_field(name="Ads", value=bool(stuff[4]))
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.guild:
            async with self.bot.db.execute("SELECT ads FROM guild WHERE guild = ?;",(ctx.guild.id)) as cur: t = await cur.fetchone()
            if not t: return
            if bool(t):
                pass
            

async def setup(client):
    await client.add_cog(Guild(client))
