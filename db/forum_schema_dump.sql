PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS sports(
  sport_id INTEGER PRIMARY KEY AUTOINCREMENT,
  sportname TEXT UNIQUE, 
  time TEXT, 
  hallnumber INTEGER,
  note TEXT);
CREATE TABLE IF NOT EXISTS orders(
  order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
  nickname TEXT,sportname TEXT, 
  timestamp INTEGER,
  FOREIGN KEY(sportname) REFERENCES sports(sportname) ON DELETE CASCADE,
  FOREIGN KEY (nickname) REFERENCES users(nickname) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS users(
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  nickname TEXT UNIQUE,
  password TEXT,
  regDate INTEGER,
  lastLogin INTEGER,
  timesviewed INTEGER,
  userType BOOL,
  UNIQUE(user_id, nickname));
CREATE TABLE IF NOT EXISTS users_profile(
  user_id INTEGER PRIMARY KEY,
  firstname TEXT,
  lastname TEXT,
  email TEXT,
  website TEXT,
  picture TEXT,
  mobile TEXT,
  skype TEXT,
  age INTEGER,
  residence TEXT,
  gender TEXT,
  signature TEXT,
  avatar TEXT,
  FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS friends (
  user_id INTEGER,
  friend_id INTEGER,
  PRIMARY KEY(user_id, friend_id),
  FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(friend_id) REFERENCES users(user_id) ON DELETE CASCADE);

COMMIT;
PRAGMA foreign_keys=ON;