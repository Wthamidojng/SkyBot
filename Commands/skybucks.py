from typing import Union
from discord.ext import commands
import discord
from asyncio import TimeoutError
from random import choice

class Skybucks(commands.Cog):
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
        await self.bot.wait_until_ready()
        async with self.bot.db.execute("SELECT guild FROM guild WHERE scGuild = 1;") as cur: guilds = await cur.fetchall()
        for r in guilds:
            guild = self.bot.get_guild(r[0])
            person = guild.get_member(user.id)
            leadership = discord.utils.get(guild.roles, name="Leadership_Roles") or await self.role("lsRole",guild)
            if leadership in person.roles: return True
        return False

    @commands.command(name = "balance", description = "check how many skybucks you have!", aliases = ["bal", "scb", "skybucks"])
    async def balance(self, ctx, user : discord.Member = None):
        user = user or ctx.author
        await self.userSetup(user)
        async with self.bot.db.execute("SELECT scb FROM members WHERE memberID = ?", (int(user.id),)) as cur:
            balance = await cur.fetchone()
        embed = discord.Embed(title=":dollar: Skybucks", color=0x5AC18E)
        embed.add_field(name="Balance",value=balance[0])
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name="rich",description="A list of the richest people!")
    async def rich(self, ctx):
        async with self.bot.db.execute("SELECT * FROM members ORDER BY scb DESC;") as cur: r = await cur.fetchall()
        embed = discord.Embed(title="Richest Users",color=choice(self.bot.colorList))
        rank=0
        for row in r: 
            try: 
                user = self.bot.get_user(int(row[0]))
                if not user or not ctx.guild.get_member(user.id) in ctx.guild.members: continue
                if row[1] != 0:
                    rank+=1
                    if rank == 1: fplace = ":first_place:"
                    elif rank == 2: fplace = ":second_place:"
                    elif rank == 3: fplace = ":third_place:"
                    else: fplace= (f"**{rank}.** ")
                    embed.add_field(name=f"{fplace} {user}",value=f"Skybucks- {row[1]}",inline=False)
            except Exception: pass
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.avatar.url)
        mesg = await ctx.send(embed=embed)
        await mesg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "❌"

        try: reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except TimeoutError: await mesg.clear_reactions()
        else: await mesg.delete()
        
    @commands.command(name = "admingive", description = "admins can give you skybucks!", aliases = ["ag"])
    async def admingive(self, ctx, user : discord.Member = None, amt = 0):
        user = user or ctx.author
        await self.userSetup(user)
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)

        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author):
            async with self.bot.db.execute("SELECT scb FROM members WHERE memberID = ?", (int(user.id),)) as cur: balance = await cur.fetchone()
            await self.bot.db.execute("UPDATE members SET scb = scb + ? WHERE memberID = ?", (amt,int(user.id)))
            embed = discord.Embed(title="Admin Gave Skybucks",color=0x5ac18e)
            embed.add_field(name="To",value=user,inline=False)
            embed.add_field(name="Amount",value=amt)
            embed.add_field(name="Balance",value=int(balance[0])+int(amt))
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            await self.bot.db.commit()
        else: await ctx.reply("You do not have sufficient permissions.")
    
    @commands.command(name="admintest")
    async def joe(self, ctx):
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole", ctx.guild.id)
        print(admin)

        if admin in ctx.author.roles: print("True")
        else: print(False)

        print((await self.sc(ctx.guild.id)))
        print((await self.power(ctx.author)))

    @commands.command(name = "take", description = "admins can also take away your skybucks!", aliases = ["at"])
    async def adminremove(self, ctx, user: Union[discord.Member, discord.User, int] = None, amt = 0):
        user = self.bot.check_id(user) or ctx.author
        await self.userSetup(user)
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)

        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author):
            async with self.bot.db.execute("SELECT scb FROM members WHERE memberID = ?", (int(user.id),)) as cur: balance = await cur.fetchone()
            await self.bot.db.execute("UPDATE members SET scb = scb - ? WHERE memberID = ?", (amt,int(user.id)))
            embed = discord.Embed(title="Admin Removed Skybucks",color=0xdd1414)
            embed.add_field(name="From",value=user,inline=False)
            embed.add_field(name="Amount",value=amt)
            embed.add_field(name="Balance",value=int(balance[0])-int(amt))
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            await self.bot.db.commit()
        else: await ctx.reply("You do not have sufficient permissions.")
        
    @commands.command(name = "give", description = "pay someone skybucks. No system of anti cheat yet", aliases = ["pay"])
    async def remove(self, ctx, user: Union[discord.Member, discord.User, int] = None, amt = 0):
        if user:
            self.bot.check_id(user)    
        await self.userSetup(user)
        if user is None: await ctx.reply("You can't give Skybucks to yourself!")
        else: 
            async with self.bot.db.execute("SELECT scb FROM members WHERE memberID = ?", (int(ctx.author.id),)) as cur: balance = await cur.fetchone()
            if balance[0] >= amt and amt > 0:
                await self.bot.db.execute("UPDATE members SET scb = scb - ? WHERE memberID = ?", (amt,int(ctx.author.id)))
                await self.bot.db.execute("UPDATE members SET scb = scb + ? WHERE memberID = ?", (amt,int(user.id))) 
                async with self.bot.db.execute("SELECT scb FROM members WHERE memberID = ?", (int(user.id),)) as cur: userTwoBalance = await cur.fetchone()
                embed = discord.Embed(title="Gift!",color=0x487E8A)
                embed.add_field(name="To",value=user,inline=False)
                embed.add_field(name="Amount",value=amt,inline=True)
                embed.add_field(name=f"{ctx.author.name}'s balance",value=balance[0],inline=False)
                embed.add_field(name=f"{user.name}'s balance",value=userTwoBalance[0],inline=True)
                embed.set_thumbnail(url=user.avatar.url)
                embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            else: await ctx.reply(f"{ctx.author.mention}, you don't have enough money or that's an invalid amount.")

    @commands.command(name = "setbal", description = "Change someones balance. For admin only", aliases = ["sb","setbalance"])
    async def setbal(self, ctx, user: Union[discord.Member, discord.User, int], amt):
        user = self.bot.check_id(user) or ctx.author
        await self.userSetup(user)

        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id)
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or await self.power(ctx.author):

            await self.bot.db.execute("UPDATE members SET scb = ? WHERE memberID = ?", (amt,int(user.id)))
            embed = discord.Embed(title="Admin Set Skybucks",color=0x1471cd)
            embed.add_field(name="User",value=user,inline=False)
            embed.add_field(name="Amount",value=amt)
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            await self.bot.db.commit()
        else: await ctx.reply("You do not have sufficient permissions.")
    
    @commands.command(name="createshopitem", description="Create an item to put in the shop!", aliases=["csi"])
    async def createshopitem(self, ctx, price, inStock, *, item):
        await self.userSetup(ctx.author)
        await ctx.send("Type the description of the item...")
        msg = await self.bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel)
        async with self.bot.db.execute("INSERT INTO shop (itemName, itemDesc, sellerID, price, inStock) VALUES (?, ?, ?, ?, ?) RETURNING *;",(item,msg.content,ctx.author.id,price,int(inStock))) as cur: data = await cur.fetchone()
        embed = discord.Embed(title="New Item in Shop!",color=0x5ac18e)
        embed.add_field(name="Item",value=item)
        embed.add_field(name="Price",value=price)
        embed.add_field(name="Seller",value=ctx.author.name)
        embed.add_field(name="ID",value=data[4])
        embed.add_field(name="In Stock",value=inStock)
        embed.add_field(name="Item Description",value=msg.content,inline=False)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        await self.bot.db.commit()
    
    @commands.command(name="buyitem",description="Buy an item from the shop, but you need to give an ID.",aliases=["buy","bi"])
    async def buyitem(self, ctx, id):
        await self.userSetup(ctx.author)
        async with self.bot.db.execute("SELECT itemName, itemDesc, sellerID, price, inStock FROM shop WHERE itemID = ?;",(int(id),)) as cur: fetch = await cur.fetchone()
        async with self.bot.db.execute("SELECT scb FROM members WHERE memberID = ?;",(ctx.author.id,)) as cur: balance = await cur.fetchone()
        if fetch[3] <= balance[0]:
            await self.bot.db.execute("UPDATE members SET scb = scb - ? WHERE memberID = ?;", (fetch[3],int(ctx.author.id)))
            await self.bot.db.execute("UPDATE members SET scb = scb + ? WHERE memberID = ?;", (fetch[3],int(fetch[2]))) 
            await self.bot.db.execute("UPDATE shop SET inStock = inStock - 1 WHERE itemID = ?;",(int(id),))
            if int(fetch[4])-1 == 0: await self.bot.db.execute("DELETE FROM shop WHERE itemID = ?",(int(id),))
            embed = discord.Embed(title="Item Sold!",color=0x5ac18e)
            embed.add_field(name="Item",value=fetch[0])
            embed.add_field(name="Price",value=fetch[3])
            embed.add_field(name="Seller",value=self.bot.get_user(fetch[2])) or await self.bot.fetch_user(fetch[2])
            embed.add_field(name="ID",value=int(id))
            embed.add_field(name="Left in stock",value=fetch[4]-1)
            embed.add_field(name="Item Description",value=fetch[1],inline=False)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            await self.bot.db.commit()
        else: await ctx.send(f"{ctx.author.mention}, you're poor!")
    
    @commands.command(name="viewitem",description="View any item in the shop!",aliases=["view","vi"])
    async def viewitem(self, ctx, id):
        await self.userSetup(ctx.author)

        async with self.bot.db.execute("SELECT itemName, itemDesc, sellerID, price, inStock FROM shop WHERE itemID = ?",(int(id),)) as cur: fetch = await cur.fetchone()
        if fetch is not None:
            seller = self.bot.get_user(fetch[2]) or await self.bot.fetch_user(fetch[2])
            embed = discord.Embed(title="Item",color=0x107DAC)
            embed.add_field(name="Price",value=fetch[3])
            embed.add_field(name="Item Name",value=fetch[0])
            embed.add_field(name="Seller",value=seller)
            embed.add_field(name="In Stock",value=fetch[4])
            embed.add_field(name="Description",value=fetch[1],inline=False)
            embed.set_thumbnail(url=seller.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else: await ctx.send(f"{ctx.author.mention}, that item doesn't exist!")


    @commands.command(name="searchitem",description="Search for items you want!",aliases=["search"]) 
    async def search(self, ctx, *, query):
        await self.userSetup(ctx.author)
        embed = discord.Embed(title="Results",color=0x1471cd)
        async with self.bot.db.execute("SELECT * FROM shop ORDER BY RANDOM();") as cur: table = await cur.fetchall()
        amt = 0
        for r in table:
            if query in r[0]: 
                embed.add_field(name=r[0],value=f"Description: {r[1]} | Price: {r[2]} | ID: {r[4]}")
                amt+=1
        if amt == 0: embed.add_field(name="No Results",value="Sorry. No results were found with the given query.")
        embed.set_thumbnail(icon_url=ctx.guild.icon.url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        mesg = await ctx.send(embed=embed)
        await mesg.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == "❌"

        try: reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except TimeoutError: await mesg.clear_reactions()
        else: await mesg.delete()
    
    @commands.command(name="removeitem",description="Remove the item. Requires certain permissions.")
    async def removeitem(self, ctx, id, *, reason="None was specified"):
        await self.userSetup(ctx.author)
        admin = discord.utils.get(ctx.guild.roles, name="Leadership_Roles") or await self.role("lsRole",ctx.guild.id) or await self.power(ctx.author)
        async with self.bot.db.execute("SELECT * FROM shop WHERE itemID = ?;",(id,)) as cur: seller = await cur.fetchone() 
        if (admin in ctx.author.roles and await self.sc(ctx.guild.id)) or seller[2] == ctx.author.id or await self.power(ctx.author): await self.bot.db.execute("DELETE FROM shop WHERE itemID = ?;",(id,))
        embed = discord.Embed(title="Deleted Item",color=0x5ac18e)
        embed.add_field(name="Item Name",value=seller[0])
        person = self.bot.get_user(seller[2]) or await self.bot.fetch_user(seller[2])
        embed.add_field(name="Seller",value=person)
        embed.add_field(name="Price",value=seller[3])
        embed.add_field(name="Reason",value=reason)
        embed.add_field(name="Item Description",value=seller[1],inline=False)
        embed.set_thumbnail(url=person.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="searchitem",descritpion="Search for items that you would like to buy",aliases=["search"])
    async def search(self, ctx, *, query):
        async with self.bot.db.execute("SELECT * FROM shop ORDER BY price ASC;") as cur: items = await cur.fetchall()
        embed = discord.Embed(title="Results", color=0x107DAC)
        icon = None
        results = 0
        for r in items:
            seller = self.bot.get_user(r[2]) or await self.bot.fetch_user(r[2])
            if not icon: icon = seller.avatar.url
            if query in r[0]: 
                embed.add_field(name=r[0],value=f"Seller: {seller} | Price: {r[3]} | ID: {r[4]}\n{r[1]}")
                results+=1
        embed.set_thumbnail(url=icon or ctx.author.avatar.url)
        if results == 0: embed.add_field(name="No Results",value="Try again with a different query.")
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Skybucks(client))

