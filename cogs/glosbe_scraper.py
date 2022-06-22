from discord.ext import commands
import asyncio
from math import ceil
import httpx
from pyquery import PyQuery as pq
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

from resources.dest_langs import DEST_LANGS_DICT
url = "https://glosbe.com/"
SOURCE_LANG = 'en'

async def scrape_glosbe_dict(word: str, from_lang: str = "en", to_lang: str = "jp") -> [str]:
    # Getting the link
    try:
        resp = httpx.get(f"{url}{from_lang}/{to_lang}/{word}")
    except Exception:
        raise

    # Reading the site's text
    doc = pq(resp.text)

    # Getting the translated words
    try:
        translated_words = doc('''#dictionary-content > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > ul > li > div:nth-child(3) > span.translation__item__phrase''').text()
        return translated_words
    except:
        #If no translation is found it returns empty string which is later used to delete untranslated entries
        return ''

class Glosbe_Scraper(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.command()
    async def scrapeglosbe(self, ctx, langset, *, phrase):
        # First, the bot translates the word to one predefined language
        body = []
        result_list = await scrape_glosbe_dict(phrase, SOURCE_LANG, 'ja')
        body.append(['japanese', result_list])

        output = t2a(
            header=["Language", "Translation"],
            body=body,
            style=PresetStyle.thick,
            alignments=[Alignment.LEFT] + [Alignment.CENTER],
            first_col_heading=True
        )
        await ctx.send(f"```\n{output}\n```")

    # Now depending on the arguments, the set is created and the phrase is translated into other languages

        DEST_LANGS = ()
        try:
            for letter in list(langset):
                DEST_LANGS += DEST_LANGS_DICT[letter]
        except:
            await ctx.send("Wrong language set")
            return

        loop = asyncio.get_event_loop()
        # A list of tasks is created and then converted into a tuple
        tasks = tuple([(scrape_glosbe_dict(phrase, 'en', lang[1])) for lang in DEST_LANGS])
        # Then they are gathered into a list of results
        results = await asyncio.gather(*tasks)

        body = []
        # A body for the next table is created
        for i in range(len(DEST_LANGS)):
            words = ', '.join(results[i].split(' '))
            body.append([DEST_LANGS[i], words])

        # Getting rid of words with no translation
        body = [entry for entry in body if entry[1] != '']

        # The translations are sent in batches of 5 per message
        # The limit is 2000 characters so sending in batches of 10+ sometimes gives errors due to the length
        for i in range(int(ceil(len(body)/5))):
            try:
                body_part = body[i*5:(i*5)+5]
                output = t2a(
                    header=["Language", "Translation"],
                    body=body_part,
                    style=PresetStyle.thick,
                    alignments=[Alignment.LEFT]+[Alignment.CENTER],
                    first_col_heading=True
                )
                await ctx.send(f"```\n{output}\n```")

            except IndexError as e:
                # Not enough translations to select 5 of them, instead it just takes the rest and sends
                body_part = body[i * 5:]
                output = t2a(
                    header=["Language", "Translation"],
                    body=body_part,
                    style=PresetStyle.thick,
                    alignments=[Alignment.LEFT] + [Alignment.CENTER],
                    first_col_heading=True
                )
                await ctx.send(f"```\n{output}\n```")

def setup(client):
    client.add_cog(Glosbe_Scraper(client))