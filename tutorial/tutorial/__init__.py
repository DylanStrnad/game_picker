import json

from scrapy.crawler import CrawlerProcess
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from spiders.collect_steam_games import InfinitePageSpider

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# fetch data
with open("games_tags.json") as file:
    tag_data = json.load(file)

def crawl_page():
    genre = input(
        "what genre of game do you want to play? select from any steam game tag [indie, multiplayer, singleplayer, action, adeventure, rpg, etc]"
    )

    #get the tagID
    tag_id = tag_data[0]["tags"][genre]

    scrape_amount = input(
        "how many games to scrape? (More will take longer, but provide more accurate results)"
    )
    scrape_amount = int(scrape_amount)

    review_score = input("minimum review score for game [very negative, negative, mixed, postive, very positive, overwhelmingly positive]")

    # create web crawler
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
    # pass user defined arguments
    process.crawl(InfinitePageSpider, tag_id=tag_id, review_score=review_score, scrape_amount=scrape_amount)
    process.start()

def clean_data_and_embed():
    with open("games.json") as file:
        data = json.load(file)

    cleaned_data = [item for item in data if item.get("game")]

    game_descriptions = [
        f"Title: {g['game'].strip()}. Genres: {', '.join(g['genre'])}. Tags: {', '.join(g['tags'])}. Reviews: {g['reviews']}."
        for g in cleaned_data
    ]

    game_embeddings = model.encode(game_descriptions)
    return game_embeddings, cleaned_data


def recommend_games(user_input, num_of_results, game_embeddings, cleaned_data):
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

if __name__ == "__main__":
    crawl_page()
    embedded_data, cleaned_data = clean_data_and_embed()
    user_input = input("describe the game your looking for:\n")
    num_of_results = input("How many games to show in results:\n")
    recommend_games(user_input, int(num_of_results), embedded_data, cleaned_data)
