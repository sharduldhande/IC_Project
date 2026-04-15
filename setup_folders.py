import os
import shutil
import random

def setup_folders():

    os.makedirs("alice_movies", exist_ok=True)
    os.makedirs("bob_movies", exist_ok=True)

    if not os.path.exists("charles_movies"):
        os.makedirs("charles_movies")
        for i in range(1, 31):
            with open(f"charles_movies/file{i}.txt", "w") as f:
                f.write(f"content {i}")

    charles_movies = os.listdir("charles_movies")

    alice_movies = random.sample(charles_movies, 15)
    bob_movies = random.sample(charles_movies, 15)

    for movie in alice_movies:
        shutil.copy(f"charles_movies/{movie}", "alice_movies/")

    for movie in bob_movies:
        shutil.copy(f"charles_movies/{movie}", "bob_movies/")
