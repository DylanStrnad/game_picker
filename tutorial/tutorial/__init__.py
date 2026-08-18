import json

from scrapy.crawler import CrawlerProcess
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from spiders.infinite_scroll import InfinitePageSpider

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# fetch data
with open("games_tags.json") as file:
    tag_data = json.load(file)

user_input = input(
    "what genre of game do you want to play? select from any steam game tag [indie, multiplayer, singleplayer, action, adeventure, rpg, etc]"
)
#get the tagID
tag_id = tag_data[0]["tags"][user_input]

user_input = input(
    "how many games to scrape? (More will take longer, but provide more accurate results)"
)
scrape_amount = int(user_input)

process = CrawlerProcess(
    settings={
        "FEEDS": {
            "games.json": {
                "format": "json",
                "overwrite": True,
            },
        },
    }
)
process.crawl(InfinitePageSpider, tag_id=tag_id, scrape_amount=scrape_amount)
process.start()

with open("games.json") as file:
    data = json.load(file)

cleaned_data = [item for item in data if item.get("game")]

game_descriptions = [
    f"Title: {g['game'].strip()}. Genres: {', '.join(g['genre'])}. Tags: {', '.join(g['tags'])}. Reviews: {g['reviews']}."
    for g in cleaned_data
]
# print(game_descriptions)

game_embeddings = model.encode(game_descriptions)
# print(game_embeddings)


def recommend_games(user_input, num_of_results):
    input_embedding = model.encode([user_input])
    calc_similarity = cosine_similarity(input_embedding, game_embeddings)[0]

    #fetches the top results
    top_matches = calc_similarity.argsort()[::-1][:num_of_results]
    for idx in top_matches:
        game = cleaned_data[idx]
        score = calc_similarity[idx]
        print(f"• {game['game'].strip()} (Match Score: {score:.2f})")
        print(f"  Genres: {', '.join(game['genre'])}")
        print(f"  tags: {', '.join(game['tags'])}")
        print(f"  Reviews: {game['reviews']}\n")


# Example Usage
if __name__ == "__main__":
    user_input = input("describe the game your looking for:\n")
    num_of_results = input("How many games to show in results:")
    recommend_games(user_input, int(num_of_results))
