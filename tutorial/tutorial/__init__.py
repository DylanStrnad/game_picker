# import json

# from scrapy.crawler import CrawlerProcess
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from spiders.infinite_scroll import InfinitePageSpider

# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# gameTags = {"singleplayer": 4182, "multiplayer": 3859, "indie": 492, "action": 19, "rpg": 122}

# user_input = input(
#     "what genre of game do you want to play? select from: [singleplayer, multiplayer, indie, action, or rpg]"
# )
# tag_id = gameTags.get(user_input)

# user_input = input(
#     "how many games to scrape? (More will take longer, but provide more accurate results)"
# )
# scrape_amount = int(user_input)

# process = CrawlerProcess(
#     settings={
#         "FEEDS": {
#             "games.json": {
#                 "format": "json",
#                 "overwrite": True,
#             },
#         },
#     }
# )
# process.crawl(InfinitePageSpider, tag_id=tag_id, scrape_amount=scrape_amount)
# process.start()

# with open("games.json") as file:
#     data = json.load(file)

# cleaned_data = [item for item in data if item.get("game")]

# game_descriptions = [
#     f"Title: {g['game'].strip()}. Genres: {', '.join(g['genre'])}. Tags: {', '.join(g['tags'])}. Reviews: {g['reviews']}."
#     for g in cleaned_data
# ]
# print(game_descriptions)

# game_embeddings = model.encode(game_descriptions)
# print(game_embeddings)


# def recommend_games(user_input):
#     input_embedding = model.encode([user_input])
#     calc_similarity = cosine_similarity(input_embedding, game_embeddings)[0]

#     top_matches = calc_similarity.argsort()[::-1][:3]
#     for idx in top_matches:
#         game = cleaned_data[idx]
#         score = calc_similarity[idx]
#         print(f"• {game['game'].strip()} (Match Score: {score:.2f})")
#         print(f"  Genres: {', '.join(game['genre'])}")
#         print(f"  tags: {', '.join(game['tags'])}")
#         print(f"  Reviews: {game['reviews']}\n")


# # Example Usage
# if __name__ == "__main__":
#     user_input = input("describe the game your looking for:\n")
#     recommend_games(user_input)
