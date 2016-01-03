/* DROP TABLE users; /**/
CREATE TABLE IF NOT EXISTS
users (
  user_id INTEGER PRIMARY KEY,
  name TEXT,
  image BLOB,
  logged_in INTEGER DEFAULT 0,
  event_when INTEGER
);

/* DROP TABLE cards; /**/
CREATE TABLE IF NOT EXISTS
cards (
  card_id INTEGER PRIMARY KEY,
  card_uuid BLOB,
  user_id INTEGER,
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS card_uuid_idx ON cards(card_uuid);

/* DROP TABLE attendance; /**/
CREATE TABLE IF NOT EXISTS
attendance (
  name TEXT,
  logged_in INTEGER,
  event_when INTEGER
);
