CREATE TABLE smob (
  smobid INTEGER PRIMARY KEY,
  name TEXT UNIQUE
);

CREATE TABLE load (
  smobid INTEGER,
  item TEXT,
  count INTEGER,
  date TEXT,
  FOREIGN KEY(smobid) REFERENCES smob(id)
);

CREATE TABLE item (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  type TEXT,
  found_in TEXT
);

CREATE TABLE 