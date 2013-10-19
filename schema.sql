CREATE TABLE smob (
  smobid serial PRIMARY KEY,
  name varchar(80) UNIQUE,
  stab boolean,
  channel varchar(80),
  shortname varchar(80),
  location varchar(80),
  pick integer,
  search integer
);
CREATE TABLE load (
  loadid bigserial PRIMARY KEY,
  smobid serial references smob(smobid),
  who varchar(80),
  date timestamp
);
CREATE TABLE item (
  itemid bigserial PRIMARY KEY,
  name varchar(80)
);
CREATE TABLE load_item (
  loadid bigserial references load(loadid),
  itemid bigserial references item(itemid),
  quantity integer,
  location varchar(80)
);
