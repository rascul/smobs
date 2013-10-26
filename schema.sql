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
  name varchar(80) UNIQUE,
  type varchar(20)
);
CREATE TABLE load_item (
  loadid bigserial references load(loadid),
  itemid bigserial references item(itemid),
  quantity integer,
  location varchar(80)
);
CREATE TABLE weapon (
  itemid bigserial references item(itemid) PRIMARY KEY,
  type varchar(20),
  ob integer,
  pb integer,
  weight float,
  hands float,
  rent integer,
  name varchar(80)
);
CREATE TABLE armor (
  itemid bigserial references item(itemid) PRIMARY KEY,
  type varchar(20),
  db integer,
  pb integer,
  moves integer,
  abs float,
  weight float,
  rent integer,
  sheath boolean,
  name varchar(80)
);
CREATE TABLE trink (
  itemid bigserial references item(itemid) PRIMARY KEY,
  type varchar(20),
  db float,
  pb float,
  moves integer,
  weight float,
  rent integer,
  sheath boolean,
  name varchar(80)
);
CREATE TABLE quest_location (
  locationid serial PRIMARY KEY,
  location varchar(80)
);
CREATE TABLE quest (
  questid serial PRIMARY KEY,
  locationid serial references quest_location(locationid),
  mob varchar(80),
  quest text
);
