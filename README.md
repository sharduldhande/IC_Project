# Private Set Intersection Cardinality (PSI-CA) for Movie Matching

This project implements a cryptographic protocol allowing two parties (Alice and Bob) to determine exactly how many movies they have in common (the cardinality of their intersection) without revealing the names or contents of the overlapping movies, nor the rest of their libraries.

## Math Foundations

The project leverages a **Diffie-Hellman based Private Set Intersection Cardinality (DH-PSI-CA)** protocol. It operates in the multiplicative group of integers modulo a prime $p$ (specifically using the 1536-bit safe prime defined in RFC 3526). 

Let Alice's set of movies be $A = \{m_1, m_2, ..., m_{u}\}$ and Bob's set be $B = \{n_1, n_2, ..., n_{v}\}$. Alice and Bob each hold secret large private keys $a$ and $b$, respectively. 

The protocol operates in three main steps:

### 1. Hashing and First Exponentiation
Since the movies are 100MB files, digesting them securely into group elements is vital to efficiency. Rather than sending the movies themselves, both parties stream each file through `SHA-256`, converting it to a 256-bit integer $H(\text{movie})$. This acts as a cryptographic fingerprint mapped into $\mathbb{Z}_p^*$.
* **Alice** computes $X_i = H(m_i)^a \pmod p$ for each movie. She publishes this set as $A'$.
* **Bob** computes $Y_j = H(n_j)^b \pmod p$ for each movie. He publishes this set as $B'$.

### 2. Second Exponentiation (Double Encryption)
Neither party can understand the contents of the opposite party's published set since the Discrete Logarithm Problem heavily guards $H(m)$ and the opposite party lacks the required private key to trace it back. 

To conduct the intersection gracefully via exponentiation commutativity $(x^a)^b \equiv (x^b)^a \pmod p$:
* **Alice** takes Bob's set $B'$ and raises every item to her private key $a$: $Z_{A} = \{ Y_j^a \pmod p \} = \{ H(n_j)^{ba} \pmod p \}$. She publishes $B''$.
* **Bob** takes Alice's set $A'$ and raises every item to his private key $b$: $Z_{B} = \{ X_i^b \pmod p \} = \{ H(m_i)^{ab} \pmod p \}$. He publishes $A''$.

### 3. Calculating the Cardinality
If Alice and Bob share an identical movie ($m_i = n_j$), their resulting double-encrypted hashes will be identical because $H(m_i)^{ab} \equiv H(n_j)^{ba} \pmod p$.
Both parties take the symmetric difference by finding the intersection overlap $|A'' \cap B''|$. Taking the length of this intersection mathematically outputs the cardinality without requiring any more communication.

### How Anonymity / Hiding is Assured
A critical goal is that **neither party learns *which* of their specific movies matched**.
* Even though Alice knows the overlap intersection value $Z$, she does not know Bob's private key $b$. Therefore, she cannot computationally reverse-engineer which of her original single-encrypted keys ($X_i$) Bob used to arrive at $Z$.
* From a system side-channel perspective, preserving the array index positions during iterations would break the linkage anonymity. Our implementation gracefully prevents this correlation. When parsing the exchanged JSON keys, Python converts them into a `set()`. For integers, Python's underlying hashing natively scatters the iteration order deterministically based on their individual mathematical limits ($\pmod{table\_size}$). Because Alice does not know $b$, mapping back $X_i^b$ purely through iteration order resembles a secure random permutation.

## Running the Code

The implementation simulates the entire environment end-to-end, mimicking the data-broker Charles generating personalized test databases of identical format for Alice and Bob, performing the protocol mathematics, and securely wiping the footprint.

**Requirements**:
* Python 3.8+ (No external non-standard dependencies)

To execute the protocol, securely test its cardinality results, and observe the output, simply run the driver file:

```bash
python main.py
```

### Protocol Execution Flow
When you run `main.py`, the following sequences automatically fire:
1. `setup_folders.py`: Acts as the trusted dealer Charles. He creates an overarching random catalog of 30 distinct dummy movie files (`charles_movies`). Charles then randomly allocates a sampled selection of 15 movies exactly to Alice's and Bob's private directories (`alice_movies` and `bob_movies`).
2. **Key Generation**: Both Alice and Bob spawn random secret keys $a$ and $b$ and hash their incoming physical movie bytes in fast memory-safe 8KB chunks. 
3. **Stage 1 Handshake**: The mathematical properties $H(m)^a$ are logged natively to `alice_keys.json` and `bob_keys.json`.
4. **Stage 2 Shuffle**: Both components pull down the opposite party's generated keys independently, compute the double-encryption keys $H(m)^{ab}$, and inject them into `*_double_keys.json` safely. 
5. Overlapping match boundaries are checked implicitly using native binary Set Intersections yielding the total aggregate shared tally.
6. The exact number of identical movies gets printed out seamlessly. 
7. (*Note: The initial start calls `cleanup_movies()` and `cleanup_keys()` automatically to groom standard state tests between each clean run of `main.py`*).

### Collaboration Statement
Our team used Claude (Anthropic) to assist with debugging, ideating, and testing our protocol.
