drop table if exists emails;
create table emails(
  id integer primary key autoincrement,
  email text not null unique,
  validated boolean not null,
  confirmation_token text not null unique,
  friendbuy_id integer
);