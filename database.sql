DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS url_checks;

CREATE TABLE urls (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(255) UNIQUE NOT NULL,
  created_at DATE NOT NULL
);

CREATE TABLE url_checks (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  url_id bigint REFERENCES urls(id) NOT NULL,
  status_code VARCHAR(3),
  h1 VARCHAR(255),
  title TEXT,
  description TEXT,
  created_at DATE NOT NULL
);

/*Railway Postresql Command*/
/*To remove data from the main table and all tables
that have foreign key references to the main table,
please, use:
TRUNCATE TABLE urls CASCADE;*/