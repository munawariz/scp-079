from asyncpraw import Reddit as RedditClient
from asyncpraw.models import Subreddit, Submission
from asyncprawcore.exceptions import NotFound, Redirect, ServerError
from bot import SCP079
from datetime import datetime
from discord import app_commands, ButtonStyle, Embed, Interaction, DiscordException
from discord.ext import commands
from discord.ui import button, Button, View
from enum import Enum
from typing import List
from utils.url import is_valid_image
import aiohttp
import os

class Reddit(commands.Cog):
    def __init__(self, bot: SCP079):
        self.bot = bot

    async def get_client(self):
        self.session = aiohttp.ClientSession(trust_env=True)
        self.reddit_client = RedditClient(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent=os.environ.get('REDDIT_USER_AGENT'),
            username=os.environ.get('REDDIT_USERNAME'),
            password=os.environ.get('REDDIT_PASSWORD'),
            requestor_kwargs={'session': self.session},
        )

        return self.reddit_client

    class Sort(Enum):
        Random = 'random'
        Relevance = 'relevance'
        Hot = 'hot'
        Top = 'top'
        New = 'new'
    
    class Syntax(Enum):
        Lucene = 'lucene'
        Plain = 'plain'
        Cloudsearch = 'cloudsearch'
        
    class TimeFilter(Enum):
        All = 'all'
        Day = 'day'
        Hour = 'hour'
        Week = 'week'
        Month = 'month'
        Year = 'year'

    class RedditView(View):
        def __init__(self, submissions: List[Submission], orig_interaction: Interaction):
            super().__init__(timeout=180)

            self.current_index = 0
            self.submissions = submissions
            self.orig_interaction = orig_interaction
            self.toggle_send_button()

        async def on_timeout(self) -> None:
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True

            await self.orig_interaction.edit_original_response(view=self)
            return await super().on_timeout()

        @property
        def submission(self) -> Submission:
            return self.submissions[self.current_index]

        @property
        def send_button(self) -> Button:
            return [child for child in self.children if isinstance(child, Button) and child.custom_id == 'reddit:send'][0]

        @property
        def submission_has_image(self) -> bool:
            return self.submission.thumbnail and is_valid_image(self.submission.url)

        # Currently violating DRY concept, refactor ASAP
        @property
        def embed(self) -> Embed:
            date = datetime.utcfromtimestamp(self.submission.created_utc).strftime('%Y-%m-%d')
            embed = Embed(title=self.submission.title[:255], url=self.submission.url, color=0xff4500)
            embed.set_author(name=f'Posted by /u/{self.submission.author} on {date}',icon_url="https://cdn2.iconfinder.com/data/icons/metro-ui-icon-set/512/Reddit.png", url=f'https://www.reddit.com/user/{self.submission.author}')

            if self.submission.link_flair_text: embed.add_field(name='🏷️ Flair', value=self.submission.link_flair_text, inline=True)
            if self.submission.over_18: embed.add_field(name='🏷️ Marked', value="NSFW", inline=True)
            if self.submission.thumbnail and is_valid_image(self.submission.url): embed.set_image(url=self.submission.url)
            if self.submission.is_video: embed.add_field(name='Video URL', value=self.submission.url, inline=False)
            if self.submission.selftext: embed.description = f'{self.submission.selftext[:1024]}\n'

            embed.set_footer(text=f'👍{self.submission.ups} ─── {self.current_index+1} of {len(self.submissions)} posts')

            return embed

        def toggle_send_button(self):
            if self.submission_has_image: self.send_button.disabled=False
            else: self.send_button.disabled=True

        @button(label='Prev', style=ButtonStyle.grey, custom_id='reddit:prev')
        async def prev(self, interaction: Interaction, button: Button):
            await interaction.response.defer()
            self.current_index -= 1
            self.toggle_send_button()
            await self.orig_interaction.edit_original_response(embed=self.embed, view=self)

        @button(label='Delete', style=ButtonStyle.red, custom_id='reddit:delete')
        async def delete(self, interaction: Interaction, button: Button):
            await self.orig_interaction.delete_original_response()

        @button(label='Next', style=ButtonStyle.grey, custom_id='reddit:next')
        async def next(self, interaction: Interaction, button: Button):
            await interaction.response.defer()
            self.current_index += 1
            self.toggle_send_button()
            await self.orig_interaction.edit_original_response(embed=self.embed, view=self)

        @button(label='Send To Me', style=ButtonStyle.blurple, custom_id='reddit:send')
        async def send(self, interaction: Interaction, button: Button):
            await interaction.response.defer()
            await interaction.user.send(self.submission.url)

    @app_commands.command(description='Fetch submission(s) from a subreddit', nsfw=True)
    @app_commands.describe(subreddit='Subreddit name')
    @app_commands.describe(search='Search query')
    @app_commands.describe(limit='Maximum submissions fetched, default 20')
    @app_commands.describe(sort='Sort submission, default random')
    @app_commands.describe(syntax='Searching syntax, default lucene')
    @app_commands.describe(time_filter='Submission time filter, default all')
    async def reddit(self,
        interaction: Interaction,
        subreddit: str,
        search: str=None,
        limit: int=20,
        sort: Sort=Sort.Random,
        syntax: Syntax=Syntax.Lucene,
        time_filter: TimeFilter=TimeFilter.All):
        await interaction.response.defer()

        client = await self.get_client()
        self.subreddit = await client.subreddit(subreddit, fetch=True)
        self.submissions = await self.get_submission(subreddit=self.subreddit, search=search, limit=limit, sort=sort.value, syntax=syntax.value, time_filter=time_filter.value)
        self.current_index = 0
        self.submission = self.submissions[self.current_index]
        await self.session.close()

        await interaction.followup.send(embed=self.embed, view=self.RedditView(submissions=self.submissions, orig_interaction=interaction))

    async def get_submission(self,
        subreddit: Subreddit,
        search: str,
        limit: int,
        sort: str,
        syntax: str,
        time_filter: str) -> List[Submission]:
        result = []
        if search:
            async for submission in subreddit.search(
                query=search,
                sort=sort,
                syntax=syntax,
                time_filter=time_filter,
                limit=limit): 
                
                result.append(submission)
        else:
            if sort == 'hot':
                result = [submission async for submission in subreddit.hot(limit=limit)]
            elif sort == 'new':
                result = [submission async for submission in subreddit.new(limit=limit)]
            elif sort == 'top':
                result = [submission async for submission in subreddit.top(limit=limit)]
            else:
                result = [submission async for submission in subreddit.random_rising(limit=limit)]

        return result

    # Currently violating DRY concept, refactor ASAP
    @property
    def embed(self) -> Embed:
        date = datetime.utcfromtimestamp(self.submission.created_utc).strftime('%Y-%m-%d')
        embed = Embed(title=self.submission.title[:255], url=self.submission.url, color=0xff4500)
        embed.set_author(
            name=f'Posted by /u/{self.submission.author} on {date}',
            icon_url='https://cdn2.iconfinder.com/data/icons/metro-ui-icon-set/512/Reddit.png',
            url=f'https://www.reddit.com/user/{self.submission.author}')

        if self.submission.link_flair_text: embed.add_field(name='🏷️ Flair', value=self.submission.link_flair_text, inline=True)
        if self.submission.over_18: embed.add_field(name='🏷️ Marked', value="NSFW", inline=True)
        if self.submission.thumbnail and is_valid_image(self.submission.url):embed.set_image(url=self.submission.url)
        if self.submission.is_video: embed.add_field(name='Video URL', value=self.submission.url, inline=False)
        if self.submission.selftext: embed.description = f'{self.submission.selftext[:1024]}\n'

        embed.set_footer(text=f'👍{self.submission.ups} ─── {self.current_index+1} of {len(self.submissions)} posts')

        return embed

    @reddit.error
    async def reddit_error(self, interaction: Interaction, error: DiscordException):
        embed = Embed(color=0xd62929, title='Terjadi Kesalahan Saat Menjalankan Command Reddit')
        error = error.original if hasattr(error, 'original') else error

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = 'Kesalahan Penggunan Command.\n `!reddit <namasubreddit> <optional:submissionsearch>`'

        if isinstance(error, Redirect) or isinstance(error, NotFound):
            embed.description = 'Subreddit gagal ditemukan atau tidak tersedia'

        if isinstance(error, IndexError):
            embed.description = 'Submission gagal ditemukan atau tidak tersedia'

        if isinstance(error, ServerError):
            pass

        embed.set_footer(text=f'❌  {error}')

        await self.session.close()
        await interaction.followup.send(embed=embed, ephemeral=True)
        await self.bot.on_app_command_error(interaction, error)

async def setup(bot: SCP079):
    await bot.add_cog(Reddit(bot=bot))