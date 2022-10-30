CREATE TABLE games_gender(
	id int(11) NOT NULL PRIMARY KEY,
	game_gender varchar(100) NOT NULL
    )ENGINE=InnoDB DEFAULT CHARSET='utf8';

CREATE TABLE games_productors(
	id int(11) NOT NULL PRIMARY KEY,
    productor_name varchar(100) NOT NULL,
    country varchar(50) NOT NULL
    )ENGINE=InnoDB DEFAULT CHARSET='utf8';

CREATE TABLE games_list(
  id int(11) NOT NULL PRIMARY KEY,
  game_name varchar(50) NOT NULL,
  productor int(11) NOT NULL,
  gender int(11) NOT NULL,
  game_rate decimal(4, 2) NOT NULL,
  game_description TEXT NOT NULL,
  best_seller boolean NOT NULL,
  FOREIGN KEY(productor) REFERENCES games_productors(id),
  FOREIGN KEY(gender) REFERENCES games_gender(id)
   )ENGINE=InnoDB DEFAULT CHARSET='utf8';
    
CREATE TABLE users(
  id int(11) PRIMARY KEY,
  real_name varchar(50) NOT NULL,
  age int(11) NOT NULL,
  sex varchar(20) NOT NULL,
  username varchar(100) NOT NULL,
  user_pswd varchar(100) NOT NULL
  )ENGINE='InnoDB' DEFAULT CHARSET='utf8';

    
