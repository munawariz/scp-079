from discord import Embed
from discord.ext import commands
from tokopedia_wrapper.product import Product
import locale

class Tokopedia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
        self.bot = bot

    @commands.command(aliases=['tp'])
    async def tokopedia_product(self, ctx: commands.Context, url: str):
        async with ctx.typing():
            product = Product(link=url)
            embed = self.generate_embed(product, url)
            await ctx.channel.send(embed=embed)

    def generate_embed(self, product: Product, url: str):
        data = product.serialize
        print(data)

        embed = Embed(title=data['product']['name'], url=url, color=0x059200)
        embed.set_author(name='Product by '+data['shop']['name'], url='https://www.tokopedia.com/'+product.shop_domain, icon_url='https://seeklogo.com/images/T/tokopedia-logo-5340B636F6-seeklogo.com.png')
        embed.set_image(url=data['product']['images'][0])
        embed.add_field(name='Harga', value=locale.currency(data['product']['price'], grouping=True))
        embed.add_field(name='Stok', value=data['product']['stock'])
        embed.add_field(name='Kondisi', value=data['product']['condition'])
        embed.add_field(name='Kategori', value=data['product']['category'])

        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Tokopedia(bot=bot))