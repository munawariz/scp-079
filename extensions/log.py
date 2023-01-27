from datetime import datetime
from discord import DiscordException
from discord.ext import commands
from utils.channel import LOG_CHANNEL

class Logger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def send_log_to_channel(self, ctx: commands.Context, error: DiscordException=None):
        log_channel = self.bot.get_channel(LOG_CHANNEL)

        if not ctx.command:
            await log_channel.send(f"""
```ansi
\u001b[0;31mtimestamp:\u001b[0;0m  {datetime.now()}
\u001b[0;31mguild:\u001b[0;0m      {ctx.guild.name}
\u001b[0;31mchannel:\u001b[0;0m    {ctx.channel.name}
\u001b[0;31mauthor:\u001b[0;0m     {ctx.author.name}#{ctx.author.discriminator}
\u001b[0;31merror:\u001b[0;0m      {error}
```
            """)
        elif ctx.command_failed:
            await log_channel.send(f"""
```ansi
\u001b[0;31mtimestamp:\u001b[0;0m  {datetime.now()}
\u001b[0;31mguild:\u001b[0;0m      {ctx.guild.name}
\u001b[0;31mchannel:\u001b[0;0m    {ctx.channel.name}
\u001b[0;31mcommand:\u001b[0;0m    {ctx.command.name}
\u001b[0;31mauthor:\u001b[0;0m     {ctx.author.name}#{ctx.author.discriminator}
\u001b[0;31merror:\u001b[0;0m      {error}
\u001b[0;31mprompt:\u001b[0;0m     {ctx.current_argument}
```
            """)
        else:
            await log_channel.send(f"""
```ansi
\u001b[0;32mtimestamp:\u001b[0;0m  {datetime.now()}
\u001b[0;32mguild:\u001b[0;0m      {ctx.guild.name}
\u001b[0;32mchannel:\u001b[0;0m    {ctx.channel.name}
\u001b[0;32mcommand:\u001b[0;0m    {ctx.command.name}
\u001b[0;32mauthor:\u001b[0;0m     {ctx.author.name}#{ctx.author.discriminator}
\u001b[0;32merror:\u001b[0;0m      -
\u001b[0;32mprompt:\u001b[0;0m     {ctx.current_argument}
```
            """)

async def setup(bot: commands.Bot):
    await bot.add_cog(Logger(bot=bot))