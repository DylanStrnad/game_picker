import scrapy
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider


class InfinitePageSpider(CrawlSpider):
    """
    Spider to crawl steam page
    """

    name = "scroll_and_collect"

    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "args": [
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            "headless": False,
        },
        "LOG_LEVEL": "INFO",
    }
    print("custom_settings")

    def __init__(self, tag_id="", **kwargs):
        self.start_urls = [f"https://store.steampowered.com/search/?hwtype=0&tags={tag_id}"]
        super().__init__(**kwargs)

    async def start(self):
        print("start requests")
        yield scrapy.Request(
            url=f"{self.start_urls[0]}",
            meta=dict(
                playwright=True,
                playwright_include_page=True,
            ),
            callback=self.parse,
        )

    async def parse(
        self,
        response,
    ):
        print("parse")
        page = response.meta["playwright_page"]
        page.set_default_timeout(10000)

        await page.wait_for_timeout(5000)
        try:
            last_position = await page.evaluate("window.scrollY")

            while True:
                # scroll by 700 while not at the bottom
                await page.evaluate("window.scrollBy(0, 1000)")
                # await page.wait_for_timeout(750) # wait for 750ms for the request to complete
                current_position = await page.evaluate("window.scrollY")

                if current_position >= 10000:
                    print("fetch the top results.")
                    break

                last_position = current_position
                # break #temporary

        except Exception as error:
            print(f"Error: {error}")
            pass

        print("Getting content")
        content = await page.content()

        print("Parsing content")
        selector = Selector(text=content)

        matches = selector.css("a.search_result_row")
        print("matches:", len(matches))

        for request in self.parse_link(selector):
            print("yielding request")
            yield request

    def parse_link(self, selector):
        print("parse_link")
        matches = selector.css("a.search_result_row")
        print("matches:", len(matches))
        for game in selector.css("a.search_result_row"):
            url = game.css("::attr(href)").get()
            yield scrapy.Request(url, callback=self.parse_game)
        print("done")

    def parse_game(self, response):
        print("parse game")
        name = response.xpath(
            '//div[@id="genresAndManufacturer"]/b[contains(text(), "Title:")]/following-sibling::text()[1]'
        ).get()
        genre = response.css("#genresAndManufacturer span[data-panel] a::text").getall()
        tags = response.css("div.glance_tags a.app_tag::text").getall()
        tags = [tag.strip() for tag in tags]
        reviews = response.css("span.game_review_summary.positive::text").get()
        # print(reviews)
        yield {"game": name, "genre": genre, "tags": tags, "reviews": reviews}
        # print("parse_game")
