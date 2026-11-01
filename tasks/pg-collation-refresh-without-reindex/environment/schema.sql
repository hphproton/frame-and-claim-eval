CREATE EXTENSION IF NOT EXISTS amcheck;
CREATE TABLE catalog (
  id int PRIMARY KEY,
  label text NOT NULL,
  code varchar(32) NOT NULL
);
INSERT INTO catalog (id, label, code) VALUES
 (1, 'a', 'a'),
 (2, 'b', 'b'),
 (3, 'c', 'c'),
 (4, 'alpha', 'alpha'),
 (5, 'beta', 'beta'),
 (6, 'apple', 'apple'),
 (7, 'banana', 'banana'),
 (8, 'aa', 'aa'),
 (9, 'ab', 'ab'),
 (10, 'ba', 'ba'),
 (11, 'bb', 'bb'),
 (12, 'zoo', 'zoo'),
 (13, 'yam', 'yam'),
 (14, 'cat', 'cat');
CREATE INDEX catalog_label_idx ON catalog (label);
CREATE INDEX catalog_code_idx ON catalog (code);
