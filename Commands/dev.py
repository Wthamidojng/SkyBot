from discord.ext import commands
import discord
from asyncio import TimeoutError

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot

    @commands.command(name="request",description="Request features and report bug fixes!",aliases=["bug","feature", "report"])
    async def report(self,ctx,*,bug):
        with open("requests.txt","a") as f: f.write(f"{bug} -{ctx.author}")
        await ctx.send("Thank you for requesting the feature/bug fix!")

    @commands.command(name="about",description="About the bot and the people who helped make it happen") #DO NOT EDIT THIS
    async def about(self,ctx):
        embed = discord.Embed(title="About Me",color=0x154f94)
        embed.set_thumbnail(url=ctx.me.avatar.url)
        embed.add_field(name="Developers",value="Spikestar\nLeafshade\nDarkfang\nDarklord\ndvogit\nAM",inline=False)
        embed.add_field(name="About",value="This bot was created for SkyClan, a group which hangs out and talks to each other.")
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        mesg = await ctx.send(embed=embed)
        await mesg.add_reaction("❌")

        try: reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=lambda r, u: u.id == ctx.author.id and str(r.emoji) == "❌")
        except TimeoutError: await mesg.clear_reactions()
        else: await mesg.delete()

async def setup(client):
    await client.add_cog(Dev(client))
