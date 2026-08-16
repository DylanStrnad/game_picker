# import json
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# with open("games.json", "r") as file:
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
#         print(f"  Reviews: {game['reviews']}\n")

# # Example Usage
# if __name__ == "__main__":
#     user_input = input("what kind of game do you want to play? ")
#     recommend_games(user_input)
