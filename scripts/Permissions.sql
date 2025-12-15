GRANT USAGE ON SCHEMA warehouse TO manitkalpeshshah;
-- Grants permission of schema

GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA warehouse TO manitkalpeshshah;
-- Gives permission to select, insert and update the data from the warehouse schema

ALTER DEFAULT PRIVILEGES IN SCHEMA warehouse
GRANT SELECT, INSERT, UPDATE ON TABLES TO manitkalpeshshah;
-- Future table permission will be auto granted