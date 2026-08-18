import scrapy
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider


class SteamTagSpider(CrawlSpider):
    """
    Spider to crawl steam page
    """

    name = "collect_tags"

    async def start(self):
            url = "https://store.steampowered.com/tag/browse/#global_492"
            self.gameTags = {}
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for tag in response.css("div.tag_browse_tag"):
            self.gameTags.update({tag.css("::text").get(): int(tag.css("::attr(data-tagid)").get())})

        yield{
            "tags": self.gameTags
        }
        print("done")