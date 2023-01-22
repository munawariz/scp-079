from discord.ext import commands

class Tokopedia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['tp'])
    async def tokopedia_product(self, ctx: commands.Context, url: str):
        await ctx.channel.send(url)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tokopedia(bot=bot))