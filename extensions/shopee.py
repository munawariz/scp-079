from bot import SCP079
from discord import Embed
from discord.ext import commands
from shopee_wrapper.product import Product
from utils.currency import to_currency_string

class Shopee(commands.Cog):
    def __init__(self, bot: SCP079):
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
        embed.add_field(name='Harga', value=self.get_product_price(data))
        embed.add_field(name='Terjual', value=data['product']['sold'])
        embed.add_field(name='Stok', value=data['product']['stock'])
        embed.add_field(name='Brand', value=data['product']['brand'])
        if data['product']['attributes']:
            for attribute in data['product']['attributes']:
                embed.add_field(name=attribute['name'], value=attribute['value'])

        return embed

    def get_product_price(self, data):
        if data['product']['price_min'] != data['product']['price_max']:
            return f'{to_currency_string(data["product"]["price_min"])} - {to_currency_string(data["product"]["price_max"])}'
        else:
            return to_currency_string(data['product']['price'])

async def setup(bot: SCP079):
    await bot.add_cog(Shopee(bot=bot))