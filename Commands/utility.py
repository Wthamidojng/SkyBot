from datetime import timedelta
import re
from typing import Union
import discord
from discord.ext import commands
from asyncio import sleep
from random import choice

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot
        

    async def userSetup(self, user):
        try: 
            await self.bot.db.execute("INSERT INTO members (memberID) VALUES (?);", (int(user.id),))
            await self.bot.db.commit()
        except Exception: pass

    async def role(self, role, guild):
        async with self.bot.db.execute(f"SELECT {role} FROM guild WHERE guild = ?;",(guild.id,)) as cur: roleId = await cur.fetchone()
        role = discord.utils.get(guild.roles,id=roleId[0])
        return role

    async def power(self,user):
        await self.bot.wait_until_ready()
        async with self.bot.db.execute(f"SELECT guild FROM guild WhERE scGuild = 1;") as cur: guilds = await cur.fetchall()
        for r in guilds:
            guild = self.bot.get_guild(r[0])
            person = guild.get_member(user.id)
            leadership = discord.utils.get(guild.roles, name="Leadership_Roles") or await self.role("lsRole",guild)
            if leadership in person.roles: return True
        return False

    @commands.command(name = "kick", description = "kick members from the server.") 
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user : discord.Member, *, reason = "None was specified"):
        if ctx.author.top_role > user.top_role:
            try: await user.send(f"You got kicked by `{ctx.author}` because `{reason}`")
            except Exception: pass
            await user.kick(reason=reason)
            embed = discord.Embed(name="User Kicked",color=0xf72424)
            embed.add_field(name="User",value=user)
            embed.add_field(name="Kicked By",value=ctx.author.mention)
            embed.add_field(name="Reason",value=reason,inline=False)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else: await ctx.reply(f"{user.mention} has higher permissions than you!")

    @commands.command(name = "ban", description = "bans members from the server.") 
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user : discord.Member, *, reason = "None was specified"):
        if ctx.author.top_role > user.top_role:
            try: await user.send(f"You got banned by `{ctx.author}` because `{reason}`")
            except Exception: pass
            await user.ban(reason=reason)
            embed = discord.Embed(name="User Banned",color=0xf72424)
            embed.add_field(name="User",value=user)
            embed.add_field(name="Banned By",value=ctx.author.mention)
            embed.add_field(name="Reason",value=reason,inline=False)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else: await ctx.reply(f"{user.mention} has higher permissions than you!")

    @commands.command(name = "mute", description = "Mutes people. For length, enter `[number][unit]` (e.g. 10m, 24h, 3d)", aliases=["timeout", "to"])
    @commands.has_guild_permissions(moderate_members=True)
    async def mute(self, ctx, user : discord.Member, length: str = "10m", * ,reason="None was specified"):
        if ctx.author.top_role > user.top_role:
            try:
                time = int("".join(re.findall(re.compile(r"\d"), length)))
                unit = re.findall(re.compile("s|m|h|d|w"), length)[0]
                if unit == "w": time = time * 604800
                elif unit == "d": time = time * 86400
                elif unit == "h": time = time * 3600
                elif unit == "m": time = time * 60
            except:
                return await ctx.send("Please enter a proper mute length (e.g. `74minutes`, `34h`)")
            if time > 2419200:
                return await ctx.send("That is too long of a duration!")
            await user.timeout(timedelta(seconds=time), reason=reason)
            embed = discord.Embed(title="User Muted",color=0xf72424)
            embed.add_field(name="User",value=user)
            embed.add_field(name="Muted By",value=ctx.author.mention)
            embed.add_field(name="Reason",value=reason,inline=False)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else: await ctx.reply(f"{user.mention} has higher permissions than you!")

    @commands.command(name = "unmute", description = "Unmutes people")
    @commands.has_guild_permissions(moderate_members=True)
    async def unmute(self, ctx, user : discord.Member): 
        if ctx.author.top_role > user.top_role:
            await user.timeout(timedelta(seconds=0))
            embed = discord.Embed(title="User Unmuted",color=0x0B646D)
            embed.add_field(name="User",value=user)
            embed.add_field(name="Unmuted By",value=ctx.author.mention)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            try: await user.send(f"You were unmuted by `{ctx.author}`")
            except Exception: pass 
        else: await ctx.reply(f"{user.mention} has higher permissions than you!")
    
    @commands.command(name = "purge", description = "Deletes messages")
    async def purge(self, ctx, amount=1): 
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 667760867483582492:
            channel = ctx.message.channel
            messages = []
            async for message in channel.history(limit=int(amount) + 1): messages.append(message)
            myMsg = await ctx.send(f"Purged `{amount}` messages successfully!")
            await channel.delete_messages(messages)
            await sleep(1)
            await myMsg.delete()
        else: await ctx.send(f"**{ctx.author.mention}**, you need the `Manage Messages` permission for that.")

    @commands.command(name = "setnickname", description = "changes a users nickname", aliases=["setnick", "sn", "nick"])
    async def setnick(self, ctx, user : discord.Member = None, *, nickname = None):
        user = user or ctx.author
        if ctx.author.guild_permissions.manage_nicknames and ctx.author.top_role >= user.top_role:
            nickName = user.nick
            await user.edit(nick=nickname)
            embed = discord.Embed(title="Changed Nickname",color=0x1CAC78)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            embed.add_field(name="New Nickname",value=user.nick)
            embed.add_field(name="Old Nickname",value=nickName or user.name)
            embed.add_field(name="User",value=user.mention,inline=False)
            await ctx.send(embed=embed)
        else: await ctx.send(f"{ctx.author.mention}, you need better perms!")    
    
    @commands.command(name="banword",description="make a word ban or unban a word",aliases=["banwd","bw"])
    async def banword(self,ctx,action, *, word):
        if ctx.author.guild_permissions.administrator:
            if action in ["add","create","append", "a"]: 
                await self.bot.db.execute("INSERT INTO bannedWords VALUES (?,?);",(word,ctx.guild.id))
                await ctx.send(f"Added `{word}` into the Banned Words list.")
            elif action in ["remove","delete","pop", "rm", "r"]: 
                try:
                    if ctx.author.id != 732627312805412884:
                        await self.bot.db.execute("DELETE FROM bannedWords WHERE word = ? AND guild = ?;",(word,ctx.guild.id))
                    await ctx.send(f"Successfully removed `{word}` from banned words")
                except: return await ctx.send("That word doesn't exist.")
            else: return await ctx.send("The options are `add` and `remove`")
        else:
            await ctx.send(f"{ctx.author.mention} Sorry, you need more permissions.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.member.id == self.bot.user.id: return
        async with self.bot.db.execute("SELECT role FROM reaction WHERE msg = ? AND emoji = ?;",(payload.message_id,str(payload.emoji))) as cur: l = await cur.fetchall()
        if not l: return
        for item in l:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(item[0])
            user = guild.get_member(payload.user_id)
            await user.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        async with self.bot.db.execute("SELECT role FROM reaction WHERE msg = ? AND emoji = ?;",(payload.message_id,str(payload.emoji))) as cur: l = await cur.fetchall()
        if not l: return
        for item in l:
            try:
                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(item[0])
                user = guild.get_member(payload.user_id)
                await user.remove_roles(role)
            except: pass

    @commands.command(name="reaction",description="add a new reaction role")
    async def reaction(self,ctx):
        await ctx.send("What is the message ID of the reaction role?")
        message = await self.bot.wait_for("message",check = lambda msg: msg.channel == ctx.channel and msg.author == ctx.author and msg.content.isnumeric())
        
        await ctx.send("The reaction: (React to this message)")
        emoji = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author)

        await ctx.send("The role the user would get:")
        role = await self.bot.wait_for("message",check = lambda msg: msg.channel == ctx.channel and msg.author == ctx.author)
        role = self.bot.check_id(role)        

        await self.bot.db.execute("INSERT INTO reaction VALUES (?,?,?);",(int(message.content),str(emoji[0]),role.id))
        em = discord.Embed(title="Added new reaction role :thumbsup:",color=choice(self.bot.colorList))
        em.add_field(name="Message ID",value=int(message.content))
        em.add_field(name="Emoji",value=str(emoji[0]))
        em.add_field(name="Role",value=role)
        em.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.send(embed=em)
        msg = await ctx.channel.fetch_message(message.content)
        await msg.add_reaction(str(emoji[0]))
    
    @commands.command(name="verify", description="Verifies a user")
    async def verify(self,ctx, user: discord.Member, *, nickname = None):
        if ctx.author.guild_permissions.manage_roles and ctx.author.top_role > user.top_role:
            unvertified = discord.utils.get(ctx.guild.roles, name="Unverified")
            if unvertified in user.roles:
                await user.remove_roles(unvertified)
                memb = discord.utils.get(ctx.guild.roles, name="Member")
                try: await user.add_roles(memb)
                except: pass
                if nickname:
                    await user.edit(nick=nickname)
                embed = discord.Embed(title="Success!", color=choice(self.bot.colorList), description=f"Successfully verified {user.display_name}")
                embed.set_footer(text=f"Approved by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
                general = discord.utils.get(ctx.guild.channels, name="💬⌈general⌋")
                embed = discord.Embed(title=f"Hello! Welcome to the Official SkyClan Discord `{user.display_name}`", color=choice(self.bot.colorList), description="You are officially a new member of SkyClan! You might be very confused as to what all of this is, however do not fear, because I can show you the basics around here.")
                embed.add_field(name="What you should do right now:", value="Right now, you should probably grab a few roles in <#928421166580891718>, ESPECIALLY the Kit role.\nIf you haven't done so already, get familiar with the rules in here. You **will** get punished if you break a rule, so make sure you don't break any rules here.")
                embed.add_field(name="Things to consider:", inline=False, value="The more you talk, the more you level up. Do NOT spam, as this will not contribute to your total xp count. You only gain xp after 60 seconds of sending your last message. You can check your levels by running `!lvl` in any channel (except for threads, SkyBot does NOT listen to commands run in threads).\nGaining levels will give you skybucks, and an additional level to your total level count. Skybucks currently are cosmetics, however soon we will have uses for this currency. You can also check the richest players by running `!rich`.")
                embed.add_field(name="Have a good time here!", inline=False, value="If you read up till here (which I probably doubt, and no one is gonna read this embed that I spent 20 minutes making), then just keep doing what you are doing, maybe try to make the server a bit active, and have a good time during your stay here :smile:")
                embed.set_footer(text=f"`{user.display_name}`", icon_url=user.avatar.url)
                try: await user.send(embed=embed)
                except: 
                    await general.send(content=user.mention, embed=embed)

async def setup(client):
    await client.add_cog(Utility(client))
