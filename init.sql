-- This is used to initialize the db and tables required
-- This may be a desctuctive operation.

CREATE TABLE IF NOT EXISTS obituaries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(100),
  date_of_birth DATE,
  date_of_death DATE,
  content TEXT,
  author VARCHAR(100),
  submission_date DATETIME DEFAULT CURRENT_TIMESTAMP, -- Should default to the time that the db gets the data
  slug VARCHAR(255)  UNIQUE -- For SEO, I'm a SEO bro now!
);
