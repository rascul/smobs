create table smob (
  smobid serial primary key,
  name varchar(80) unique,
  stab boolean,
  channel varchar(80),
  shortname varchar(80),
  location varchar(80),
  pick integer,
  search integer,
  notes text
);
create table load (
  loadid bigserial primary key,
  smobid serial references smob(smobid),
  who varchar(80),
  date timestamp
);
create table item (
  itemid bigserial primary key,
  name varchar(80) unique,
  type varchar(20)
);
create table load_item (
  loadid bigserial references load(loadid),
  itemid bigserial references item(itemid),
  quantity integer,
  location varchar(80)
);
create table weapon (
  itemid bigserial references item(itemid) primary key,
  subtype varchar(20),
  ob integer,
  pb integer,
  weight float,
  hands float,
  rent integer,
  name varchar(80)
);
create table armor (
  itemid bigserial references item(itemid) primary key,
  subtype varchar(20),
  db integer,
  pb integer,
  moves integer,
  abs float,
  weight float,
  rent integer,
  sheath boolean,
  name varchar(80)
);
create table trink (
  itemid bigserial references item(itemid) primary key,
  subtype varchar(20),
  db float,
  pb float,
  moves integer,
  weight float,
  rent integer,
  sheath boolean,
  name varchar(80)
);
create table herb (
  itemid bigserial references item(itemid) primary key,
  name varchar(80),
  locations text,
  weight float,
  rent integer
);
create table potion (
  potionid bigserial primary key,
  itemid bigserial references item(itemid) primary key,
  name varchar(80),
  effect varchar(80),
  weight float,
  rent integer
);
create table ingredient (
  potionid bigserial references potion(potionid),
  itemid bigserial references item(itemid),
  quantity integer,
  name varchar(80)
);
create table food (
  itemid bigserial references item(itemid),
  weight float,
  nibbles integer,
  rent integer
);
create table container (
  itemid bigserial references item(itemid),
  weight float,
  capacity float,
  rent integer
);
create table liquid_container (
  itemid bigserial references item(itemid),
  weight_empty float,
  weight_full float,
  sips integer,
  rent integer
);
create table keys (
  itemid bigserial references item(itemid),
  opens varchar(80),
  loads varchar(80)
);
create table angreal (
  itemid bigserial references item(itemid),
  sex varchar(1),
  weight float,
  rent integer
);
create table light (
  itemid bigserial references item(itemid),
  weight float,
  duration integer,
  rent integer
);
create table horseeq (
  itemid bigserial references item(itemid),
  slot varchar(10),
  moves integer,
  weight float,
  rent integer
);

  

