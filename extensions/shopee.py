from discord import Embed
from discord.ext import commands
from shopee_wrapper.product import Product
import locale

class Shopee(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['sp'])
    async def shopee_product(self, ctx: commands.Context, url: str):
        async with ctx.typing():
            product = Product(link=url)
            embed = self.generate_embed(product, url)
            await ctx.channel.send(embed=embed)
    
    def generate_embed(self, product: Product, url: str):
        data = product.serialize

        embed = Embed(title=data['product']['name'], url=url, color=0xff4500)
        embed.set_author(name='Product by '+data['shop']['name'], url='https://shopee.co.id/'+data['shop']['username'], icon_url='https://img.icons8.com/fluency/512/shopee.png')
        embed.set_image(url=data['product']['images'][0])
        embed.add_field(name='Description', value=data['product']['description'][0:256]+'...', inline=False)
        embed.add_field(name='Price', value=self.get_product_price(data))
        embed.add_field(name='Sold', value=data['product']['sold'])
        embed.add_field(name='Stock', value=data['product']['stock'])
        embed.add_field(name='Brand', value=data['product']['brand'])
        for attribute in data['product']['attributes']:
            embed.add_field(name=attribute['name'], value=attribute['value'])

        return embed

    def get_product_price(self, data):
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
        if data['product']['price_min'] != data['product']['price_max']:
            return f'{locale.currency(data["product"]["prince_min"], grouping=True)} - {locale.currency(data["product"]["price_max"], grouping=True)}'
        else:
            return locale.currency(data['product']['price'], grouping=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Shopee(bot=bot))