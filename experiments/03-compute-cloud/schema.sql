DROP TABLE IF EXISTS jobs;
CREATE TABLE jobs (
  id        serial PRIMARY KEY,
  lo        bigint NOT NULL,          -- range start
  hi        bigint NOT NULL,          -- range end
  status    text   NOT NULL DEFAULT 'queued',   -- queued | running | done
  worker    text,
  result    bigint,                   -- primes found in [lo,hi)
  started   timestamptz,
  finished  timestamptz
);
