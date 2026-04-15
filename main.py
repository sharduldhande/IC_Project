from cleanup import cleanup_movies, cleanup_keys
from setup_folders import setup_folders
from Alice import Alice
from Bob import Bob

cleanup_movies()
cleanup_keys()
setup_folders()


alice = Alice("alice_movies")
bob = Bob("bob_movies")

alice.generate_movie_keys()
bob.generate_movie_keys()

alice.publish_movie_keys("alice_keys")
bob.publish_movie_keys("bob_keys")

alice.generate_double_movie_keys("bob_keys")
bob.generate_double_movie_keys("alice_keys")

alice.publish_double_movie_keys("alice_double_keys")
bob.publish_double_movie_keys("bob_double_keys")

common_movies = alice.compare_movies("bob_double_keys")


print("="*100)
print("Number of movies common between Alice and Bob are:")
print(common_movies)
print("="*100)
