-- Row count of every table, one "table|count" line each. Used to check that a
-- restored database matches the original (see DEPLOYMENT.md):
--   psql -At -d htplanner -f table_counts.sql > counts.txt
SELECT string_agg(format('SELECT %L, count(*) FROM %I', tablename, tablename), ' UNION ALL ' ORDER BY tablename) AS q
FROM pg_tables WHERE schemaname = 'public' \gset
:q
