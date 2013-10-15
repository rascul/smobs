CREATE TABLE smob (
  smobid serial PRIMARY KEY,
  name varchar(80) UNIQUE,
  stab boolean,
  channel boolean
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
