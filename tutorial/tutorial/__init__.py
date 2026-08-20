import json

from scrapy.crawler import CrawlerProcess
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from spiders.collect_steam_games import InfinitePageSpider

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# fetch data
with open("games_tags.json") as file:
    tag_data = json.load(file)

REVIEW_SCORES_INDEX = {
    "Overwhelmingly Negative": 0, "Very Negative": 1, "Negative": 2, "Mostly Negative": 3, "Mixed": 4, "Mostly Positive": 5, "Positive": 6, "Very Positive": 7, "Overwhelmingly Positive": 8
}

def get_user_input():
    tag_id = None
    while tag_id is None:
        genre = input(
            "what genre of game do you want to play? select from any steam game tag [Indie, Multiplayer, Singleplayer, Action, Adeventure, RPG, etc]\n" \
            "to show list of tags - enter: list\n"
        )
        if genre == "list":
            #print tags
            print(list(tag_data[0]["tags"].keys()))
        else:
            try:
                tag_id = tag_data[0]["tags"][genre]
            except KeyError:
                print("Unknown steam tag. Try again")
        
    scrape_amount = None
    while scrape_amount is None:
        scrape_amount_input = input(
            "how many games to scrape? (More will take longer, but provide more accurate results)"
        )
        try:
            scrape_amount = int(scrape_amount_input)
        except ValueError:
            print("invalid number. Try again")

    review_score = None
    while review_score is None:
        review_score_input = input("minimum review score for game [very negative, negative, mixed, postive, very positive, overwhelmingly positive]").title()
        try: 
            REVIEW_SCORES_INDEX[review_score_input]
        except KeyError:
            print("invalid review score. Try again")
            continue

        review_score = review_score_input
    return tag_id, scrape_amount, review_score

def crawl_page():
    tag_id, scrape_amount, review_score = get_user_input()
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
    while True:
        crawl_page()
        embedded_data, cleaned_data = clean_data_and_embed()
        user_input = input("describe the game your looking for:\n")
        num_of_results = input("How many games to show in results:\n")
        recommend_games(user_input, int(num_of_results), embedded_data, cleaned_data)
        user_input = input("Do you want to try again? [Y/N]").capitalize()
        try_again = True if user_input == "Y" else False
        if not try_again:
            break


