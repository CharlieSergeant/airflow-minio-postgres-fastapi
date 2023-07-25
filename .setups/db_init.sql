-- Check if the "airflow" database exists
SELECT db FROM pg_database WHERE db = 'airflow';

-- If the "airflow" database does not exist, create it
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE db = 'airflow') THEN
    CREATE DATABASE airflow;
  END IF;
END $$;