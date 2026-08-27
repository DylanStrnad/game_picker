import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    async def start(self):
        url = "https://store.steampowered.com/search/"
        # tag = getattr(self, "tag", None)
        # if tag is not None:
        #     url = url + "tag/" + tag
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        # for tag in response.css("div.tag_browse_tag"):
        #     yield{
        #         "tag": tag.css("::text").get()
        #     }
        matches = response.css("a.search_result_row")
        print("matches:", len(matches))
        for game in response.css("a.search_result_row"):
            url = game.css("::attr(href)").get()
            # print(url)
            # print(name)
            yield scrapy.Request(url, self.parse_game)
        print("done")

    def parse_game(self, response):
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
