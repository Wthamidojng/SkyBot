from asyncio import sleep
from discord.ext import commands
import discord
from random import choice

class Helpful(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot

    async def sc(self,guild):
        async with self.bot.db.execute("SELECT scGuild FROM guild WHERE guild = ?;",(guild,)) as cur: scguild = await cur.fetchone()
        if not scguild: return False

        if scguild[0] == 1: return True
        else: return False

    async def userSetup(self, user):
        try: 
            await self.bot.db.execute("INSERT INTO members (memberID) VALUES (?);", (int(user.id),))
            await self.bot.db.commit()
        except Exception: pass

    async def role(self, role : str, guild):
        async with self.bot.db.execute(f"SELECT {role} FROM guild WHERE guild = ?",(guild,)) as cur: roleid = await cur.fetchone()
        if not role: return None
        role = self.bot.get_role(roleid[0])
        return role
    
    async def power(self,user):
        async with self.bot.db.execute(f"SELECT guild FROM guild WhERE scGuild = 1;") as cur: guilds = await cur.fetchall()
        for r in guilds:
            guild = self.bot.get_guild(r[0])
            if guild:
                person = guild.get_member(user.id)
                leadership = discord.utils.get(guild.roles, name="Leadership_Roles") or await self.role("lsRole",guild)
                if leadership in person.roles: return True
        return False

    @commands.command(name="setstory",value="Sets your story to your choice!")
    async def setstory(self,ctx,*,story=None): 
        await self.userSetup(ctx.author)
        await self.bot.db.execute("UPDATE members SET story = ? WHERE memberID = ?;",(story,ctx.author.id))
        await ctx.send("Added your story :thumbsup:")

    @commands.command(name="maketag",description="Makes a tag.")
    async def mktag(self,ctx,*,tagName):
        await ctx.send("Whats the tag description?")
        desc = (await self.bot.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel)).content
        if len(desc) > 1970 : return await ctx.reply("Please shorten your description a bit.")
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author): approve = 1
        else: approve = 0
        try: await self.bot.db.execute("INSERT INTO tags VALUES (?,?,?,?);",(tagName,desc,ctx.author.id,approve))
        except Exception: return await ctx.send("Sorry, that tag is already taken.")
        
        await ctx.send(f"Added tag :thumbsup:")

    @commands.command(name="tag",description="Tag something. Put `unapprove` before the name of the tag if you want to see unapproved tags.", aliases=['t', 'ta'])
    async def tag(self,ctx,*,tag):
        async with self.bot.db.execute("SELECT * FROM tags WHERE name = ?;",(tag,)) as cur: t = await cur.fetchone()
        if not t: return await ctx.send("This tag does not exist. Use `!maketag` to make one.")
        if t[3] != 1: return await ctx.send("That tag isn't approved, you can't use it.")
        user =  self.bot.get_user(t[2]) or await self.bot.fetch_user(t[2])
        return await ctx.send(f"{t[1]}\n\n**-{user}**")

    @commands.command(name="edittag",description="edit or entirely remove your tag.",aliases=["et"])
    async def edit_tag(self,ctx,*,tag):
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)
        async with self.bot.db.execute("SELECT * FROM tags WHERE name = ?;",(tag,)) as cur: t = await cur.fetchone()
        if not t: return await ctx.reply("That tag doesn't exist.")
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author) or ctx.author.id == t[2]: 
            await ctx.send("Type what to set the tag to. You can also type (d)elete tag or (q)uit.")
            msg = await self.bot.wait_for("message",check = lambda u: u.channel == ctx.channel and u.author == ctx.author)
            if msg.content == "d": 
                await self.bot.db.execute("DELETE FROM tags WHERE name = ?;",(tag,))
                await ctx.send(f"Tag `{tag}` deleted.")
            elif msg.content == "q": return await ctx.send("Successfully quit.")
            elif msg.content == t[1]:return await ctx.send(f"Please set a new value for tag `{tag}`.")
            elif len(msg.content) > 1970: return await msg.reply("Please shorten your description a bit.")
            else:
                await self.bot.db.execute("UPDATE tags SET desc = ? WHERE name = ?;",(msg.content,tag))
                await self.bot.db.execute("UPDATE tags SET user = ? WHERE name = ?;", (msg.author.id, tag)) 
                embed = discord.Embed(title=f"Successfully updated tag `{tag}`!", color=choice(self.bot.colorList))
                embed.add_field(name="Original Content", value=t[1] if len(t[1]) < 1024 else str(t[1])[0:1010] + "...")
                embed.add_field(name="Updated Content", value=msg.content if len(msg.content) < 1024 else msg.content[0:1010] + "...", inline=False)
                embed.set_footer(text=f"Edited by {ctx.author}", icon_url=ctx.author.avatar.url)
                try: await ctx.send(embed=embed)
                except discord.errors.HTTPException:
                    value = str(t[1])[0:1010] + "..."
                    embed.set_field_at(index=0, value=value)
                    await ctx.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention} You do not own this tag.")

    @commands.command(name="deletetag", description="deletes a tag", aliases=["deltag", "dt", "delt", "dtag"])
    async def deletetag(self,ctx,*,tag):
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)
        async with self.bot.db.execute("SELECT * FROM tags WHERE NAME = ?;",(tag)) as cur: t = await cur.fetchone()
        if not t: return await ctx.reply("That tag doesn't exist.")
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author) or ctx.author.id == t[2]:
            msg = await ctx.send(f"Are you sure you want to delete tag {tag}?")
            await msg.add_reaction("✅")
            await msg.add_reaction("❎")
            try: 
                reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user.id == ctx.author.id and str(reaction.emoji) in ["✅", "❎"] and reaction.message.channel.id == ctx.channel.id, timeout=60.0)
            except TimeoutError: 
                await ctx.send("Automatically cancelled the operation.")
                return await msg.clear_reactions()
            else:
                if str(reaction.emoji) == "❎":
                    await ctx.send("Cancelled the operation.")
                    await sleep(1)
                    await ctx.channel.purge(limit=3, check=lambda c: c.author.id == ctx.author.id or c.author == self.bot.user)
                else:
                    await self.bot.db.execute("DELETE FROM tags WHERE name = ?", (tag))
                    await ctx.send(f"Tag `{tag}` deleted with content:\n```{t[1]}```")
        else:
            await ctx.send(f"{ctx.author.mention} You do not own this tag.")
                
                

            
    @commands.command(name="approvetag",description="approves a tag",aliases=["approve", "app", "ap"])
    async def approvetag(self,ctx,*,tag=None):
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)

        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author):
            if tag:
                async with self.bot.db.execute("SELECT * FROM tags WHERE name = ?;",(tag,)) as cur: t = await cur.fetchone()
                if not t: return await ctx.reply("That tag doesn't exist.")
                if t[3] == 1: return await ctx.reply("That tag is already approved, or it has been made by an admin.")
                await self.bot.db.execute("UPDATE tags SET status = 1 WHERE name = ?;", (tag,))
                embed = discord.Embed(title=f"Approved Tag **{tag}**! ", color=choice(self.bot.colorList))
                embed.set_footer(text=f"Edited by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.add_field(name="Tag content", value=t[1])
                await ctx.send(embed=embed)
            else:
                async with self.bot.db.execute("SELECT * FROM tags WHERE status = 0;") as cur: tags = await cur.fetchall()
                desc = ""
                for t in tags: desc+=f"\n{t[0]}"
                em = discord.Embed(title="Unapproved tags",color=choice(self.bot.colorList),description=f"{desc}\n\nUse `!approvetag <tag>` to approve a tag (only works for leadership roles+).")
                em.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
                await ctx.send(embed=em)
        else:
            return await ctx.reply("You need more perms to use this command.")

    @commands.command(name="unapproved",description="displays all unapproved tags", aliases=["unapp", "u", "ua", "un"])
    async def unapproved(self, ctx):
        await ctx.invoke(self.approvetag)
    
    @commands.command(name="customprefix", description="Sets a custom prefix for yourself :)", aliases=["cp", "prefix", "pref", "custompref"])
    async def customprefix(self,ctx,*,prefix = None):
        if not prefix:
            async with self.bot.db.execute("SELECT prefix FROM members WHERE memberID = ?;",(ctx.author.id)) as cur: pre = await cur.fetchone()
            return await ctx.send(f"Your current custom prefix is `{'None Set' if pre[0] == '!' else pre[0]}`")
        await self.bot.db.execute("UPDATE members SET prefix = ? WHERE memberID = ?;", (prefix, ctx.author.id))
        embed = discord.Embed(title="Successfully set custom prefix", color=choice(self.bot.colorList))
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        embed.add_field(name="Updated Prefix", value=prefix)
        embed.set_thumbnail(url="https://th.bing.com/th/id/OIP.fvP3VLBUE76X5WaKPcNc4QHaHw?pid=ImgDet&rs=1")
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Helpful(client))