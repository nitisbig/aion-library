"""Robin's criterion (s27): sigma(n) / (n ln ln n) for 3 <= n <= 10^5 against e^gamma. RH holds iff
sigma(n) < e^gamma n ln ln n for every n > 5040 (G. Robin, 1984). Every value here is computed from a divisor sieve."""
from functools import lru_cache

import numpy as np

EG = float(np.exp(np.euler_gamma))           # e^gamma = 1.7810724...
NMAX = 100_000


@lru_cache(maxsize=1)
def data(nmax=NMAX):
    s = np.zeros(nmax + 1, dtype=np.int64)
    for d in range(1, nmax + 1):
        s[d::d] += d
    n = np.arange(3, nmax + 1)
    r = s[3:] / (n * np.log(np.log(n)))
    return n, s[3:], r


def check():
    n, s, r = data()
    above = n[r >= EG]
    assert above.max() == 5040 and s[n == 5040][0] == 19344, above.max()
    return above
