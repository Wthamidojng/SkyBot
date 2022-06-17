from typing import Union
import discord
from discord.ext import commands
from random import randint, choice
from asyncio import TimeoutError

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot
        self.message_cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)

    
    async def role(self, role : str, guild):
        async with self.bot.db.execute(f"SELECT {role} FROM guild WHERE guild = ?",(guild,)) as cur: roleid = await cur.fetchone()
        role = self.bot.get_guild(guild).get_role(roleid[0])
        return role
    
    async def power(self,user):
        await self.bot.wait_until_ready()
        async with self.bot.db.execute("SELECT guild FROM guild WhERE scGuild = 1;") as cur: guilds = await cur.fetchall()
        for r in guilds:
            guild = self.bot.get_guild(r[0])
            person = guild.get_member(user.id)
            leadership = discord.utils.get(guild.roles, name="Leadership_Roles") or await self.role("lsRole",guild)
            if leadership in person.roles: return True
        return False

    async def userSetup(self, user):
        try: 
            await self.bot.db.execute("INSERT INTO members (memberID) VALUES (?);", (user.id),)
            await self.bot.db.commit()
        except Exception: pass

    async def multi(self,guild):
        async with self.bot.db.execute("SELECT xpMulti FROM guild WHERE guild = ?;",(guild,)) as cur: xp = await cur.fetchone()
        return int(xp[0])

    async def levelUp(self,user,ctx):
        async with self.bot.db.execute("SELECT * FROM members WHERE memberID = ?;",(user,)) as cur: level = await cur.fetchone() 
        if level[2] <= level[3] ** 0.25: 
            scb = randint((level[2])*2,((level[2])*3))
            async with self.bot.db.execute("SELECT level FROM members WHERE memberID = ?;",(user,)) as cur: lvl = await cur.fetchone()
            await self.bot.db.execute("UPDATE members SET level = level + 1, scb = scb + ?, xp = xp - ? WHERE memberID = ?;",(scb,lvl[0]**4,user))
            embed = discord.Embed(title=":arrow_up: Level Up :arrow_up:",color=0x2b6a0a)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            embed.add_field(name="Level",value=level[2]+1)
            embed.add_field(name="Skybucks Gained",value=scb)
            await ctx.channel.send(embed=embed)
            await self.bot.db.commit()
            return True
        return False

    async def sc(self,guild):
        async with self.bot.db.execute("SELECT scGuild FROM guild WHERE guild = ?;",(guild,)) as cur: scguild = await cur.fetchone()
        if not scguild: return False

        if scguild[0] == 1: return True
        else: return False

    @commands.command(name="rank",description="View your level and XP!",aliases=["lvl"])
    async def rank(self, ctx, user: Union[discord.Member, discord.User, int] = None):
        user = self.bot.check_id(user) or ctx.author
        await self.userSetup(user)
        await self.levelUp(ctx.author.id,ctx)
        async with self.bot.db.execute("SELECT level, xp FROM members WHERE memberID = ?;",(user.id,)) as cur: level = await cur.fetchone()
        embed = discord.Embed(title="Rank",color=0x00703C)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        embed.add_field(name="User",value=user,inline=False)
        embed.add_field(name="XP",value=f"{level[1]}/{level[0]**4}",inline=True)
        embed.add_field(name="Level",value=level[0])
        await ctx.send(embed=embed)

    async def banned_words(self, message):
        return
        if not message.guild: return
        async with self.bot.db.execute("SELECT * FROM bannedWords WHERE guild = ?;",(message.guild.id,)) as cur: bannedWords = await cur.fetchall()
        if bannedWords and not message.content.startswith("!") and message.author.id != self.bot.user.id and "https://" not in message.content:
            for word in bannedWords:
                for i in [message.content, message.content.lower(), message.content.replace(" ", ""), message.content.lower().replace(" ", "")]:
                    if word[0] in i:
                        await message.delete()
                        return await message.channel.send(f"{message.author.mention}, don't say that!")
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild: return
        
        # Banned Words
        await self.banned_words(message=message)

        # Leveling
        if not message.author.bot and not self.message_cooldown.update_rate_limit(message) and await self.sc(message.guild.id): 
            await self.userSetup(message.author)
            multi = await self.multi(message.guild.id)
            await self.bot.db.execute("UPDATE members SET xp = xp + ? WHERE memberID = ?;",((randint(1,5)*multi),message.author.id)) 
            await self.levelUp(message.author.id,message)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, message):
            await self.banned_words(message=message)

    @commands.command(name="leaderboard",description="View the top rankings of people",aliases=["lb"])
    async def leaderboard(self, ctx):
        async with self.bot.db.execute("SELECT * FROM members ORDER BY level DESC, xp DESC;") as cur: r = await cur.fetchall()
        embed = discord.Embed(title="Leaderboard",color=choice(self.bot.colorList))
        rank = 0
        for row in r: 
            try: 
                await self.levelUp(row[0],ctx)
                user = self.bot.get_user(int(row[0])) or await self.bot.fetch_user(int(row[0]))
                if row[2] != 0 and not user.bot: 
                    place = None
                    rank+=1
                    if rank == 1: place = ":first_place:"
                    elif rank == 2: place = ":second_place:"
                    elif rank == 3: place = ":third_place:"
                    strrank = f"{rank}."

                    embed.add_field(name=f"**{place or strrank}** {user}",value=f"**Level:** {row[2]} | **XP:** {row[3]}/{row[2]**4}",inline=False)
                if user.bot: await self.bot.db.execute("DELETE FROM members WHERE memberID = ?;",(row[0]))
            except Exception: pass
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        mesg = await ctx.send(embed=embed)
        await mesg.add_reaction("❌")
        await self.bot.db.execute("DELETE FROM members WHERE level = 0 AND xp = 0 and scb = 0;")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "❌"

        try: reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except TimeoutError: await mesg.clear_reactions()
        else: await mesg.delete()
    
    @commands.command(name="multi",description="sets the multiplier for xp")
    async def multiplier(self,ctx,multi = None):
        if multi is None: return await ctx.send(f"The multi is currently `{await self.multi(ctx.guild.id)}`.")
        if int(multi) > 10: return await ctx.send("The maximum multi is `10`.")
        admin = discord.utils.get(ctx.guild.roles,name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author):
            await self.bot.db.execute("UPDATE guild SET xpMulti = ? WHERE guild = ?;",(int(multi),ctx.guild.id))
            return await ctx.send(f":white_check_mark: Set the multi to **{multi}**")
        else: await ctx.reply(f"{ctx.author.mention}, you need better permissions!")
    
    @commands.command(name="setxp", description="Sets the XP of a user", aliases=["setexp", "sxp", "sp", "sx"])
    async def setxp(self, ctx, user: Union[discord.Member, discord.User, int    ] = None, xp: int = None):
        if user:
            user = self.bot.check_id(user)
        admin = discord.utils.get(ctx.guild.roles,name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author):
            await self.bot.db.execute("UPDATE members SET xp = ? WHERE memberID = ?;", (xp, user.id))
            return await ctx.send(f":white_check_mark: Set {user.display_name}'s xp to **{xp}**")
        else:
            await ctx.reply(f"{ctx.author.mention}, you need better permissions!")

    @commands.command(name="setlevel", description="sets the level of a user", aliases=["setlvl", "slvl", "sl"])
    async def setlevel(self, ctx, user: Union[discord.Member, discord.User, int] = None, lvl: int = None):
        if user:
            user = self.bot.check_id(user)
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_roles") or await self.role("lsRole", ctx.guild.id)
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author):
            await self.bot.db.execute("UPDATE members SET level = ? WHERE memberID = ?;", (lvl, user.id))
            return await ctx.send(f":white_check_mark: Set {user.display_name}'s level to **{lvl}**")
        else:
            await ctx.reply(f"{ctx.author.mention}, you need better permissions!")
    
    
async def setup(client):
    await client.add_cog(Level(client))
