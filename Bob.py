import json
import os
import hashlib
import secrets

#Kivinen, Tero, and Mika Kojo. More modular exponential (modp) diffie-hellman groups for internet key exchange (IKE). No. rfc3526. 2003.

PRIME = int("""
    FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
    29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
    EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
    E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
    EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
    C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
    83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
    670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
    E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
    DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
    15728E5A 8AACAA68 FFFFFFFF FFFFFFFF
    """.replace(" ", "").replace("\n", ""), 16)

class Bob:
    def __init__(self, movie_folder):

        #Rescorla, Eric. "RFC2631: Diffie-Hellman key agreement method." (1999).
        #"X9.42 requires that the private key x be in the interval [2, (q -2)]"

        self.__private_key = 2 + secrets.randbelow((PRIME-2))

        self.__movies = set()

        self.__movie_keys = None
        self.__double_movie_keys = None


        for filename in os.listdir(movie_folder):
            filepath = os.path.join(movie_folder, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as f:
                    hash_obj = hashlib.sha256()
                    while chunk := f.read(8192):
                        hash_obj.update(chunk)
                    file_hash = int(hash_obj.hexdigest(), 16)
                self.__movies.add(file_hash)



    def generate_movie_keys(self):
        movie_keys = set()
        for ahash in self.__movies:
            movie_key = pow(ahash, self.__private_key, PRIME)
            movie_keys.add(movie_key)

        self.__movie_keys = list(movie_keys)

    def generate_double_movie_keys(self, opposite_party_movie_key_filepath):
        with open(opposite_party_movie_key_filepath, 'r') as f:
            opposite_party_movie_keys = set(json.load(f))
        double_movie_keys = set()
        for ahash in opposite_party_movie_keys:
            double_movie_key = pow(ahash, self.__private_key, PRIME)
            double_movie_keys.add(double_movie_key)

        self.__double_movie_keys = list(double_movie_keys)


    def compare_movies(self, opposite_party_double_movie_key_filepath):
        with open(opposite_party_double_movie_key_filepath, 'r') as f:
            opposite_party_double_movie_keys = set(json.load(f))
        common_movies = set(self.__double_movie_keys) & opposite_party_double_movie_keys

        return len(common_movies)


    def publish_movie_keys(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.__movie_keys, f)


    def publish_double_movie_keys(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.__double_movie_keys, f)
