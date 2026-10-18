# Samples per-core CPU use from /proc/stat while loading 0,1,2,4 cores in 3s phases.
import subprocess, time, json, os
def read():
    r={}
    for l in open('/proc/stat'):
        if l.startswith('cpu') and l[3].isdigit():
            f=l.split(); v=list(map(int,f[1:])); r[int(f[0][3:])]=(sum(v)-v[3]-v[4],sum(v))
    return r
frames=[]; procs=[]; prev=read(); t0=time.time()
def burn(core): return subprocess.Popen(['taskset','-c',str(core),'python3','-c','while 1: pass'])
for phase,n in enumerate([0,1,2,4,0]):
    while len(procs)<n: procs.append(burn(len(procs)))
    while len(procs)>n: procs.pop().kill()
    for _ in range(6):
        time.sleep(0.5); cur=read()
        u=[round(100*(cur[i][0]-prev[i][0])/max(1,cur[i][1]-prev[i][1])) for i in range(4)]
        frames.append({'t':round(time.time()-t0,1),'busy':n,'cores':u,'load':open('/proc/loadavg').read().split()[0]}); prev=cur
for p in procs: p.kill()
print(json.dumps(frames))
