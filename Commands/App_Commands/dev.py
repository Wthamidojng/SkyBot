from discord.ext import commands
import discord
from discord import app_commands
from asyncio import TimeoutError

class Slash_Dev(commands.Cog):
    def __init__(self,bot):
        self.bot : commands.Bot = bot

    @app_commands.command(name="request", description="Request features and report bug fixes!")
    @app_commands.describe(report="What you want to report")
    @app_commands.guilds(921230858311057418)
    async def report(self, interaction: discord.Interaction,report: str):
        with open("requests.txt","a") as f: f.write(f"\n{interaction.created_at}: {report} - {interaction.user}")
        await interaction.response.send_message("Thank you for requesting the feature or reporting the bug!")

    @app_commands.command(name="about",description="About the bot and the people who helped make it happen") #DO NOT EDIT THIS
    @app_commands.guilds(921230858311057418)
    async def about(self,interaction: discord.Interaction):
        embed = discord.Embed(title="About Me",color=0x154f94)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Developers",value="Spikestar\nLeafshade\nDarkfang\nDarklord\ndvogit\nAM",inline=False)
        embed.add_field(name="About",value="This bot was created for SkyClan, a group which hangs out and talks to each other.")
        embed.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
        mesg = await interaction.original_message()
        await mesg.add_reaction("❌")

        try: reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: u.id == interaction.user.id and str(r.emoji) == "❌")
        except TimeoutError: await mesg.clear_reactions()
        else: await mesg.delete()

async def setup(bot: commands.Bot):
    await bot.add_cog(Slash_Dev(bot))
        
    
