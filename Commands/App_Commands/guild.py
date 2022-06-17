from random import choice
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

class Slash_Guild(commands.Cog):
    def __init__(self,bot): #guild INT PRIMARY KEY, lsRole INT, counterChnl INT, unverified INT, prefix TEXT DEFAULT \"!\", scGuild INT, countedNum INT DEFAULT 0, xpMulti DEFAULT 1
        self.bot : commands.Bot = bot
    
    async def role(self, role, guild):
        async with self.bot.db.execute(f"SELECT {role} FROM guild WHERE guild = ?;",(guild,)) as cur: roleid = await cur.fetchone()
        role = self.bot.get_guild(guild).get_role(roleid[0])
        return role

    async def power(self,user):
        await self.bot.wait_until_ready()
        async with self.bot.db.execute(f"SELECT guild FROM guild WhERE scGuild = 1;") as cur: guilds = await cur.fetchall()
        for r in guilds:
            guild = self.bot.get_guild(r[0])
            leadership = discord.utils.get(guild.roles, name="Leadership_Roles") or await self.role("lsRole",guild)
            if leadership in user.roles: return True
        return False

    @app_commands.command(name="set",description="Set a specific item to your choice.")
    @app_commands.guilds(921230858311057418)
    @app_commands.describe(item="What Item You Want to Reset", value="The Value You Want to Set that Item to")
    @app_commands.choices(item=[
        Choice(name="Leadership Role", value="lsRole"),
        Choice(name="Counter Channel", value="counterChnl"),
        Choice(name="Unverified", value="unverified"),
        Choice(name="Prefix", value="prefix"),
        Choice(name="Ads", value="ads"),
        Choice(name="SkyClan Guild", value="scGuild")
    ])
    async def set(self, interaction: discord.Interaction, item: Choice[str], value: str):
        if item.value == "scGuild" and not (await self.power(interaction.user) or await self.role("lsRole", interaction.guild.id)) or not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(f"{interaction.user.mention}, you don't have the permissions for that.", ephemeral=True)

        if item.value in ("lsRole", "unverified"):
            try: value = await commands.RoleConverter.convert(await self.bot.get_context(interaction.channel.last_message), value)
            except: return await interaction.response.send_message("That role does not exist.", ephemeral=True)

        if item.value in ("ads", "scGuild") and not isinstance(value, int): value = int(bool(value))
        if item.value == "counterChnl": 
            try: value = await commands.RoleConverter.convert(self.bot.get_context(interaction.channel.last_message), value)
            except: return await interaction.response.send_message("That channel does not exist.", ephemeral=True)
        
        await self.bot.db.execute(f"UPDATE guild SET {item.value} = ? WHERE guild = ?;",(value,interaction.guild.id))

        async with self.bot.db.execute("SELECT lsRole, counterChnl, unverified, prefix, ads FROM guild WHERE guild = ?;",(interaction.guild.id,)) as cur: stuff = await cur.fetchone()
        embed = discord.Embed(title=f"Set {item.name} to `{value}`", color=choice(self.bot.colorList))
        embed.add_field(name="Leadership Role",value=interaction.guild.get_role(stuff[0]))
        embed.add_field(name="Counting channel",value=interaction.guild.get_channel(stuff[2]))
        embed.add_field(name="Unverified Role",value=interaction.guild.get_role(stuff[3]),inline=False)
        embed.add_field(name="Prefix",value=stuff[3])
        embed.add_field(name="Ads", value=bool(stuff[4]))
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serversetup",description="Sets up the server! This command should be run first.")
    @app_commands.guilds(921230858311057418)
    @app_commands.describe(lsrole="Leadership Role for This Server (Admin)", counting="The Counting Channel for this Server", unverified="The Unverified Role for this Server", prefix="The Bot Prefix for this Server", ads="Whether or not SkyBot Should Post Ads in this Server")
    async def ssetup(self, interaction: discord.Interaction, lsrole: discord.Role, counting: discord.TextChannel, unverified: discord.Role, prefix: str = "!", ads: bool = True):
        await interaction.response.defer(thinking=True)
        await self.bot.db.execute("UPDATE guild SET lsRole = ?, counterChnl = ?, unverified = ?, prefix = ?, ads = ? WHERE guild = ?;",(lsrole.id, counting.id, unverified.id, prefix, int(ads), interaction.guild.id))
        embed = discord.Embed(title="Server Successfully Set up!",color=0x134E41)
        embed.add_field(name="Leadership Role",value=lsrole)
        embed.add_field(name="Counting channel",value=counting)
        embed.add_field(name="Unverified Role",value=unverified,inline=False)
        embed.add_field(name="Prefix",value=prefix)
        embed.add_field(name="Ads", value=ads)
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
            

async def setup(client):
    await client.add_cog(Slash_Guild(client))
