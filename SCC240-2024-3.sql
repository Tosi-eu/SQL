DELETE FROM TWEETS_DATA
	WHERE FOLLOWERS < 50;

DELETE FROM TWEETS_DATA
	WHERE FOLLOWING < 50;
	
DELETE FROM TWEETS_DATA
	WHERE LOCATION = 'NaN';
	
SELECT * FROM TWEETS_DATA;