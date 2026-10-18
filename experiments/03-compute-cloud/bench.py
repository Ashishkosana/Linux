# Run the same 48 jobs with 1, 2, 4 and 8 workers; dump per-job timing from the database as JSON.
import subprocess, psycopg2, json, time
JOBS, SPAN, BASE = 48, 60_000_000, 1_000_000_000
def conn(): return psycopg2.connect(host='/tmp', port=5433, dbname='cloud', user='postgres')
runs = []
for w in (1, 2, 4, 8):
    db = conn(); c = db.cursor()
    c.execute(open('schema.sql').read())
    c.executemany("INSERT INTO jobs(lo,hi) VALUES (%s,%s)", [(BASE + i*SPAN, BASE + (i+1)*SPAN) for i in range(JOBS)]); db.commit()
    t0 = time.time()
    ps = [subprocess.Popen(['python3', 'worker.py', f'w{i}']) for i in range(w)]
    for p in ps: p.wait()
    wall = time.time() - t0
    c.execute("""SELECT id, worker, extract(epoch from started - min(started) over ()), extract(epoch from finished - min(started) over ()), result
                 FROM jobs ORDER BY id"""); rows = c.fetchall()
    c.execute("SELECT sum(result), count(*) FROM jobs WHERE status='done'"); tot, n = c.fetchone()
    c.execute('SELECT extract(epoch from max(finished)-min(started)) FROM jobs'); span = float(c.fetchone()[0])
    runs.append(dict(workers=w, wall=round(wall, 2), compute=round(span, 2), total_primes=int(tot), done=n,
                     jobs=[dict(id=r[0], w=r[1], s=round(float(r[2]), 3), e=round(float(r[3]), 3), n=int(r[4])) for r in rows]))
    print(w, 'workers', round(wall, 2), 's', int(tot), 'primes', n, 'jobs', flush=True)
json.dump(runs, open('runs.json', 'w'))
