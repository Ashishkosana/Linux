# A worker: claim one queued job at a time with SKIP LOCKED, compute, write the result back.
import sys, psycopg2, numpy as np
name = sys.argv[1]
db = psycopg2.connect(host='/tmp', port=5433, dbname='cloud', user='postgres'); db.autocommit = False
cur = db.cursor()
def count_primes(lo, hi):                     # sieve of Eratosthenes over [lo,hi) using numpy
    n = int(hi**0.5) + 1
    small = np.ones(n + 1, bool); small[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if small[i]: small[i*i::i] = False
    seg = np.ones(hi - lo, bool)
    for p in np.nonzero(small)[0]:
        s = max(p * p, ((lo + p - 1) // p) * p); seg[s - lo::p] = False
    seg[:max(0, 2 - lo)] = False
    return int(seg.sum())
while True:
    cur.execute("""UPDATE jobs SET status='running', worker=%s, started=clock_timestamp()
                   WHERE id = (SELECT id FROM jobs WHERE status='queued' ORDER BY id
                               FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING id, lo, hi""", (name,))
    row = cur.fetchone(); db.commit()
    if not row: break
    jid, lo, hi = row
    res = count_primes(lo, hi)
    cur.execute("UPDATE jobs SET status='done', result=%s, finished=clock_timestamp() WHERE id=%s", (res, jid))
    db.commit()
