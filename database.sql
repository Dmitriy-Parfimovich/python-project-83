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
1 step - DROP TABLE IF EXISTS url_checks;
2 step - DROP TABLE IF EXISTS urls;
(TRUNCATE TABLE urls CASCADE; - deletes data from tables, 
but with empty tables, the column "id" does not start from "1"*/