from discord.ext import commands
import discord
from random import choice

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
      with open("logs.txt","+r") as f: f.write("Message deleted")
      channel = self.bot.get_channel(921581993945362453)
      async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
        if entry.target == message.author:
          deleter = entry.user
        else:
          deleter = message.author
      deleted = discord.Embed(
          description=f"Message deleted in {message.channel.mention}", color=choice(self.bot.colorList))
      deleted.add_field(name="Message", value=message.content or ("This is an embed so it cannot be displayed here"))
      deleted.add_field(name="Author", value=message.author, inline=False)
      deleted.add_field(name="Deleted By", value=deleter, inline=False)
      deleted.set_thumbnail(url=message.author.avatar.url)
      deleted.timestamp = message.created_at
      await channel.send(embed=deleted)

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
      if not message_after.author.bot:
        if message_before.content!=message_after.content:
          channel = self.bot.get_channel(921581993945362453)
          edited = discord.Embed(
              description=f"Message edited in {message_before.channel.mention}", color=choice(self.bot.colorList))
          edited.add_field(name="Message Before", value=message_before.content or 'Not able to be displayed', inline=False)
          edited.add_field(name="Message After", value=message_after.content or 'Not able to be displayed', inline=False)
          edited.add_field(name="Author", value=message_before.author, inline=False)
          edited.set_thumbnail(url=message_before.author.avatar.url)
          edited.timestamp = message_after.created_at
          await channel.send(embed=edited)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
      channel = self.bot.get_channel(921581993945362453)
      m=""
      for message in messages:
          m+=f"{message.content} , " or "Not able to be Displayed , "
      deleter = self.bot.user
      amount = messages.count
      atime = messages[0].created_at
      em = discord.Embed(
          description=f"Bulk messages deleted in {message.channel.mention}", color=choice(self.bot.colorList))
      em.add_field(name="Deleted By", value=deleter, inline=False)
      em.add_field(name="Amount", value=amount, inline=False)
      em.add_field(name="Messages", value=m or ("One or more of the messages is an embed so it cannot be displayed here"), inline=False)
      em.timestamp = atime
      em.set_thumbnail(url=deleter.avatar.url)
      await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_join(self, member):
      channel = self.bot.get_channel(921581993945362453)
      em = discord.Embed(
          description="New Member Joined", color=choice(self.bot.colorList))
      em.add_field(name="Member Name", value=member.mention, inline=False)
      em.add_field(name="Joined At", value=member.joined_at, inline=False)
      em.add_field(name="Account Age", value=member.created_at, inline=False)
      em.set_thumbnail(url=member.avatar.url)
      em.set_footer(text=f"Members in guild: {channel.guild.member_count}")
      await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
      channel = self.bot.get_channel(921581993945362453)
      em = discord.Embed(
          description="Member Left", color=choice(self.bot.colorList))
      em.add_field(name="Member Name", value=member.mention, inline=False)
      em.add_field(name="Joined At", value=member.joined_at, inline=False)
      em.add_field(name="Account Age", value=member.created_at, inline=False)
      em.set_thumbnail(url=member.avatar.url)
      em.set_footer(text=f"Members in guild: {channel.guild.member_count}")
      await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
      channel = self.bot.get_channel(921581993945362453)
      async for entry in channel.guild.audit_logs(limit=1):
          atime = entry.created_at
          user = entry.user
      if before.nick != after.nick:
        em = discord.Embed(
          description="Nickname Updated", color=choice(self.bot.colorList))
        em.add_field(name="Member Name", value=before.name, inline=False)
        em.add_field(name="Old Nickname", value=before.nick, inline=False)
        em.add_field(name="Updated Nickname", value=after.nick, inline=False)
        em.add_field(name="Updated By", value=user, inline=False)
        em.timestamp=(atime)
        em.set_thumbnail(url=before.avatar.url)
        await channel.send(embed=em)

      if before.roles!=after.roles:
        finalbeforeroles=''
        finalafterroles= ''
        for role in before.roles:
          finalbeforeroles+=role.name + ', '
        for role in after.roles:
          finalafterroles+=role.name + ', '
        em = discord.Embed(
          description="Roles Updated", color=choice(self.bot.colorList))
        em.add_field(name="Member Name", value=before.name, inline=False)
        em.add_field(name="Old Roles", value=finalbeforeroles, inline=False)
        em.add_field(name="Updated Roles", value=finalafterroles, inline=False)
        em.set_thumbnail(url=before.avatar.url)
        em.timestamp=(atime)
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
      channel = self.bot.get_channel(921581993945362453)

      if before.channel!=after.channel:
        if before.channel is None:
          em = discord.Embed(
            description="Voice Channel Joined", color=choice(self.bot.colorList))
          em.add_field(name="Member Name", value=member.name, inline=False)
          em.add_field(name="Voice Channel Joined", value=after.channel, inline=False)

        elif after.channel is None:
          em = discord.Embed(
            description="Voice Channel Left", color=choice(self.bot.colorList))
          em.add_field(name="Member Name", value=member.name, inline=False)
          em.add_field(name="Channel Left", value=before.channel, inline=False)

        else:
          em = discord.Embed(
              description="Voice Channel Switched", color=choice(self.bot.colorList))
          em.add_field(name="Member Name", value=member.name, inline=False)
          em.add_field(name="Old Voice Channel", value=before.channel, inline=False)
          em.add_field(name="New Voice Channel", value=after.channel, inline=False)
        em.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=em)

      if before.deaf or after.deaf:
        async for entry in channel.guild.audit_logs(limit=1):
          atime = entry.created_at
          user = entry.user
        em = discord.Embed(
            description="Member Defeaned/Undefeaned", color=choice(self.bot.colorList))
        em.add_field(name="Member Name", value=member.name, inline=False)
        if before.deaf: action="Undeafened"
        else: action="Deafened"
        em.add_field(name="Action", value=action, inline=False)
        em.add_field(name="Done By:", value=user, inline=False)
        em.timestamp=(atime)
        em.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=em)

      if before.mute or after.mute:
        async for entry in channel.guild.audit_logs(limit=1):
          atime = entry.created_at
          user = entry.user
        em = discord.Embed(
            description="Member Muted/Unmuted", color=choice(self.bot.colorList))
        em.add_field(name="Member Name", value=member.name, inline=False)
        if before.mute: action="Unmuted"
        else: action="Muted"
        em.add_field(name="Action", value=action, inline=False)
        em.add_field(name="Done By:", value=user, inline=False)
        em.timestamp=(atime)
        em.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
      channel = self.bot.get_channel(921581993945362453)
      fbefore=""
      fafter=""
      for emoji in before:
        fbefore+=emoji.name+", "
      for emoji in after:
        fafter+=emoji.name+", "
      async for entry in channel.guild.audit_logs(limit=1):
          atime = entry.created_at
          user = entry.user
          action=entry.action
          name=entry.target
          before=(entry.before)
          after=(entry.after)
      em = discord.Embed(
            description="Emojis Updated", color=choice(self.bot.colorList))
      em.add_field(name="Updated By", value=user, inline=False)
      if str(action)=="AuditLogAction.emoji_delete":
        em.add_field(name="Emoji Removed", value=name, inline=False)
      elif str(action)=='AuditLogAction.emoji_create':
        em.add_field(name="Emoji Removed", value=name, inline=False)
      elif str(action)=='AuditLogAction.emoji_update':
        em.add_field(name="Emoji Updated", value=name, inline=False)
        em.add_field(name="Before", value=before.name, inline=True)
        em.add_field(name="After", value=after.name, inline=True)

      em.add_field(name="Old Emojis", value=fbefore, inline=False)
      em.add_field(name="Updated Emojis", value=fafter, inline=False)
      em.timestamp=(atime)
      await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
      pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
      pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
      channel = self.bot.get_channel(921581993945362453)
      if invite.max_uses==0: maxuses="infinite"
      else: maxuses=invite.max_uses
      if invite.max_age==0: maxage="infinite"
      else: maxage=invite.max_age
      em = discord.Embed(
            description="Invite Created", color=choice(self.bot.colorList))
      em.add_field(name="Invite Link", value=invite.url, inline=False)
      em.add_field(name="Created By", value=invite.inviter, inline=False)
      em.add_field(name="For Channel", value=invite.channel, inline=False)
      em.add_field(name="Max age", value=maxage, inline=True)
      em.add_field(name="Max Uses", value=maxuses, inline=True)
      em.timestamp=(invite.created_at)
      await channel.send(embed=em)
  
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
      channel = self.bot.get_channel(921581993945362453)
      async for entry in channel.guild.audit_logs(limit=1):
          atime = entry.created_at
      em = discord.Embed(
            description="Invite Deleted", color=choice(self.bot.colorList))
      em.add_field(name="Code", value=invite.code, inline=False)
      em.add_field(name="For Channel", value=invite.channel, inline=False)
      em.add_field(name="Used", value=invite.uses, inline=False)
      em.timestamp=(atime)
      await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
      async for entry in channel.guild.audit_logs(limit=1):
          user = entry.user
      sendingchannel = self.bot.get_channel(921581993945362453)
      em = discord.Embed(
            description=f"Channel Created {channel.mention}", color=choice(self.bot.colorList))
      em.add_field(name="Name", value=channel.name, inline=False)
      em.add_field(name="Type", value=channel.type, inline=False)
      em.add_field(name="Catgory", value=channel.category, inline=False)
      em.add_field(name="Created By", value=user, inline=False)
      em.set_thumbnail(url=user.avatar.url)
      em.timestamp=(channel.created_at)
      await sendingchannel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
      async for entry in channel.guild.audit_logs(limit=1):
          user = entry.user
      sendingchannel = self.bot.get_channel(921581993945362453)
      em = discord.Embed(
            description="Channel Deleted", color=choice(self.bot.colorList))
      em.add_field(name="Name", value=channel.name, inline=False)
      em.add_field(name="Type", value=channel.type, inline=False)
      em.add_field(name="Catgory", value=channel.category, inline=False)
      em.add_field(name="Deleted By", value=user, inline=False)
      em.set_thumbnail(url=user.avatar.url)
      em.timestamp=(channel.created_at)
      await sendingchannel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
      channel = self.bot.get_channel(921581993945362453)
      async for entry in channel.guild.audit_logs(limit=1):
          user = entry.user
          changes=entry.changes
          atime=entry.created_at
      fbefore=''
      fafter=''
      for change in changes.before:
        fbefore+=f"**{change[0]}** : {change[1]}, "
      for change in changes.after:
        fafter+=f"**{change[0]}** : {change[1]}, "
      em = discord.Embed(
            description="Channel Updated", color=choice(self.bot.colorList))
      em.add_field(name="Channel", value=before.name, inline=False)
      em.add_field(name="Before", value=fbefore, inline=False)
      em.add_field(name="After", value=fafter, inline=False)
      em.set_thumbnail(url=user.avatar.url)
      em.timestamp=(atime)
      await channel.send(embed=em)


#starboard stuf below
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
      if (payload.emoji.name)=='\U00002B50':
        channel= self.bot.get_channel(payload.channel_id)
        msg= await channel.fetch_message(payload.message_id)
        channel=self.bot.get_channel(932711285903224892)
        user=self.bot.get_user(payload.user_id)
        reactor = (await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)).author
        reaction = discord.utils.get(msg.reactions, emoji=payload.emoji.name) 

        if reaction.count==1:
          em = discord.Embed(description=msg.author, color=choice(self.bot.colorList))
          em.add_field(name="Message", value=msg.content or "message could not be typed", inline=False)
          em.add_field(name="Starred by", value=user.mention, inline=False)
          em.add_field(name="Jump Link", value=f'[Jump]({msg.jump_url})')
          em.set_thumbnail(url=reactor.avatar.url)
          em.timestamp=msg.created_at
          await channel.send(content=f':star: in {msg.channel.mention} | ID: {msg.id}', embed=em)
          


    
async def setup(client):
    await client.add_cog(Logs(client))