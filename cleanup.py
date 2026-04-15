import os
import shutil

def cleanup_movies():

    for folder in ["alice_movies", "bob_movies"]:
        shutil.rmtree(folder, ignore_errors=True)

def cleanup_keys():

    for keyfile in ["alice_keys", "bob_keys", "alice_double_keys", "bob_double_keys"]:
        try:
            os.remove(keyfile)
        except:
            pass

def cleanup_charles():
    shutil.rmtree("charles_movies", ignore_errors=True)


cleanup_movies()
cleanup_keys()
cleanup_charles()
