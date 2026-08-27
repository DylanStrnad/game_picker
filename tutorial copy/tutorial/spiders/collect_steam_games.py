import scrapy
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider

review_scores_index = {
    "Overwhelmingly Negative": 0, "Very Negative": 1, "Negative": 2, "Mostly Negative": 3, "Mixed": 4, "Mostly Positive": 5, "Positive": 6, "Very Positive": 7, "Overwhelmingly Positive": 8
}


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

    def __init__(self, tag_id="", scrape_amount=50, review_score="any", **kwargs):
        self.start_urls = [f"https://store.steampowered.com/search/?hwtype=0&tags={tag_id}"]
        self.scrape_amount = scrape_amount
        self.review_score = review_score
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
        # print("parse")
        page = response.meta["playwright_page"]
        page.set_default_timeout(10000)
        try:
            print("Fetching Results...")
            while True:
                # scroll by 1000
                await page.evaluate("window.scrollBy(0, 1000)")
                current_position = await page.evaluate("window.scrollY")
                content = await page.content()
                selector = Selector(text=content)
                matches = selector.css("a.search_result_row")

                if len(matches) >= self.scrape_amount:
                    break

        except Exception as error:
            print(f"Error: {error}")
            pass

        print("Getting content")
        content = await page.content()

        print("Parsing content")
        selector = Selector(text=content)

        matches = selector.css("a.search_result_row")
        print("matches:", len(matches))

        print("yielding request...")
        for request in self.parse_link(selector):
            yield request

    def parse_link(self, selector):
        # print("parse_link")
        for game in selector.css("a.search_result_row"):
            url = game.css("::attr(href)").get()
            yield scrapy.Request(url, callback=self.parse_game)

    def parse_game(self, response):
        # print("parse game")
        name = response.xpath(
            '//div[@id="genresAndManufacturer"]/b[contains(text(), "Title:")]/following-sibling::text()[1]'
        ).get()
        genre = response.css("#genresAndManufacturer span[data-panel] a::text").getall()
        tags = response.css("div.glance_tags a.app_tag::text").getall()
        tags = [tag.strip() for tag in tags]
        reviews = response.css("span.game_review_summary.positive::text").get()
        if reviews is None:
            return # skip games with no reviews
        if review_scores_index[reviews] >= review_scores_index[self.review_score]:
            yield {"game": name, "genre": genre, "tags": tags, "reviews": reviews}
