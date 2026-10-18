#!/bin/sh
# Start a throwaway PostgreSQL 16 on port 5433 (data in /tmp/pgdata, owned by user postgres)
BIN=/usr/lib/postgresql/16/bin
[ -d /tmp/pgdata ] || { mkdir /tmp/pgdata && chown postgres /tmp/pgdata && su postgres -c "$BIN/initdb -D /tmp/pgdata -A trust >/dev/null"; }
su postgres -c "$BIN/pg_ctl -D /tmp/pgdata -o '-p 5433 -k /tmp' -l /tmp/pg.log -w start" >/dev/null
su postgres -c "psql -h /tmp -p 5433 -tc \"select 1 from pg_database where datname='cloud'\" postgres" | grep -q 1 || su postgres -c "createdb -h /tmp -p 5433 cloud"
echo "postgres ready: $(su postgres -c "psql -h /tmp -p 5433 -tAc 'select version()' cloud" | cut -c1-40)"
