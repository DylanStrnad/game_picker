import json

from flask import Flask, render_template, request
from markupsafe import escape
from scrapy.crawler import CrawlerProcess
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from spiders.collect_steam_games import InfinitePageSpider

app = Flask(__name__)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# fetch data
with open("games_tags.json") as file:
    tag_data = json.load(file)

REVIEW_SCORES_INDEX = {
    "Overwhelmingly Negative": 0,
    "Very Negative": 1,
    "Negative": 2,
    "Mostly Negative": 3,
    "Mixed": 4,
    "Mostly Positive": 5,
    "Positive": 6,
    "Very Positive": 7,
    "Overwhelmingly Positive": 8,
}


def crawl_page(genre, scrape_amount, review_score):
    print("crawl page")
    # tag_id, scrape_amount, review_score = get_user_input()
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
    process.crawl(InfinitePageSpider, tag_id=genre, scrape_amount=scrape_amount, review_score=review_score)
    process.start()
    print("Crawl finished")


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

def recommend_games(game_description, number_of_results, game_embeddings, cleaned_data):
    input_embedding = model.encode([game_description])
    calc_similarity = cosine_similarity(input_embedding, game_embeddings)[0]
    print(number_of_results)
    # fetches the top results
    top_matches = calc_similarity.argsort()[::-1][:number_of_results]
    results = []
    for idx in top_matches:
        game = cleaned_data[idx]
        score = calc_similarity[idx]
        results.append({
            'game': game['game'].strip(),
            'match_score': f"{score:.2f}",
            'genres':(game['genre']),
            'tags': (game['tags']),
            'review': game['reviews']
        }
        )
    return results

@app.route("/", methods=["GET", "POST"])
@app.route("/result.html", methods=["GET", "POST"])
def home():
    print("home")
    if request.method == "POST":
        genre = request.form.get("genre")
        scrape_amount = request.form.get("scrape_amount")
        review_score = request.form.get("review_score").strip()
        game_description = request.form.get("game_description")
        number_of_results = int(request.form.get("number_of_results"))
        crawl_page(genre, scrape_amount, review_score)
        game_embeddings, cleaned_data = clean_data_and_embed()
        results = recommend_games(game_description, number_of_results, game_embeddings, cleaned_data)
        return render_template("results.html", results=results)
    return render_template("index.html")

# if __name__ == "__main__":
#     while True:
#         crawl_page()
#         embedded_data, cleaned_data = clean_data_and_embed()
#         user_input = input("describe the game your looking for:\n")
#         num_of_results = input("How many games to show in results:\n")
#         recommend_games(user_input, int(num_of_results), embedded_data, cleaned_data)
#         user_input = input("Do you want to try again? [Y/N]").capitalize()
#         try_again = True if user_input == "Y" else False
#         if not try_again:
#             break
