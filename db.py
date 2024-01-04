'''
This file is used for experimenting and playing with postgresql, not needed for the app to work
'''

from pgdb import Connection 
import pandas as pd
import auth

conn = Connection(database=auth.database, host=auth.host,
                  user=auth.user, password=auth.password)
cur = conn.cursor()

cur.execute("SELECT * FROM Groups WHERE group_id=9")
conn.commit()
print(cur.fetchone())

# query = pd.read_sql_query('''SELECT * FROM users''', conn)
# print(query)

# conn.close()

''' -----------------------------------------------------------------
SQL QUERIES to initially create tables:

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);

**** added other columns to users table as well, see using SELECT * FROM users 
	 deleted foreign key constraints for now
****

CREATE TABLE Students (
	user_id INT,
	group_id INT
);

CREATE TABLE Groups (
	group_id INT GENERATED ALWAYS AS IDENTITY,
	group_name VARCHAR(50),
	group_owner INT,
	group_description VARCHAR(1000),
	PRIMARY KEY(group_id),
	CONSTRAINT fk_user
		FOREIGN KEY(group_owner)
			REFERENCES users(user_id)
			ON DELETE SET NULL
);


CREATE TABLE Exercises (
	exercise_id INT GENERATED ALWAYS AS IDENTITY,
	exercise_name VARCHAR(100),
	met_constant INT,
	PRIMARY KEY(exercise_id)
);


CREATE TABLE Workouts (
	workout_id INT GENERATED ALWAYS AS IDENTITY,
	user_id INT,
	exercise_id INT,
	calories_burned INT,
	distance NUMERIC, 
	reps INT,
	time TIME,
	PRIMARY KEY(workout_id),
	CONSTRAINT fk_user
		FOREIGN KEY(user_id)
			REFERENCES users(user_id)
			ON DELETE SET NULL,
	CONSTRAINT fk_exercise
		FOREIGN KEY(exercise_id)
			REFERENCES exercises(exercise_id)
			ON DELETE SET NULL
);

CREATE TABLE Assignments (
	assignment_id INT GENERATED ALWAYS AS IDENTITY,
	user_id INT,
	group_id INT, 
	exercise_id INT,
	workout_id INT,
	CONSTRAINT fk_user
		FOREIGN KEY(user_id)
			REFERENCES users(user_id)
			ON DELETE SET NULL,
	CONSTRAINT fk_group
		FOREIGN KEY(group_id)
			REFERENCES groups(group_id)
			ON DELETE SET NULL,
	CONSTRAINT fk_exercise
		FOREIGN KEY(exercise_id)
			REFERENCES exercises(exercise_id)
			ON DELETE SET NULL,
	CONSTRAINT fk_workout
		FOREIGN KEY(workout_id)
			REFERENCES workouts(workout_id)
);

------

INSERT INTO Exercises (exercise_name, met_constant) VALUES ('running', 8);
INSERT INTO Exercises (exercise_name, met_constant) VALUES ('Pull-Ups', 8);
INSERT INTO Exercises (exercise_name, met_constant) VALUES ('Squats', 5);
INSERT INTO Exercises (exercise_name, met_constant) VALUES ('Push-Ups', 6);

'''