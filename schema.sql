drop table if exists emails;
create table emails(
  id integer primary key autoincrement,
  email text not null unique,
  validated boolean not null
);