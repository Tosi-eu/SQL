INSERT
	INTO games_gender
    VALUES
		(1, 'Action'),
        (2, 'Sports'),
        (3, 'Adventure'),
        (4, 'Fight'),
        (5, 'Terror'),
        (6, 'Indie'),
        (7, 'RPG'),
        (8, 'Anime'),
        (9, 'Puzzle'),
        (10, 'FPS'),
        (11, 'Shooter');

INSERT
	INTO games_productors
    VALUES
		(1, 'Bethesda', 'Germany'),
        (2, 'CAPCOM', 'Japan'),
        (3, 'SEGA', 'Japan'),
        (4, 'EA Sports Games', 'EUA'),
        (5, 'Activision', 'EUA'),
        (6, 'Ubisoft', 'EUA'),
        (7, 'Pixar', 'EUA'),
        (8, 'Paramount', 'EUA'), 
        (9, 'Valve', 'EUA'),
        (10, 'SNK', 'Japan'),
        (11, 'Pipeworks Studio', 'EUA'),
        (12, 'Gorka Sutdios', 'EUA');
        
INSERT
	INTO games_list
	VALUES
		(1, 'The Elder Scrolls IV: Oblivion', 1, 7, 8.1, 'Description: RPG game in first person mode, based in complete tasks to advance in the main history.', true),
        (2, 'Street Fighter', 3, 4, 9.2, 'Description: Historic Fight Game where you can beat and launch power by doing AMAZING combos', true),
        (3, 'Mega Man', 3, 2, 8.3, 'Description: Indie game by sega where you control Mega man, fighting enemies, collecting improvements for himself', true),
        (4, 'Fifa 15', 4, 2, 7.7, 'Description: Soccer game, with AMAZING graphics and totally updated', false),
        (5, 'Bomberman', 3, 8, 8.1, 'Description: Platform nd aventure game based in defeat your enemies by plating bombs', false),
        (6, 'Metal Slug', 10, 11, 9.1, 'Description: Shoot game in third person mode and multiplayer, you defeat enemies and advance in map trying to conclude the mission lauching bombs and giving bullets and more bullets', true),
        (7, 'Cat Mario', 12, 6, 4.7, 'Description: Indie game, that can do you get angry anytime', false),
        (8, 'Terraria', 11, 6, 6.9, 'Description: Indie game based in exploration, improve elements, kill enemies, complete missions. Its 3rd person mode and multiplayer (local and server)', false),
        (9, 'Counter Strike: Global Offensive', 9, 11, 8.8, 'Description: FPS globally famous, 5x5, buying guns and killing your oponents to get the victory', true);
