-- Sample development data for HT Status
-- This file is loaded after init-db.sql in development environments
-- Provides test data for development and testing

-- Only load in development/test environments
DO $$
BEGIN
  -- Check if this is a development/test database
  IF current_database() LIKE '%test%' OR current_database() LIKE '%dev%' OR current_database() = 'htplanner' THEN

    -- Insert sample user data (if Users table exists and is empty)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
      INSERT INTO users (id, username, email, created_at)
      SELECT 1, 'dev_user', 'dev@htstatus.local', NOW()
      WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = 1);
    END IF;

    -- Insert sample group data (if Groups table exists)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'groups') THEN
      INSERT INTO groups (id, name, description, created_at)
      SELECT 1, 'Development Team', 'Sample development team for testing', NOW()
      WHERE NOT EXISTS (SELECT 1 FROM groups WHERE id = 1);
    END IF;

    RAISE NOTICE 'Development sample data loaded for database: %', current_database();
  ELSE
    RAISE NOTICE 'Skipping sample data - not a development database: %', current_database();
  END IF;
END
$$;
