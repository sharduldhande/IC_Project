# Project Specification: Private Set Intersection (PSI)

## Team Members
Vinay Gupta & Shardul Dhande

---

## 1. Problem Statement

Alice and Bob each receive 15 movies (each ~100 MB) from a distributor named Charles. They suspect Charles is not personalizing their lists and want to identify exactly which movies they have in common. However, neither party trusts the other enough to reveal the contents of their full movie libraries. Our goal is to implement a **Private Set Intersection (PSI)** protocol: both parties correctly learn which movies they share, while neither party learns anything about the other party's movies that are *not* in the intersection.

---

## 2. Security Goals

We define the following formal security goals for this protocol:

### 2.1 Privacy of Alice's Non-Intersection Elements
After the protocol concludes, Bob learns the blinded fingerprints of the matched movies `{H(m)^(ab) : m ∈ A ∩ B}` — the intended PSI output — but learns **nothing** about any of Alice's movies that are *not* in the intersection. He cannot distinguish Alice's exclusive movies from any other movies not in her set.

### 2.2 Privacy of Bob's Non-Intersection Elements
Symmetrically, Alice learns the blinded fingerprints of matched movies but learns **nothing** about any of Bob's movies that are not in the intersection.

### 2.3 Correctness
If both parties execute the protocol honestly, both parties correctly identify every movie that is byte-for-byte identical between their two sets, and no false matches are reported.

### 2.4 Known Limitations and Assumptions
- **No active security**: The protocol is proven secure only against **passive adversaries** who follow the protocol honestly but may attempt to extract additional information from their view. Active attacks (e.g., sending malformed exponentials) are out of scope.
- **No authentication**: There is no mechanism to verify that published keys come from the claimed party. A man-in-the-middle attack is ruled out of scope.
- **Blinded output, not plaintext**: The intersection is revealed as double-encrypted blinded fingerprints `{H(m)^(ab)}`, not as raw movie identities. Recovering actual movie content from these values requires solving the Discrete Logarithm Problem. The count `|A ∩ B|` is printed as a human-readable summary.
- **Set-size leakage**: Both parties can observe the number of published key values (15 each), revealing set sizes, which is considered public in our model.

---

## 3. Threat Model

- **Adversary type**: Both Alice and Bob follow the protocol steps exactly as specified, but each independently attempts to extract additional information from all messages they receive.
- **No shared initial state**: Alice and Bob do not share any keys, parameters, or secrets prior to the protocol. The only shared value is the public prime `p` (specified in the protocol parameters below), which is published in the RFC and known to all parties.
- **Passive channel**: Messages are exchanged over a channel, and in our case we assume the channel is authenticated (neither party can forge the other's messages), but not necessarily confidential, as the single-encrypted keys `A'` and `B'` are deliberately made public.
- **Charles is not a party**: Charles's behavior is irrelevant to the privacy goals for our interpretation and implementation of the protocol; the protocol only concerns what Alice and Bob can learn from each other.

---

## 4. Protocol Specification

### 4.1 Parameters

| Parameter | Value |
|-----------|-------|
| Group | Multiplicative group Z*_p |
| Prime `p` | 1536-bit MODP Group from RFC 3526 (Group 5) |
| Hash function | SHA-256 (outputs 256-bit integer) |
| Private key range | Uniform random in [2, p-2] |
| Key generation | Python `secrets.randbelow` (CSPRNG) |

**RFC 3526 Group 5 Prime (hexadecimal):**
```
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
```

### 4.2 Notation

| Symbol | Meaning |
|--------|---------|
| A = {m₁, …, m₁₅} | Alice's set of movies (as SHA-256 file hashes → integers in Z*_p) |
| B = {n₁, …, n₁₅} | Bob's set of movies (as SHA-256 file hashes → integers in Z*_p) |
| a | Alice's secret private key, uniform in [2, p-2] |
| b | Bob's secret private key, uniform in [2, p-2] |
| H(m) | SHA-256 hash of file m, interpreted as a 256-bit integer |
| A' | {H(mᵢ)^a mod p : mᵢ ∈ A} — Alice's first-encrypted set |
| B' | {H(nⱼ)^b mod p : nⱼ ∈ B} — Bob's first-encrypted set |
| A'' | {xᵢ^b mod p : xᵢ ∈ A'} = {H(mᵢ)^(ab) mod p} — double-encrypted Alice |
| B'' | {yⱼ^a mod p : yⱼ ∈ B'} = {H(nⱼ)^(ba) mod p} — double-encrypted Bob |

### 4.3 Protocol Steps

```
Alice                                              Bob
  |                                                 |
  |-- generates secret key a                        |-- generates secret key b
  |-- for each mᵢ ∈ A: computes H(mᵢ)^a mod p     |-- for each nⱼ ∈ B: computes H(nⱼ)^b mod p
  |                                                 |
  |   publishes A' = {H(mᵢ)^a mod p}  -----------> |
  |           <------------------------  publishes B' = {H(nⱼ)^b mod p}
  |                                                 |
  |-- for each yⱼ ∈ B': computes yⱼ^a mod p        |-- for each xᵢ ∈ A': computes xᵢ^b mod p
  |   (produces B'' = {H(nⱼ)^(ba) mod p})          |   (produces A'' = {H(mᵢ)^(ab) mod p})
  |                                                 |
  |   publishes B''            ──────────────────>  |
  |           <────────────────────────────────     | publishes A''
  |                                                 |
  |-- output: B'' ∩ A''  (the PSI result)            |-- (optionally output: A'' ∩ B'')
```

**Commutativity property**: Because modular exponentiation is commutative,
```
H(mᵢ)^(ab) mod p  =  H(mᵢ)^(ba) mod p
```
Therefore an element appears in both A'' and B'' **if and only if** the same movie mᵢ = nⱼ exists in both original sets.

### 4.4 Output

The PSI output is the set `B'' ∩ A'' = {H(m)^(ab) mod p : m ∈ A ∩ B}` — the double-encrypted fingerprints of all shared movies. Alice computes this intersection and reports its size as a human-readable count. Bob can independently compute `A'' ∩ B''` and obtain the identical set. The actual movie identities are protected by the Discrete Logarithm Problem — neither party can recover movie content from a blinded fingerprint without solving DLP.

---

## 5. Security Analysis

### 5.1 Hardness Assumption
Security of this protocol relies on the **Decisional Diffie-Hellman (DDH) assumption** in the group Z*_p with the RFC 3526 Group 5 1536-bit prime. The DDH assumption states that for a uniformly random secret exponent `a`, the tuple (g, g^x, g^a, g^(xa)) is computationally indistinguishable from (g, g^x, g^a, g^r) for a random r. This is believed to hold for the 1536-bit MODP group.

### 5.2 Privacy of Alice's Non-Intersection Elements Against Bob

**What Bob observes**: his own set B, A' = {H(mᵢ)^a mod p}, and A'' = {H(mᵢ)^(ab) mod p}.

**PSI security claim**: Bob correctly learns the blinded intersection `{H(m)^(ab) : m ∈ A ∩ B}` (the intended output), but learns **nothing** about Alice's non-intersection movies `A \ B`.

**Why Bob cannot learn about Alice's exclusive movies**:
- From A', Bob sees blinded hashes. To test whether a specific movie m_guess is in Alice's set, he would need to compute `H(m_guess)^a mod p` and check membership in A'. This requires Alice's secret key `a` — without it, this is the Computational Diffie-Hellman (CDH) problem in a 1536-bit group.
- From A'', Bob sees `{H(mᵢ)^(ab)}`. Bob knows b, so he can compute `(H(mᵢ)^(ab))^(b⁻¹ mod (p-1))` to recover A' — but he already has A'. Even with A', recovering H(mᵢ) requires solving DLP.
- **Bob does correctly learn which A' entries are in the intersection** (he built the A' → A'' mapping himself during `generate_double_movie_keys`). This is the intended PSI behavior — Bob identifies the matched blinded elements. He cannot trace these back to actual movie identities without solving DLP.
- For Alice's non-matched movies: their blinded entries in A' are computationally indistinguishable from random group elements under DDH. Bob gains zero information about them.

Under DDH, Bob learns the blinded intersection fingerprints and nothing about Alice's non-intersection movies.

### 5.3 Privacy of Bob's Non-Intersection Elements Against Alice

By the symmetric structure of the protocol, an identical argument holds for Alice's view {A', B', B''}. Alice correctly learns the blinded intersection fingerprints. Under DDH, she learns nothing about Bob's movies in `B \ A`.

### 5.4 Correctness

**Claim**: The computed value `|B'' ∩ A''|` equals the true `|A ∩ B|`.

**Proof**:
- For any mᵢ ∈ A ∩ B, H(mᵢ) = H(nⱼ) for some nⱼ ∈ B (since SHA-256 is deterministic and collision-resistant).
- Therefore H(mᵢ)^(ab) mod p = H(nⱼ)^(ba) mod p, so this value appears in both A'' and B''.
- For any mᵢ ∈ A \ B (exclusive to Alice), H(mᵢ) ≠ H(nⱼ) for all nⱼ ∈ B. Since SHA-256 is collision-resistant, H(mᵢ)^(ab) ≠ H(nⱼ)^(ab) mod p with overwhelming probability (a collision would require either a SHA-256 collision or the DLP solution). So this value is in A'' but not B''.
- The same argument applies for elements exclusive to Bob's set.
- Therefore `|A'' ∩ B''| = |A ∩ B|`.

### 5.5 What Bob Learns (PSI Output)

In a PSI protocol, both parties are *entitled* to learn which set elements are in the intersection. During `generate_double_movie_keys`, Bob iterates over A' and builds the mapping `H(mᵢ)^a → H(mᵢ)^(ab)`. When he computes `A'' ∩ B''`, he can identify which specific entries of A' correspond to matched movies. This is **correct PSI behavior**, not a leakage — it is the designed output of the protocol.

What Bob cannot do beyond this:
- **Recover movie content**: Knowing `H(mᵢ)^a` for a matched entry does not reveal `H(mᵢ)` or the movie file — DLP prevents inversion.
- **Test non-intersection guesses**: Testing whether a movie `m_guess ∉ A ∩ B` is in Alice's exclusive set requires computing `H(m_guess)^a` without knowing `a` — CDH prevents this.
- **Learn anything about A \ B**: Alice's non-matched entries in A' are computationally indistinguishable from random group elements under DDH.

---

## 6. Implementation Details

### 6.1 File Hashing
Each movie file is hashed using SHA-256 in streaming 8 KB chunks to avoid loading ~100 MB files entirely into memory. For simplicity and to keep the repository lightweight we use smaller files in practice, but the logic holds the same:
```python
hash_obj = hashlib.sha256()
while chunk := f.read(8192):
    hash_obj.update(chunk)
file_hash = int(hash_obj.hexdigest(), 16)
```
The resulting 256-bit integer is used directly as the group element `H(m)` in Z*_p.

### 6.2 Private Key Generation
Private keys are generated using Python's `secrets.randbelow`, which draws from the OS CSPRNG (`/dev/urandom` on macOS/Linux):
```python
self.__private_key = 2 + secrets.randbelow((PRIME - 2))
```
This ensures the key is uniform in [2, p-2], consistent with the X9.42 recommendation cited in RFC 2631.

### 6.3 Modular Exponentiation
Python's built-in `pow(base, exp, mod)` uses fast binary exponentiation (square-and-multiply) and is implemented in C, making it suitable for 1536-bit modular exponentiations.

### 6.4 Key Encapsulation
Private keys are stored as Python instance attributes with the name-mangled prefix `__` (double underscore), ensuring Python's name mangling prevents accidental external access. The key is never written to disk.

### 6.5 Inter-Party Communication (Simulation)
In this simulation, "communication" between Alice and Bob is done via JSON files on the filesystem. In a real deployment, these would be transmitted over a network channel. The files used are:

| File | Contents |
|------|----------|
| `alice_keys` | A' = Alice's single-encrypted hashes (list of integers) |
| `bob_keys` | B' = Bob's single-encrypted hashes |
| `alice_double_keys` | A'' = Alice's double-encrypted hashes |
| `bob_double_keys` | B'' = Bob's double-encrypted hashes |

---

## 7. How to Run

**Requirements**: Python 3.8+ (no external dependencies)

```bash
python main.py
```

This will:
1. Clean up any prior run artifacts.
2. Create 30 dummy movie files as Charles's catalog.
3. Randomly assign 15 movies each to Alice and Bob.
4. Execute the full DH-PSI protocol.
5. Print the number of common movies.

---

## 8. Limitations and Future Work

| Limitation | Description |
|------------|-------------|
| Passive adversaries only | Active adversaries could send malformed exponentials. A malicious-secure protocol would require zero-knowledge proofs of correct exponentiation. |
| No authentication | A man in the middle could replace A' with a different set. |
| Small test files | The simulation uses tiny text files; real 100 MB movie files would make the SHA-256 streaming step non-trivial but the protocol proof and implementation stays the same as it is now. |
| No output verification by Bob | Only Alice computes and prints the result; Bob could independently compute |A'' ∩ B''| for mutual verification. |

---

## 9. References

1. Kivinen, T., and Kojo, M. "More Modular Exponential (MODP) Diffie-Hellman Groups for Internet Key Exchange (IKE)." RFC 3526, March 2003. https://www.rfc-editor.org/rfc/rfc3526
2. Rescorla, E. "Diffie-Hellman Key Agreement Method." RFC 2631, June 1999. https://www.rfc-editor.org/rfc/rfc2631
3. Freedman, M. J., Nissim, K., and Pinkas, B. "Efficient Private Matching and Set Intersection." *EUROCRYPT 2004*, LNCS 3027, pp. 1–19.
4. Python `secrets` module documentation. https://docs.python.org/3/library/secrets.html
5. Python `hashlib` module documentation. https://docs.python.org/3/library/hashlib.html
6. Protocol, spec, and research assisted for ideation and implementation by Claude (Anthropic).
