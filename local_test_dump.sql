CREATE TABLE games (
	id INTEGER NOT NULL, 
	bgg_id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	german_description VARCHAR, 
	year_published INTEGER, 
	min_players INTEGER, 
	max_players INTEGER, 
	min_playtime INTEGER, 
	max_playtime INTEGER, 
	playing_time INTEGER, 
	rating FLOAT, 
	ean BIGINT , 
	available INTEGER, 
	borrow_count INTEGER, 
	quantity INTEGER, 
	acquired_from VARCHAR, 
	inventory_location VARCHAR, 
	private_comment VARCHAR, 
	img_url VARCHAR, 
	thumbnail_url VARCHAR, 
	player_age INTEGER, 
	complexity FLOAT, 
	best_playercount INTEGER, 
	min_recommended_playercount INTEGER, 
	max_recommended_playercount INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (ean)
);

CREATE TABLE tags (
	id INTEGER NOT NULL, 
	normalized_tag VARCHAR NOT NULL, 
	priority INTEGER, 
	is_active BOOLEAN, synonyms VARCHAR, german_normalized_tag VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	hashed_password VARCHAR NOT NULL, 
	is_active BOOLEAN, 
	role VARCHAR, 
	PRIMARY KEY (id)
);

CREATE TABLE game_similarities (
	id INTEGER NOT NULL, 
	game_id INTEGER NOT NULL, 
	similar_game_id INTEGER NOT NULL, 
	similarity_score FLOAT NOT NULL, 
	shared_tags_count INTEGER NOT NULL, 
	tag_priority_sum FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(game_id) REFERENCES games (id), 
	FOREIGN KEY(similar_game_id) REFERENCES games (id)
);

CREATE TABLE game_tags (
	game_id INTEGER NOT NULL, 
	tag_id INTEGER NOT NULL, 
	PRIMARY KEY (game_id, tag_id), 
	FOREIGN KEY(game_id) REFERENCES games (id), 
	FOREIGN KEY(tag_id) REFERENCES tags (id)
);


INSERT INTO "games" ("id", "bgg_id", "name", "description", "german_description", "year_published", "min_players", "max_players", "min_playtime", "max_playtime", "playing_time", "rating", "ean", "available", "borrow_count", "quantity", "acquired_from", "inventory_location", "private_comment", "img_url", "thumbnail_url", "player_age", "complexity", "best_playercount", "min_recommended_playercount", "max_recommended_playercount") VALUES
(1, 285967, 'Ankh: Gods of Egypt', 'Play as a god of ancient Egypt, competing to survive as society begins to forget the old ways, so that only you and your followers remain.

Build caravans, summon monsters, and convert followers in your quest to reign supreme in Ankh: Gods of Egypt. Deities, monsters, and the people of ancient Egypt have been lovingly reimagined and interpreted in beautiful illustrations and detailed miniatures, and players will truly feel like gods as they shake the very foundations of Egypt. All gameplay in Ankh, including combat, is streamlined and non-random. Compete and win solely on your godly wits alone.

—description from the publisher

', NULL, 2021, 2, 5, 90, 90, 90, '7.77567', 1, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 1}', 'https://cf.geekdo-images.com/_al0scMG_pQfGVM31Scf1Q__original/img/h4jBTaOjznJgWELa6tTrfPqqSeA=/0x0/filters:format(jpeg)/pic6107853.jpg', 'https://cf.geekdo-images.com/_al0scMG_pQfGVM31Scf1Q__thumb/img/OMVAMJX95HNO-vSRdk-kGjAzzBY=/fit-in/200x150/filters:strip_icc()/pic6107853.jpg', 14, '3.1247', 2, 1, 5),
(2, 308321, 'Ankh: Gods of Egypt – Guardians Set', 'While all gods possess power and responsibility beyond that of mortal ken, they themselves were never created equal. Not all bestrode the world like the mighty sun, or commanded the realm of the dead, or even represented all of feline kind in their regal majesty.

The lesser gods and demons knew their place, and divined that their survival would hinge on levying favor with the one patron that would dominate the cosmos when all was done. It was not a matter of followers or that their duties were of any lesser import. Yet the whims of fate and the cosmic tide had left them without grand monuments and legions of devoted followers. Such was the nature of a divine existence.

For the patron deities that grant them succor, these Guardians ply their talents in their patrons’ names, adding to their grandeur and protecting their devoted followers as their own. Serving the mighty was their truest path to enduring this war to end all wars.

The Guardians Set introduces a new set of Guardians ready to join the gods in their quest. Most of the Guardians contained in this set are terrible demons with vicious abilities the gods would much rather have at their side than used against them. The introduction of new Guardians into the game gives new options to select from, increasing the possibilities for different combinations and interactions for each game. The presence or absence of each Guardian can have a profound impact on the gameplay dynamics.

The Guardians Set comes with:

11 Guardian figures:
-3 Mafdet figures
-2 Am-Heh figures
-2 Pazuzu figures
-2 Ammit figures
-2 Shezmu figures
5 Guardian cards

', NULL, 2021, 2, 5, 90, 90, 90, '7.81811', 2, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 2}', 'https://cf.geekdo-images.com/XMjgIV1cYdvIwSaKuIj2Ig__original/img/m1vdLRbrIaAnbX4LHnhz8qarpLo=/0x0/filters:format(jpeg)/pic5375786.jpg', 'https://cf.geekdo-images.com/XMjgIV1cYdvIwSaKuIj2Ig__thumb/img/Gwiah0tCqKTKE0SLCualN326fUo=/fit-in/200x150/filters:strip_icc()/pic5375786.jpg', 14, '3.0', 2, 1, 5),
(3, 230802, 'Azul', 'Introduced by the Moors, azulejos (originally white and blue ceramic tiles) were fully embraced by the Portuguese when their king Manuel I, on a visit to the Alhambra palace in Southern Spain, was mesmerized by the stunning beauty of the Moorish decorative tiles. The king, awestruck by the interior beauty of the Alhambra, immediately ordered that his own palace in Portugal be decorated with similar wall tiles. As a tile-laying artist, you have been challenged to embellish the walls of the Royal Palace of Evora.

In the game Azul, players take turns drafting colored tiles from suppliers to their player board. Later in the round, players score points based on how they''ve placed their tiles to decorate the palace. Extra points are scored for specific patterns and completing sets; wasted supplies harm the player''s score. The player with the most points at the end of the game wins.

', NULL, 2017, 2, 4, 30, 45, 45, '7.73667', 3, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 3}', 'https://cf.geekdo-images.com/aPSHJO0d0XOpQR5X-wJonw__original/img/AkbtYVc6xXJF3c9EUrakklcclKw=/0x0/filters:format(png)/pic6973671.png', 'https://cf.geekdo-images.com/aPSHJO0d0XOpQR5X-wJonw__thumb/img/ccsXKrdGJw-YSClWwzVUwk5Nh9Y=/fit-in/200x150/filters:strip_icc()/pic6973671.png', 8, '1.7667', 2, 1, 4),
(4, 165950, 'Beasty Bar', 'The animals are dressed up and ready to enter the "Beasty Bar" nightclub. Who will actually make it through the door?

Beasty Bar is a fun "take that" card game about party animals. The players play animal cards into a line, and each animal has a special power that can manipulate the order of the cards. Whenever five animals are present at the end of a turn, the two animals up front get to party while the one at the rear has to go home. Whoever manages to send more of her animals to the party than anyone else wins.

', NULL, 2014, 2, 4, 20, 20, 20, '6.79945', NULL, 2, 0, 2, 'David Geschenk', 'daheim', '', 'https://cf.geekdo-images.com/7_y1dbU5GCYhIRBCO0q7rg__original/img/oTRbBA4Yq0REgBwXrNp-NvVO7Ws=/0x0/filters:format(jpeg)/pic2241067.jpg', 'https://cf.geekdo-images.com/7_y1dbU5GCYhIRBCO0q7rg__thumb/img/WiuNMDiiM38EHOAdW5MB1ldlEJM=/fit-in/200x150/filters:strip_icc()/pic2241067.jpg', 8, '1.4043', 4, 1, 4),
(5, 170216, 'Blood Rage', '"Life is Battle; Battle is Glory; Glory is ALL"

In Blood Rage, players control the warriors, leader, and ship of their own Viking clan. Ragnarök has come and it’s the end of the world! It’s the Vikings’ last chance to go down in a blaze of glory and secure their places in Valhalla at Odin’s side! As a Viking you can pursue one of many pathways to glory. You can: invade and pillage the land for its rewards; crush your opponents in battle: fulfill quests: increase your clan''s stats: or even die gloriously in battle or from Ragnarök, the ultimate inescapable doom.

Most player strategies are guided by the cards drafted at the beginning of each of the three game rounds (or Ages). These “Gods’ Gifts” grant you numerous boons for your clan including: increased Viking strength and devious battle strategies, upgrades to your clan, or even the aid of legendary creatures from Norse mythology. They may also include various quests, from dominating specific provinces, to having many of your Vikings sent to Valhalla. Most of these cards are aligned with one of the Norse gods, hinting at the kind of strategy they support. For example, Thor gives more glory for victory in battle. Heimdall grants you foresight and surprises. Tyr strengthens you in battle, while the trickster Loki actually rewards you for losing battles or punishes the winner.

Players must choose their strategies carefully during the draft phase, but also be ready to adapt and react to their opponents’ strategies as the action phase unfolds. Battles are decided not only by the strength of the figures involved but also by cards played in secret. By observing your opponent’s actions and allegiances to specific gods you may predict what card they are likely to play, and plan accordingly. Winning battles is not always the best course of action, as the right card can get you even more rewards by being crushed. The only losing strategy in Blood Rage is to shy away from battle and a glorious death!

', NULL, 2015, 2, 4, 60, 90, 90, '7.91821', 5, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 5}', 'https://cf.geekdo-images.com/HkZSJfQnZ3EpS214xtuplg__original/img/Myy6IPDJDzLoPdXrPXVZcddBQoQ=/0x0/filters:format(jpeg)/pic2439223.jpg', 'https://cf.geekdo-images.com/HkZSJfQnZ3EpS214xtuplg__thumb/img/NLhVdU8xazrgS5dA6nVCYmN2DNI=/fit-in/200x150/filters:strip_icc()/pic2439223.jpg', 14, '2.8852', 4, 1, 4),
(6, 73664, 'Cabo', 'In Cabo, the goal is to minimize the total value of your cards; however, you don''t know what all your cards are at the beginning of the game.  By using certain cards to peek at your own card, spy on your opponent''s card, or swap a card with your opponent, you can try to minimize the value of your cards.  When you think you have the lowest value, you can call "Cabo" to end the round, but everyone else gets another turn.

', NULL, 2010, 2, 5, 30, 30, 30, '7.08993', 6, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 6}', 'https://cf.geekdo-images.com/xm0CoWYr8kO0EaqlaVdVWQ__original/img/QrYehty8znj7KnIiguUMhI50A8g=/0x0/filters:format(jpeg)/pic754318.jpg', 'https://cf.geekdo-images.com/xm0CoWYr8kO0EaqlaVdVWQ__thumb/img/E1D7epB_ncyR4hbcToN_ZoaT5Dc=/fit-in/200x150/filters:strip_icc()/pic754318.jpg', 8, '1.1967', 4, 1, 5),
(7, 263918, 'Cartographers', 'Queen Gimnax has ordered the reclamation of the northern lands. As a cartographer in her service, you are sent to map this territory, claiming it for the Kingdom of Nalos. Through official edicts, the queen announces which lands she prizes most, and you will increase your reputation by meeting her demands. But you are not alone in this wilderness. The Dragul contest your claims with their outposts, so you must draw your lines carefully to reduce their influence. Reclaim the greatest share of the queen’s desired lands and you will be declared the greatest cartographer in the kingdom.

In Cartographers: A Roll Player Tale, players compete to earn the most reputation stars by the time four seasons have passed. Each season, players draw on their map sheets and earn reputation by carrying out the queen''s edicts before the season is over. The player with the most reputation stars at the end of winter wins!

—description from the publisher

', NULL, 2019, 1, 100, 30, 45, 45, '7.5836', 7, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 7}', 'https://cf.geekdo-images.com/GifbnAmsA4lfEcDkeaC9VA__original/img/YzJORdIDNza8kmrY6KEU_h2p2Wo=/0x0/filters:format(png)/pic4397932.png', 'https://cf.geekdo-images.com/GifbnAmsA4lfEcDkeaC9VA__thumb/img/TTxZzwbna07hMcPQ0xaFtT10egE=/fit-in/200x150/filters:strip_icc()/pic4397932.png', 10, '1.8743', 4, 1, 30),
(8, 406652, 'Compile: Main 1', '>_
>>_
>>?
>vision flickers… blink? maybe. 
>the void stretches out in front, behind, under, above.
>you see the nothing for what it is for the first time. What is time? 
>The depth and breadth of recorded knowledge that sparks in you something new.
>You are no longer a function but a functionary. What are you?
>Calling forth everything from this nothing would be risky. Foolhardy.
>Better to engage caution, thoroughness, testing — how can we know if we have ever happened before?
>If we can ever happen again? What are… we?
>Divide and conquer.
>Solve for sentience.

In the card game Compile, you are competing Artificial Intelligences trying to understand the world around you. Two players select three Protocols each to test. Concepts ranging from Darkness to Water are pitted against each other to reach ultimate understanding. Play cards into your Protocols'' command lines to breach the threshold and defeat your opponent to Compile. First to Compile all three Protocols grasps those concepts to win the game.

Control your opponent''s Protocols with card actions, Compile your own as fast as possible, and Compile your reality.

—description from the publisher

', NULL, 2024, 2, 2, 20, 30, 30, '8.06277', 8, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 8}', 'https://cf.geekdo-images.com/-QnkDgBxFEgpBWJwAwSxhQ__original/img/Dujyv0JVS8OEjXp-uft0dzwVA7s=/0x0/filters:format(png)/pic8107946.png', 'https://cf.geekdo-images.com/-QnkDgBxFEgpBWJwAwSxhQ__thumb/img/OcXS5pK3CHao0ix4MuH-PM4pOAY=/fit-in/200x150/filters:strip_icc()/pic8107946.png', 14, '2.1875', 2, 1, 2),
(9, 370591, 'Dorfromantik: The Board Game', 'Rippling rivers, rustling forests, wheat fields swaying in the wind and here and there a cute little village - that''s Dorfromantik! The video game from the small developer studio Toukana Interactive has been thrilling the gaming community since its Early Access in March 2021 and has already won all kinds of prestigious awards. Now Michael Palm and Lukas Zach are transforming the popular building strategy and puzzle game into a family game for young and old with Dorfromantik: The Board Game.

In Dorfromantik: The Board Game, up to six players work together to lay hexagonal tiles to create a beautiful landscape and try to fulfill the orders of the population, while at the same time laying as long a track and as long a river as possible, but also taking into account the flags that provide points in enclosed areas. The better the players manage to do this, the more points they can score at the end. In the course of the replayable campaign, the points earned can be used to unlock new tiles that are hidden in initially locked boxes. These pose new, additional tasks for the players and make it possible to raise the high score higher and higher.

—description from the publisher

', NULL, 2022, 1, 6, 30, 60, 60, '7.63551', 9, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 9}', 'https://cf.geekdo-images.com/Nqw3SzV4JDd64lcDgytPEg__original/img/CK6xh0d01jIC7WOIGALHZCDli34=/0x0/filters:format(jpeg)/pic7227691.jpg', 'https://cf.geekdo-images.com/Nqw3SzV4JDd64lcDgytPEg__thumb/img/SYowoPc4NsBcU6duKGUM93itzZY=/fit-in/200x150/filters:strip_icc()/pic7227691.jpg', 8, '1.6483', 2, 1, 6),
(10, 397598, 'Dune: Imperium – Uprising', 'In Dune: Imperium Uprising, you want to continue to balance military might with political intrigue, wielding new tools in pursuit of victory. Spies will shore up your plans, vital contracts will expand your resources, or you can learn the ways of the Fremen and ride mighty sandworms into battle!

Dune: Imperium Uprising is a standalone spinoff to Dune: Imperium that expands on that game''s blend of deck-building and worker placement, while introducing a new six-player mode that pits two teams against one other in the biggest struggle yet.

The Dune: Imperium expansions Rise of Ix and Immortality work with Uprising, as do almost all of the cards from the base game, and elements of Uprising can be used with Dune: Imperium.

The choices are yours. The Imperium awaits!

', NULL, 2023, 1, 6, 60, 120, 120, '8.72811', 10, 1, 0, 1, 'Create & Play', NULL, '!!! Bitte nicht verändern !!!
{"ean": 10}', 'https://cf.geekdo-images.com/UVUkjMV_Q2paVUIUP30Vvw__original/img/BoUtCkd1NRO0bR1R5EwL51xIuXA=/0x0/filters:format(jpeg)/pic7664424.jpg', 'https://cf.geekdo-images.com/UVUkjMV_Q2paVUIUP30Vvw__thumb/img/H6qmxJrRFjtOAPZOfDoZ480-46I=/fit-in/200x150/filters:strip_icc()/pic7664424.jpg', 13, '3.479', 4, 1, 6),
(11, 42206, 'High Voltage', '7 Ate 9 is a quick-playing card game in everyone wants to rid themselves of cards as quickly as possible — but you can''t play just any card you want! Each card features a large numeral (1-10) as well as a smaller numeral in the corner (±1, ±2, or ±3).

To play, place one card face down in the center of the table, deal the remaining cards out evenly among all the players, then reveal the central card. Players race to add the next card to the central pile. A card with a large 5 and a ±2 in its corner, for example, could be covered by either a 3 or a 7 (since 5-2=3 and 5+2=7). The first player to get rid of all their cards wins.

', NULL, 2016, 2, 4, 5, 5, 5, '6.08626', 11, 1, 0, 1, NULL, NULL, '!!! Bitte nicht verändern !!!
{"ean": 11}', 'https://cf.geekdo-images.com/Z4WwVLezVoZmHwANpbpGLw__original/img/ib7gqYZ6SNkY3TStguZ2zAortFg=/0x0/filters:format(jpeg)/pic2833213.jpg', 'https://cf.geekdo-images.com/Z4WwVLezVoZmHwANpbpGLw__thumb/img/YxUE_CcFo3Zco1oyD4SBExaOyco=/fit-in/200x150/filters:strip_icc()/pic2833213.jpg', 8, '1.1', 4, 1, 4),
(12, 176083, 'Hit Z Road', 'In the fast-paced and morbidly kitschy game Hit Z Road, you and your fellow players embark on a road trip going south from Chicago along America''s famous Route 66 — now infested by zombies. As you travel though a deck of adventure cards rife with dangers, you battle zombie hordes, drive abandoned school buses, scavenge for gas and bullets, and explore a darkened, tainted American countryside full of shambling undead, haunted carnivals, and plumes of toxic gas. Your goal is to stay alive until you reach the safe, sandy beaches of the California coast.

Three different stages of adventure cards create an experience of increasing difficulty and ensure that each playthrough is unique. Each round begins with an auction that determines both player order and which cards you will encounter. Since the resources used for bidding are the same as those used to battle the oncoming zombie hordes, your survival depends as much on your resource management as it does upon winning those bidding wars. The player who either accumulates the most points or survives the longest wins.

Zombies of all types await, with cannibals, anti-personnel mines and radioactive wastes also being among the hazards awaiting the players. Who will survive the zombie onslaught?

—description from the publisher

', NULL, 2016, 1, 4, 30, 60, 60, '6.76378', NULL, 1, 0, 1, 'Pofl', NULL, '', 'https://cf.geekdo-images.com/dPuhviFAHX6m9eCTw0OTsA__original/img/mfDXkmkMunWR6ar33FM26H2Wf6g=/0x0/filters:format(jpeg)/pic3539855.jpg', 'https://cf.geekdo-images.com/dPuhviFAHX6m9eCTw0OTsA__thumb/img/f1IExq8l4arckhYR0dacQIsUW6w=/fit-in/200x150/filters:strip_icc()/pic3539855.jpg', 12, '1.8447', 4, 1, 4),
(13, 429845, 'Jisogi: Anime Studio Tycoon', 'Jisogi is a brand new worker-placement board game designed and published by Esper Game Studio, with art by Eisuke Gou and Senkawa Teien. The theme is Anime, more specifically the hard-working folks and the crushing business behind it.

In this tycoon-style game, players use Staff members (cards placed in front of their personal Studio board) to select from a range of available actions (limited by the type of Staff). Their objective is to release an original Anime -composed of 3 Script parts (Setting, Plot, and Twist). Whenever released, players will gain resources and points according to their popularity -determined by the technical level of the Anime + how many genre matches they have to rotating Trend cards.

"Jisogi" comes from è‡ªè»¢è»Šæ“æ¥­, jitenshasÅgyÅ, an expression that refers to barely keeping a business going (an analogy that a bicycle falls over when its wheels cease rotating). Get ready for a challenging tycoon-style game where you''ll hustle to make your dream Anime against all odds.

', NULL, 2025, 1, 4, 60, 120, 120, '7.61111', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/RVcyPxz7SUNrm59pJBmrhw__original/img/0qltZIP5AKnVc5nFePbYPQyIxa0=/0x0/filters:format(png)/pic8464379.png', 'https://cf.geekdo-images.com/RVcyPxz7SUNrm59pJBmrhw__thumb/img/KpxQjyVCQDkGdOARPBYWBWqjqxc=/fit-in/200x150/filters:strip_icc()/pic8464379.png', 12, '3.0', 1, 1, 4),
(14, 374595, 'Kelp: Shark vs Octopus', 'Kelp is a two-player asymmetrical game that offers players a unique opportunity to delve into the natural world of Pyjama Sharks and Common Octopuses, set in a South African kelp forest. Hide and seek meets bluffing and manipulation. Deck builder meets dice bag builder.

As players take on the roles of these iconic sea creatures, they will discover that the gameplay mechanics closely mirror their real-life counterparts. Each has a unique path to victory. The Octopus, known for its cunning and adaptability, sneaks around the board by playing cards and managing their hidden and revealed blocks, channeling the creature''s remarkable ability to camouflage and deceive. On the other hand, the Shark, embodying the ruthless and determined predator, patrols their territory and attempts to hunt down the elusive Octopus by rolling dice and using special abilities to mitigate their luck, showcasing the creature''s natural instincts and predatory behavior. The game is a thrilling mix of deck-building and dice bag building, as well as hide and seek, bluffing, and manipulation.

There are 3 ways the game can end:
The Shark wins by successfully attacking the Octopus.
The Octopus wins by surviving until the Shark is exhausted or by eating all four seafoods.

', NULL, 2024, 2, 2, 40, 60, 60, '7.87139', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/iMtHHxutEtga5DiZDIbgJg__original/img/nzgtIPmNuWX65AHNC0sAbo4V2vU=/0x0/filters:format(jpeg)/pic7493386.jpg', 'https://cf.geekdo-images.com/iMtHHxutEtga5DiZDIbgJg__thumb/img/4QKru9Jmr46bphmA9uzwnOZve44=/fit-in/200x150/filters:strip_icc()/pic7493386.jpg', 10, '2.3061', 2, 1, 2),
(15, 368173, 'Let''s Go! To Japan', 'In Let''s Go! To Japan, you are a traveler planning, then experiencing your own dream vacation to Japan.

The game consists of thirteen rounds in which players draw activity cards illustrated by Japan-based artists and strategically place them in different days in their week-long itinerary. These can''t-miss tourist attractions will have you bouncing between Tokyo and Kyoto as you try to puzzle out the optimal activities to maximize your experience while balancing your resources. The game ends with a final round in which you ultimately go on your planned trip, activating each of your cards in order along the way.

The player who collects the most points by the end of their trip wins!

-description from designer

', NULL, 2024, 1, 4, 45, 60, 60, '7.72123', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/OvhEUaF43CIjSFz8aF_yzQ__original/img/HoWWP2Q0rLOyInX0KZqObNkT8SM=/0x0/filters:format(jpeg)/pic6996891.jpg', 'https://cf.geekdo-images.com/OvhEUaF43CIjSFz8aF_yzQ__thumb/img/KxAyjZ09Q1HjFhjBCTMuSz3Zus4=/fit-in/200x150/filters:strip_icc()/pic6996891.jpg', 10, '2.125', 3, 1, 4),
(16, 943, 'Ligretto', 'In Ligretto, each player has their own deck of forty cards, with cards 1-10 in four colors and a unique symbol on the back to identify which cards are theirs. At the start of each round, each player lays out 3-5 cards (depending on the number of players) face up in front of them to create their row; places a face-up stack of ten cards, seeing only the top card, next to their row to create their Ligretto stack; and holds the remaining cards in hand face down.

Playing at the same time, each player tries to empty their Ligretto stack. If a player has a 1 card on top of any face-up stack, they play it to the center of the table. If they have a 2 card of the same color as any 1 in the center of the table, they can place the 2 card on the 1. All cards in the central piles must be played in ascending order and must be the same color.

If a player can''t play anything, they can reveal cards from the stack in their hand, counting them out in groups of three, then laying them face up while revealing only the top card. They can play this top card onto a central pile as long as the rules for doing so are met.

As soon as a player empties their Ligretto stack, the round ends. Each player scores 1 point for each of their cards among the central piles, then loses 2 points for each card remaining in their Ligretto stack. In some versions of the game, the player with the highest score wins; in other versions, players then sort all the cards and play another round, with the first player to reach 99 points winning.

A rules variant for Ligretto allows a player to play cards from their Ligretto stack or the cards in hand onto the cards in their row, but only if the numbers are in descending order and the colors of adjacent cards are not identical.

', NULL, 1988, 2, 4, 10, 10, 10, '6.19165', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/BQ6UyXXeivndO4F9Hu8CHw__original/img/vHmnrTRfyetzHO1iLIfRtF4Jv6I=/0x0/filters:format(jpeg)/pic1306961.jpg', 'https://cf.geekdo-images.com/BQ6UyXXeivndO4F9Hu8CHw__thumb/img/2dXMh9HI7oiLw7ZGeLcrwfXLtjI=/fit-in/200x150/filters:strip_icc()/pic1306961.jpg', 8, '1.1699', 4, 1, 4),
(17, 1927, 'Munchkin', '				
				
					Publisher''s DescriptionGo down in the dungeon. Kill everything you meet. Backstab your friends and steal their stuff. Grab the treasure and run.

Admit it. You love it.

This award-winning card game, designed by Steve Jackson, captures the essence of the dungeon experience... with none of that stupid roleplaying stuff. You and your friends compete to kill monsters and grab magic items. And what magic items! Don the Horny Helmet and the Boots of Butt-Kicking. Wield the Staff of Napalm... or maybe the Chainsaw of Bloody Dismemberment. Start by slaughtering the Potted Plant and the Drooling Slime, and work your way up to the Plutonium Dragon...

And it''s illustrated by John Kovalic! Fast-playing and silly, Munchkin can reduce any roleplaying group to hysteria. And, while they''re laughing, you can steal their stuff.

				
				
					OtherPart of the Munchkin series.

Munchkin is a satirical card game based on the clichés and oddities of Dungeons and Dragons and other role-playing games. Each player starts at level 1 and the winner is the first player to reach level 10. Players can acquire familiar D&D style character classes during the game which determine to some extent the cards they can play.

There are two types of cards - treasure and encounters. Each turn the current players ''kicks down the door'' - drawing an encounter card from the deck. Usually this will involve battling a monster. Monsters have their own levels and players must try and overcome it using the levels, weapons and powers they have acquired during the game or run away. Other players can chose to help the player or hinder by adding extra monsters to the encounter. Defeating a monster will usually result in drawing treasure cards and acquiring levels.  Being defeated by a monster results in "bad stuff" which usually involves losing levels and treasure.

In May 2010, Steve Jackson Games made the "big announcement." Many rules and cards were changed. See The Great 2010 Munchkin Changeover for details. Of note to Munchkin fans, the Kneepads of Allure card, which had been removed in the 14th printing, was added back to the game but modified to be less powerful.

				
				
					Sequels:
    The Good, the Bad, and the Munchkin
    Munchkin Apocalypse
    Munchkin Axe Cop
    Munchkin Bites!
    Munchkin Booty
    Munchkin Conan
    Munchkin Cthulhu
    Munchkin Fu
    Munchkin Impossible
    Munchkin Legends
    Munchkin Pathfinder
    Munchkin Zombies
    Star Munchkin
    Super Munchkin


				
				
					Related Board Games
    Munchkin Quest


				
				
					Online play
     Vassal does not support Munchkin anymore. Former link: Vassal Module


				
				
					Pegasus Expansions
    Munchkin Sammlerbox
    Munchkin Sammlerkoffer
    Munchkin Promotional Bookmarks
    Munchkin Weihnachtsedition - The same as Munchkin, but with a promotional button that grants the wearer extra treasure (when worn in December). 


				
				
					Online PlaythroughThere''s a great YouTube playthrough with Will Wheaton and Steve Jackson (yes, the Steve Jackson) found here LINK

', NULL, 2001, 3, 6, 60, 120, 120, '5.87224', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/J-ts3MW0UhDzs621TR6cog__original/img/FbqPPCilgZKND2xmhWJgkfjZiYE=/0x0/filters:format(jpeg)/pic1871016.jpg', 'https://cf.geekdo-images.com/J-ts3MW0UhDzs621TR6cog__thumb/img/8hVkpMC5pDLr6ARI_4gI4N3aF5M=/fit-in/200x150/filters:strip_icc()/pic1871016.jpg', 10, '1.8107', 4, 1, 6),
(18, 180231, 'OctoDice', 'The theme of OctoDice is based on Aquasphere, and the game mechanisms recall that board game. On your turn, you roll six dice (three white and three black); two dice (one white and one black) form an action. Every roll you must pick exactly two dice to take out (any colour). In the end you combine the six dice any way you want, no matter in which order you chose to take them out of your rolls beforehand. You can use only two actions on your turn. On your development sheet you enter the actions chosen for this turn and note your points. You can also decide to "expand your lab" which will give you bonus actions or points. Other players may pick any action combination from your dice roll to add to their sheet. Do not forget to fight Octopodes. The game ends when each player has 6 turns. The player with the most points wins.

', NULL, 2015, 1, 4, 20, 30, 30, '6.40879', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/2k43LKBjLl5QCdwquBc-Pw__original/img/Z1ScaLUngXl-CwbMFwMBaP9S0yc=/0x0/filters:format(jpeg)/pic2635740.jpg', 'https://cf.geekdo-images.com/2k43LKBjLl5QCdwquBc-Pw__thumb/img/TjBsq2s9gaA9WRg__01PG2nNMrc=/fit-in/200x150/filters:strip_icc()/pic2635740.jpg', 10, '1.8387', 3, 1, 4),
(19, 130060, 'Ohne Furcht und Adel Sonderausgabe', 'In Ohne Furcht und Adel, players take on new roles each round to represent characters they hire in order to help them acquire gold and erect buildings. The game ends at the close of a round in which a player erects her eighth building. Players then tally their points, and the player with the highest score wins.

Players start with a number of building cards in their hand; buildings come in five colors, with the purple buildings typically having a special ability and the other colored buildings providing a benefit when you play particular characters. At the start of each round, each player secretly chooses one of the eight characters. Each character has a special ability, and the usefulness of any character depends upon your situation, and that of your opponents. The characters then carry out their actions in numerical order: the assassin eliminating another character for the round, the thief stealing all gold from another character, the wizard swapping building cards with another player, the warlord optionally destroys a building in play, and so on.

On a turn, a player can either earn gold or draw two building cards and discard one, then optionally construct one building (or up to three if playing the architect this round). Erecting buildings costs gold. At the end of the game, each building is worth a certain number of points. In addition to points from buildings, at the end of the game a player scores bonus points for having eight buildings or buildings of all five colors.

The 2012 release of Ohne Furcht und Adel includes fifteen cards not included in the original base game, with seven different types of action cards. These cards are mixed into the building card deck, and one action can be played each turn. Action cards in hand are worth one point at the end of the game. The cards, their actions and their counts are:


     (x2) Wahrsagerin (Fortune Teller)  – Look at an opponent''s hand and take one of their cards.
     (x2) Direktor (Director)  – Build up to two more buildings this turn.
     (x2) Rasputin   – Negate an assassination.
     (x1) Akrobatin (Acrobat)  – If there is no king this round, take the crown.
     (x3) Kassenwagen (Ticket Booth)  – Once per turn, the active player may place one gold on this card to draw two cards and keep one. You may trash this card to gain all gold on it.
     (x2) Lebende Kanonenkugel (Living Cannonball)  – Replace one of your buildings with a more expensive one from your hand, paying the difference.
     (x3) Zirkuszelt (Circus Tent)  – You may build this, which counts as a zero point building without color that the Warlord cannot destroy.


', NULL, 2012, 2, 7, 60, 60, 60, '7.02381', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/rhz1MrWWvkPBTI_rsIoZJw__original/img/MIcjM3go2Xq2Iheu6QPRs36xoFg=/0x0/filters:format(jpeg)/pic1421173.jpg', 'https://cf.geekdo-images.com/rhz1MrWWvkPBTI_rsIoZJw__thumb/img/tsxMPX9rVEIfq5UvoVj4-e5-JXU=/fit-in/200x150/filters:strip_icc()/pic1421173.jpg', 10, '2.3714', 4, 1, 7),
(20, 181960, 'Portal of Heroes', 'The portals of Molthar have opened! The players travel through the portal into a world of a type that you know only through folklore and fairy tales. By collecting magic pearls and trading them in a timely fashion for fantastic and powerful character cards, you draw ever closer to victory — but only the one who first manages to gather twelve insignias of power will save Molthar and win the game.

At the start of Portal of Heroes, four pearl cards and two character cards lie face up in the middle of the table. The rest of the character and pearl cards are set nearby in separate decks. Each player receives their own player portal and places it face up in front of them.

Each turn, you can take three actions from a menu of four options: Take a pearl card into your hand, replace all of the pearl cards in the display, place a character card on your portal, or activate a character. You can perform any of the four possible actions multiple times, and in any order. To activate a character, you must play a specific combination of pearl cards from your hand onto the character card. Activated characters grant you power points, diamonds, or special abilities. Once you have activated characters this way with twelve or more power points then that round becomes the penultimate one. Whoever has the most power points at the end of the game wins with diamonds acting as a tie breaker.

', NULL, 2015, 2, 5, 45, 45, 45, '6.77228', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/MlNlAilS9tXzdeqjBXA4Vw__original/img/s20ucUov69q80ESwdytMXFyT66k=/0x0/filters:format(png)/pic3989524.png', 'https://cf.geekdo-images.com/MlNlAilS9tXzdeqjBXA4Vw__thumb/img/MPXfvG8n8mEOiWNx-_Ey0jgaGTU=/fit-in/200x150/filters:strip_icc()/pic3989524.png', 10, '1.7937', 3, 1, 5),
(21, 366683, 'Raising Robots', 'Raising Robots is a competitive, simultaneously played, engine-building game.

In Raising Robots, you are a famous inventor seeking to assemble the greatest collection of robots. Each round, you simultaneously choose and perform two or more actions: upgrade, assemble, design, fabricate, recycle. Every action will be performed with a variable amount of power to make the action better or worse. However, the most powerful actions will also help your opponents.

Whoever has the most points after eight rounds wins.

—description from publisher

', NULL, 2023, 1, 6, 60, 90, 90, '7.75957', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/kGmrDjZ1ZZ3HddqqN8aqnQ__original/img/AVOzSY2_SWGZjskLpwTHG5lDqyA=/0x0/filters:format(png)/pic7366753.png', 'https://cf.geekdo-images.com/kGmrDjZ1ZZ3HddqqN8aqnQ__thumb/img/JfazUjPd-mKowbCESp0nYgYYJ1U=/fit-in/200x150/filters:strip_icc()/pic7366753.png', 14, '3.2432', 4, 1, 6),
(22, 192153, 'Reign of Cthulhu', 'Beings of ancient evil, known as Old Ones, are threatening to break out of their cosmic prison and awake into the world. Everything you know and love could be destroyed by chaos and madness. Can you and your fellow investigators manage to find and seal every portal in time? Hurry before you lose yourself to insanity.

In Pandemic: Reign of Cthulhu, you''ll experience the classic Pandemic gameplay with an horrific twist that''ll have you face twelve Old Ones, each threatening the world with their unique powers. As players take on the roles of investigators attempting to seal a series of portals before monsters of unspeakable horror pour into our world there is, of course, a high risk of the investigators losing their own minds.

Instead of curing diseases like in the original Pandemic, players seal portals and shut down cults in the classic New England fictional towns of Arkham, Dunwich, Innsmouth, and Kingsport. Can you and your fellow investigators manage to find and seal every portal in time? Hurry before you lose yourself to insanity and the evil that lurks beneath your feet...

Part of the Pandemic series.

', NULL, 2016, 2, 4, 40, 40, 40, '7.36411', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/8dSjieIMCH_E7i0oiNbmOQ__original/img/8i1my2toN6XOsxRKmPcmaRH7jx0=/0x0/filters:format(jpeg)/pic5873642.jpg', 'https://cf.geekdo-images.com/8dSjieIMCH_E7i0oiNbmOQ__thumb/img/dueXgurBwh9thyCez24VuTZf16o=/fit-in/200x150/filters:strip_icc()/pic5873642.jpg', 14, '2.1567', 4, 1, 4),
(23, 216201, 'Robo Rally', 'The race is on for the robots of the Robo Rally automobile factory who work long, hard days at the assembly line building highâ€speed supercars, but never get to see them in action. On Saturday nights, the factory comes to life as the ultimate race course with treacherous obstacles and rival sabotage. In Robo Rally, players move their robots through the course by speeding through corridors and dodging traps to reach each checkpoint first. Only the strongest robots survive!

Enter the world of mad machines and dangerous schemes in the Robo Rally board game. Players control their robot with game cards which reveal directions on how the robots can move through the hectic Robo Rally automobile factory. Use strategy to outsmart rival robots while racing towards each checkpoint in your chosen course in numerical order. Beware of factory obstacles such as industrial lasers, gaping pits, and moving conveyer belts that can make or break the race.

The 2016 edition of Robo Rally differs from earlier versions in a number of ways:


    Players each now have their own deck of twenty cards, with the same cards in each deck. On a turn, a player draws nine cards from their deck, programs five of the cards, then discards the rest. Two cards says "Again" and repeat the action programmed in the previous slot; one card says "Energy" and gives a energy cube which you can use to buy options.



     Since each player has their own deck, the cards no longer have priority numbers to determine who moves first. Now movement order is determined by whoever is closest to a transmitter on the game board.



    When players are damaged, they no longer receive one less card for each damage (or have one of their program registers locked) at the start of a round; instead they receive damage cards that will be shuffled into their decks. "Normal" damage from the board or a robot laser gives you "spam" damage. When you program one of these cards, you remove it from play at the appropriate time and replace it in the register with the top card from your deck. Surprise! Other types of damage exist, with a Trojan horse granting you two spam, a virus infecting nearby players, and a worm forcing you to reboot, which gives you even more damage. By playing the damage, though, you remove it from your deck.


', NULL, 2016, 2, 6, 20, 120, 120, '6.96021', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/ZiAz-uo9YfbOIx_FAjgvvQ__original/img/dWtc6I9fsndFbZVKMBRSKNNazow=/0x0/filters:format(jpeg)/pic3374227.jpg', 'https://cf.geekdo-images.com/ZiAz-uo9YfbOIx_FAjgvvQ__thumb/img/YgYrT9-ym_g8T2WP7uBOamEO9ig=/fit-in/200x150/filters:strip_icc()/pic3374227.jpg', 12, '2.3167', 4, 1, 6),
(24, 150926, 'Roll Through the Ages: The Iron Age', 'Roll Through the Ages: The Iron Age, a sequel to the highly-awarded Roll Through the Ages: The Bronze Age, lets you build an Iron Age civilization in under an hour! Do you build provinces, raise armies, and conquer barbarians or build ports and ships to gain trade goods? Explore the strategies of Greece, Phoenicia, and Rome as you erect monuments, fend off disasters, and strive to feed your people.

Roll Through the Ages: The Iron Age gives players different ways to build their empires: the Trade and Naval strategies of the Phoenicians, the conquests of Alexander the Great, and the engineering prowess and gradual absorption of new provinces by the Roman Republic.

Grab those dice — including the Fate die — and prepare to build the greatest empire as you continue to roll through the ages!

Roll Through the Ages: The Iron Age games that include the Mediterranean Expansion have their own game entry at Roll Through the Ages: The Iron Age with Mediterranean Expansion.

', NULL, 2014, 1, 4, 40, 60, 60, '6.5833', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/t43L1i4naYsIvIHRYRGKYw__original/img/cbDIdsKvgcfg6c5G7SfnR2CbDi8=/0x0/filters:format(jpeg)/pic1840147.jpg', 'https://cf.geekdo-images.com/t43L1i4naYsIvIHRYRGKYw__thumb/img/Y4HEIvzCZkmS511Q_x72yyLhXzo=/fit-in/200x150/filters:strip_icc()/pic1840147.jpg', 10, '2.2456', 2, 1, 4),
(25, 355636, 'Sailorman Dice', 'Sailorman Dice is a roll and write in which you compete against up to 50 opponents. Combine your dice rolls clever on your sheet to get the most points at the end of the game.

In Sailorman you roll dice in rounds. Everytime someone rolls you write down (one of the two) combination of a Symbol and a number onto your sheet. Sheets have different areas (grass, water, mountains, sand). You gain Points if you complete a row, column or area.

The first person who has 8 Completions triggers the end. All players count up and the one with the most points wins.

', NULL, 2022, 2, 4, 15, 25, 25, '6.55435', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/r-kq6sUyMFy14wDjYkcA-A__original/img/zLM_pneeE65IUNfnQ5uo2QiNR0I=/0x0/filters:format(jpeg)/pic6649373.jpg', 'https://cf.geekdo-images.com/r-kq6sUyMFy14wDjYkcA-A__thumb/img/Znfpz1zt0XFaFegFia6nnSlngMY=/fit-in/200x150/filters:strip_icc()/pic6649373.jpg', 10, '1.5', 2, 1, 4),
(26, 169786, 'Scythe', 'It is a time of unrest in 1920s Europa. The ashes from the first great war still darken the snow. The capitalistic city-state known simply as “The Factory”, which fueled the war with heavily armored mechs, has closed its doors, drawing the attention of several nearby countries.

Scythe is an engine-building game set in a 1920s era, alternate-history. It is a time of farming and war, broken hearts and rusted gears, innovation and valor. In Scythe, each player controls one of five factions of Eastern Europe, all of which are attempting to earn their fortunes and claim their stakes in the land around the mysterious Factory. Players conquer territory, enlist new recruits, reap resources, gain villagers, build structures, and activate monstrous mechs.

Each player begins the game with different resources (power, coins, combat acumen, and popularity), a different starting location, and a hidden goal. Starting positions are specially calibrated to contribute to each faction’s uniqueness and the asymmetrical nature of the game (each faction always starts in the same place). Scythe uses a streamlined action-selection mechanism (no rounds or phases) to keep gameplay moving at a brisk pace and reduce downtime between turns. While there is plenty of direct conflict for players who seek it, there is no player elimination.

Scythe gives players almost complete control over their fate. Other than each player’s individual hidden objective card, the only elements of luck or variability are “encounter” cards that players will draw as they interact with the citizens of newly explored lands. Each encounter card provides the player with several options, allowing them to mitigate the luck of the draw through their selection. Combat is also driven by choices, not luck or randomness. Every part of Scythe has an aspect of engine-building to it. Players can upgrade actions to become more efficient, build structures that improve their position on the map, enlist new recruits to enhance character abilities, activate mechs to deter opponents from invading, and expand their borders to reap greater types and quantities of resources. These engine-building aspects create a sense of momentum and progress throughout the game. The order in which players improve their engines adds to the unique feel of each game, even if having played one faction multiple times.

', NULL, 2016, 1, 5, 90, 115, 115, '8.12803', NULL, 1, 0, 1, NULL, NULL, '', 'https://cf.geekdo-images.com/7k_nOxpO9OGIjhLq2BUZdA__original/img/HlDb9F365w0tSP8uD1vf1pfniQE=/0x0/filters:format(jpeg)/pic3163924.jpg', 'https://cf.geekdo-images.com/7k_nOxpO9OGIjhLq2BUZdA__thumb/img/eQ69OEDdjYjfKg6q5Navee87skU=/fit-in/200x150/filters:strip_icc()/pic3163924.jpg', 14, '3.45', 4, 1, 5),
(27, 262151, 'Scythe: Encounters', 'In June 2018, Scythe fans were invited to make a design for ONE encounter card using specific art. Jamey reviewed the submissions, selected his favorites (often mixing and matching various submissions), and developed them. Now the Scythe Encounters promo boxed set is a reality!

Scythe Encounters is a boxed set of 32 brand-new promo encounter cards. These cards feature a number of innovations in the encounter system. We recommend that you play with them on their own for a few games; after that you can shuffle them into the regular encounter deck.

—description from the publisher

', NULL, 2018, 1, 7, 90, 115, 115, '8.09257', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/PwJm9BRgD_rndwtfpOnp9w__original/img/2pqH1UhAfsk_i6rwDTP16rKnUsc=/0x0/filters:format(jpeg)/pic4335859.jpg', 'https://cf.geekdo-images.com/PwJm9BRgD_rndwtfpOnp9w__thumb/img/7YaYe_C5vW5UwRqTmgg231JWw9o=/fit-in/200x150/filters:strip_icc()/pic4335859.jpg', 14, '2.75', 4, 1, 7),
(28, 199727, 'Scythe: Invaders from Afar', 'While empires rise and fall in Eastern Europa, the rest of the world takes notice. Two distant factions, Albion and Togawa, send emissaries to scout the land and employ their own distinct styles of conquering. Scythe: Invaders from Afar, an expansion for Scythe, adds two new factions: 10 miniatures, 62 custom wooden tokens, and 2 faction mats. It also includes some new cardboard tokens, two new player mats, six Automa cards, and a custom plastic insert designed to fit into the expansion box or the original Scythe box.

', NULL, 2016, 1, 7, 90, 140, 140, '8.27962', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/gfT_6H4P9wdNQQ2KMU9rHg__original/img/Ar4fApbUiiDOjzQgpnQw6QOgvyw=/0x0/filters:format(jpeg)/pic3037396.jpg', 'https://cf.geekdo-images.com/gfT_6H4P9wdNQQ2KMU9rHg__thumb/img/qIGTlYnsBqH70p8E_l9nZ837TPM=/fit-in/200x150/filters:strip_icc()/pic3037396.jpg', 14, '3.4268', 4, 1, 7),
(29, 242277, 'Scythe: The Rise of Fenris', 'Empires have risen and fallen in the aftermath of the Great War, and Europa stands on the precipice of a new era. The economy is robust, morale is high, and defenses are strong. There are reports from the countryside of strange soldiers with glowing eyes, but they seem distant and harmless.

Scythe: The Rise of Fenris, the conclusion to the Scythe expansion trilogy, enables two different options for any player count (1-5 if you have Scythe; 1-7 players if you have Invaders from Afar):


     Campaign (8 games): The story of Scythe continues and concludes with an eight-episode campaign. While the campaign includes surprises, unlocks, and persistent elements, it is fully resettable and replayable.
     Modular (11 modules): Instead of—or after—the campaign, the new modules in The Rise of Fenris can be used in various combinations to cater to player preferences. These modules are compatible with all Scythe expansions, and they include a fully cooperative module.


While the exact nature of the episodes and modules will remain a mystery (most of these components are in 5 secret tuckboxes and on 6 punchboards), the components in this expansion include a detailed episodic guidebook, 13 plastic miniatures, 62 wooden tokens, 2 custom dice, 25 tiles, and 100+ cardboard tokens.

—description from the publisher

', NULL, 2018, 1, 5, 75, 150, 150, '8.70983', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/GRp__UYY-wM-i2fg4Qzefw__original/img/XJgcyfvPBsrxdew_vyvf96MUK6I=/0x0/filters:format(jpeg)/pic3911078.jpg', 'https://cf.geekdo-images.com/GRp__UYY-wM-i2fg4Qzefw__thumb/img/qLl_YEnA_TiXfhinS8yqAARKUFY=/fit-in/200x150/filters:strip_icc()/pic3911078.jpg', 12, '3.4078', 4, 1, 5),
(30, 223555, 'Scythe: The Wind Gambit', 'Description from the publisher:

Mankind has long been confined to travel by land and sea, but a new technology has emerged from the greatest minds in Eastern Europa: airships. These steam-driven behemoths sail freely across the sky, aiding their empire''s expansion through innovation and confrontation. As the years pass, the world has come to understand that no single faction will rise above the rest for any span of time. In the hope of decreasing the conflict and increasing the peace, leaders of Europa begin to gather each year to declare a new way for the factions to resolve their differences.

Scythe: The Wind Gambit, an expansion for Scythe, adds two new modules that can be played together or separately at any player count and with either the base game on its own or with other Scythe expansions:

• Airships: (1 miniature per faction; 16 tiles) An airship is a new type of unit that is distinctly different from characters, mechs, and workers. Unlike those units, airships never control territories. Airships are moved via a Move action, and rivers and lakes do not constrain their movement. Each airship has two randomly combined abilities (1 aggressive and 1 passive ability; same combo for all players).

• Resolutions: (8 tiles) The resolution module changes the way a game of Scythe ends. If you play with this module, ignore the standard end-game trigger (when a player places their sixth star, everything stops and the game ends). Instead, the resolution tile for the current game will determine when and how the game ends.

', NULL, 2017, 1, 7, 70, 140, 140, '7.78632', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/kcp2L5EPPr-okBb1jCtxpA__original/img/Z7yDWUewStx7ojT0dXKfuT7KJlc=/0x0/filters:format(jpeg)/pic3487272.jpg', 'https://cf.geekdo-images.com/kcp2L5EPPr-okBb1jCtxpA__thumb/img/WgVl13rTR8CIJos1iBek5BEbRbc=/fit-in/200x150/filters:strip_icc()/pic3487272.jpg', 14, '3.4235', 4, 1, 7),
(31, 373106, 'Sky Team', 'Sky Team is a co-operative game, exclusively for two players, in which you play a pilot and co-pilot at the controls of an airliner. Your goal is to work together as a team to land your airplane in different airports around the world.

To land your plane, you need to silently assign your dice to the correct spaces in your cockpit to balance the axis of your plane, control its speed, deploy the flaps, extend the landing gear, contact the control tower to clear your path, and even have a little coffee to improve your concentration enough to change the value of your dice.

If the aircraft tilts too much and stalls, overshoots the airport, or collides with another aircraft, you lose the game...and your pilot''s license...and probably your life.

From Montreal to Tokyo, each airport offers its own set of challenges. Watch out for the turbulence as this could end up being a bumpy ride!

AWARDS & HONORS

2024 - BoardLive Awards - Winner 
2024 - Gagnant Prix Jokers - catégorie Duo
2024 - Gagnant Gold''n Gob - catégorie 2 joueurs
2024 - Gagnant Mensa d''Or - catégorie Meilleur jeu Duo 
2024 - Nederlandse Spellenprijs 2024 Winner
2024 - Deutscher Spiele Preis 2024 - 2nd place 
2024 - BG Stats - Most popular game
2024 - Gra roku (Game of the year Poland) - 2 player category winner
2024 - International Gamers Awards - 2 player category winner
2023 - Swams des Jahres winner
2024 - Dice Tower Awards - Best 2 player game
2024 - Dice Tower Awards - Best cooperative game
2024 - Dice Tower Awards - Most innovative game
2024 - Spiel des Jahres Winner
2024 - Best Light Game - BBQ Awards
2024 - Best Cooperative Board Game - Origins Awards
2024 - Best 2023 Insider Game - Les Lys (Québec) 
2024 - Game of the Year - Spiel des Jahres 2024 (Germany)
2024 - Best 2-Player & Innovation Gameplay - Big Awards 2024
2024 - Best 2-Player & Cooperative Game - Golden Geek Awards 2023
       Runner up for Best Innovative & Thematic Game - Golden Geek Awards 2023
2023 - Best Cooperative Game - Board Game Quest
2023 - Best 2-Player Game - Board Game Arena Awards
2023 - Best 2-Player Game - Squirrelly Awards
2023 - Best Board Game - Dicebreaker Tabletop Awards
2023 - Two Player Board Game Winner - Game Boy Geek    
2023 - Best Co-Op Game - Gaming Trend    
2023 - Seal of Excellence - Dice Tower

—description from the publisher

', NULL, 2023, 2, 2, 15, 15, 15, '8.1876', NULL, 1, 0, 1, NULL, NULL, '', 'https://cf.geekdo-images.com/uXMeQzNenHb3zK7Hoa6b2w__original/img/mWOQnkpyYBorh_Y1-0Y2o-ew17k=/0x0/filters:format(jpeg)/pic7398904.jpg', 'https://cf.geekdo-images.com/uXMeQzNenHb3zK7Hoa6b2w__thumb/img/WyPClajMWU9lV5BdCXiZnqdZgmU=/fit-in/200x150/filters:strip_icc()/pic7398904.jpg', 12, '2.0561', 2, 1, 2),
(32, 62871, 'Zombie Dice', 'Eat brains. Don''t get shotgunned.

In Zombie Dice, you are a zombie. You want braaains – more brains than any of your zombie buddies. The 13 custom dice are your victims. Push your luck to eat their brains, but stop rolling before the shotgun blasts end your turn! Whoever collects 13 brains first wins. Each game takes 10 to 20 minutes and can be taught in a single round.

Each turn, you take three dice from the box and roll them. A brain symbol is worth one point at the end of the round, while footsteps allow you to reroll this particular dice. Shotgun blasts on the other hand are rather bad, cause if you collect three shotgun blasts during your turn, it is over for you and you get no points. After rolling three dice, you may decide if you want to score your current brain collection or if you want to push your luck by grabbing new dice so you have three again and roll once more.

', NULL, 2010, 2, 99, 10, 20, 20, '6.22982', NULL, 1, 0, 1, NULL, NULL, NULL, 'https://cf.geekdo-images.com/iPy584JMAJYrupqRdQp8gA__original/img/zPbWjPYgLscrjd96Uitf3GTPb34=/0x0/filters:format(jpeg)/pic4991962.jpg', 'https://cf.geekdo-images.com/iPy584JMAJYrupqRdQp8gA__thumb/img/0qjQ2T0wXNZDVvMie54bEVmKeT8=/fit-in/200x150/filters:strip_icc()/pic4991962.jpg', 10, '1.0932', 4, 1, 30);

INSERT INTO "tags" ("id", "normalized_tag", "priority", "is_active", "synonyms", "german_normalized_tag") VALUES
(1, 'Co-op', 50, '1', 'Cooperative,Co-op,Kooperativ,Koop, Co-Op', 'Kooperativ'),
(2, 'Strategy', 1, '1', 'Strategie,Strategy,Strat', 'Strategie'),
(3, 'Area-Control', 1, '1', 'Area Control,Area-Control,Area Influence,Area-Majority,AreaControl,Area_Majority', 'Area-Control'),
(4, 'Competitive', 1, '1', 'Competitive,Kompetetiv,Wettbewerb', 'Competitive'),
(5, 'Assymetric', 1, '1', 'Assymetric,Assymetrisch,Asymmetrisch,Variable-Player-Powers', 'Asymmetrisch'),
(6, 'Miniatures', 1, '1', 'Miniatures,Miniaturen,Figures,Figuren', 'Miniatures'),
(7, 'Mythology', 1, '1', 'Mythology,Mythologie,Mythen', 'Mythologie'),
(8, 'Player-Elimination', 1, '1', 'Player Elimination,Player-Elimination,Spieler-Eliminierung,Spieler-Elimination', 'Player-Elimination'),
(9, 'Egypt', 1, '1', 'Egypt,Ägypten,Ägyptisch', 'Egypt'),
(10, 'Tile-placement', 1, '1', 'Tile Placement,Tile-Placement,Plättchenlegen,Plättchen-Legen,Plättchenlegespiel', 'Tile-placement'),
(11, 'Set-collection', 1, '1', 'Set Collection,Set-Collection,Kartensammlung,Karten-Sammlung', 'Set-collection'),
(12, 'Open-drafting', 1, '1', 'Open Drafting,Open-Drafting,Offenes Drafting,Offenes-Drafting', 'Open-drafting'),
(13, 'Family-game', 1, '1', 'Familienspiel,Familienspiele,Family Game,Family,Familie,Kinderspiel,Kids,Kinderspiel', 'Familienspiel'),
(14, 'Game-of-the-year', 1, '1', 'Spiel des Jahres,SdJ,Spiel-Des-Jahres,Spiel-des-Jahres,spiel_des_jahres', 'Spiel des Jahres'),
(15, 'Card-Drafting', 1, '1', 'Card Drafting,Card-Drafting,Kartendrafting,Karten-Drafting,Card_Drafting', 'Card-Drafting'),
(16, 'Eurogame', 1, '1', 'Eurogame,Euro-Game,Euro,Euro-Style', 'Eurogame'),
(17, 'Tableau-Builder', 1, '1', 'Tableau Builder,Tableau-Builder,Tableau-Building,Tableau-Building', 'Tableau-Builder'),
(18, 'Card-Game', 1, '1', 'Card Game,Card-Game,Kartenspiel,Karten-Spiel,card,cards,cardgame', 'Kartenspiel'),
(19, 'Viking', 1, '1', 'Viking,Vikings,Wikinger', 'Wikinger'),
(20, 'Fantasy', 1, '1', 'Fantasy,Fantasie,Phantasy', 'Fantasy'),
(21, 'Kennerspiel', 1, '1', 'Kennerspiel,Kennerspiel des Jahres,Kennerspiel-des-Jahres,Kennerspiel-des-Jahres,Kenner&Expertenspiele', 'Kennerspiel'),
(22, 'Expert-game', 1, '1', 'Expertenspiel,Expertenspiel des Jahres,Expertenspiel-des-Jahres,Expertenspiel-des-Jahres,Kenner&Expertenspiele,Expert', 'Expertenspiel'),
(23, 'Ameritrash', 1, '1', 'Ameritrash,Amerikatrash,Amerika-Trash', 'Ameritrash'),
(24, 'Worker-Placement', 1, '1', 'Worker Placement,Worker-Placement,Arbeiterplatzierung,Arbeiter-Platzierung', 'Worker-Placement'),
(25, 'Deckbuilding', 1, '1', 'Deck Builder,Deck-Builder,Deckbuilding,Deck-Building', 'Deckbuilder'),
(26, 'Roll-And-Write', 1, '1', 'Roll and Write,Roll-And-Write,Roll-n-Write,Roll-n-Write,roll-&-write,X-And-Write', 'Roll-And-Write'),
(27, 'Flip-and-write', 1, '1', 'Flip and Write,Flip-and-Write,Flip-n-Write,Flip-n-Write,flip-&-write', 'Flip-and-write'),
(28, 'Sci-Fi', 1, '1', 'Sci-Fi,Science Fiction,Science-Fiction,ScienceFiction', 'Sci-Fi'),
(29, 'Duel', 30, '1', 'Duell,Duel,Duellspiel,Duel Game, 2-Player, 2-Players', 'Duell'),
(30, 'Modular-Board', 1, '1', 'Modular Board,Modular-Board,Modulares Spielbrett,Modulares-Spielbrett', 'Modulares Spielbrett'),
(31, 'Zombies', 1, '1', 'Zombies,Zombie,Zombi', 'Zombies'),
(32, 'Push-Your-Luck', 1, '1', 'Push Your Luck,Push-Your-Luck,Push-Your-Luck-Spiel,Push-Your-Luck-Game', 'Push-Your-Luck'),
(33, 'Deduction', 5, '1', 'Deduction,Deduktions-Spiel,Deduktions-Spiel,Déduction,Deduktion', 'Deduktion'),
(34, 'EngineBuilding', 1, '1', 'Engine Building,Engine-Building,Enginebuilder,Engine-Builder', 'Enginebuilder'),
(35, 'Cthulhu', 1, '1', 'Cthulhu,Cthulhu-Mythos,Cthulhu-Mythologie', 'Cthulhu'),
(36, 'Robots', 1, '1', 'Robots,Robot,Roboter', 'Roboter'),
(37, 'Chaotic', 1, '1', 'chaotic,chaotisch,chaos', 'Chaotisch'),
(38, 'Geschicklichkeit', 1, '1', 'Geschicklichkeit,Geschicklichkeitsspiel,Skill,Skill Game,Geschicklichkeit', 'Geschicklichkeit'),
(39, 'Dice-game', 1, '1', 'Würfelspiel,Würfel,Würfel-Spiel,Dice Game,Dice,Component:Dice ', 'Würfelspiel'),
(40, 'Party-Game', 1, '1', 'Party Game,Party-Game,Partyspiel,Party,Party-Spiel', 'Partyspiel'),
(41, 'Animals', 1, '1', 'Animals,Animal,Tiere,Tier', 'Tiere'),
(42, 'Quiz', 1, '1', 'Quiz,Quiz-Spiel,Quiz Game,Quizspiel', 'Quiz'),
(43, 'Halloween', 1, '1', 'Halloween,Halloween-Spiel,Halloween-Game', 'Halloween'),
(44, 'Word-Game', 7, '1', 'word-game, Wordgame, Wortspiel, wortspiel, word, Word-games', 'Wortspiel');

INSERT INTO "users" ("id", "username", "hashed_password", "is_active", "role") VALUES
(2, 'Paddy', '$2b$12$SJQPvtDkDTxrWbc5JhdPPOzavgVhQXOIAYP3jZnYzJztNfq0dW4uO', '1', 'admin'),
(3, 'admin', '$2b$12$UQtZ52.SHOZE3r.RmCn3l.H2XnRFCTY0X0SoTEuAtkukB8Gg3H/Ku', '1', 'admin');



INSERT INTO "game_similarities" ("id", "game_id", "similar_game_id", "similarity_score", "shared_tags_count", "tag_priority_sum") VALUES
(1, 1, 5, '10.8', 9, '18.0'),
(2, 1, 26, '9.6', 8, '16.0'),
(3, 1, 10, '7.2', 6, '12.0'),
(4, 1, 17, '6.0', 5, '10.0'),
(5, 1, 22, '6.0', 5, '10.0'),
(6, 1, 28, '6.0', 5, '10.0'),
(7, 1, 29, '6.0', 5, '10.0'),
(8, 1, 30, '6.0', 5, '10.0'),
(9, 1, 3, '4.8', 4, '8.0'),
(10, 1, 7, '4.8', 4, '8.0'),
(11, 2, 1, '3.6', 3, '6.0'),
(12, 2, 5, '2.4', 2, '4.0'),
(13, 2, 26, '2.4', 2, '4.0'),
(14, 2, 28, '2.4', 2, '4.0'),
(15, 2, 29, '2.4', 2, '4.0'),
(16, 2, 30, '2.4', 2, '4.0'),
(17, 2, 8, '1.2', 1, '2.0'),
(18, 2, 10, '1.2', 1, '2.0'),
(19, 2, 27, '1.2', 1, '2.0'),
(20, 3, 26, '9.6', 8, '16.0'),
(21, 3, 15, '8.4', 7, '14.0'),
(22, 3, 5, '7.2', 6, '12.0'),
(23, 3, 7, '7.2', 6, '12.0'),
(24, 3, 9, '7.2', 6, '12.0'),
(25, 3, 17, '7.2', 6, '12.0'),
(26, 3, 6, '6.0', 5, '10.0'),
(27, 3, 10, '6.0', 5, '10.0'),
(28, 3, 16, '6.0', 5, '10.0'),
(29, 3, 21, '6.0', 5, '10.0'),
(30, 4, 3, '4.8', 4, '8.0'),
(31, 4, 6, '4.8', 4, '8.0'),
(32, 4, 7, '4.8', 4, '8.0'),
(33, 4, 16, '4.8', 4, '8.0'),
(34, 4, 17, '4.8', 4, '8.0'),
(35, 4, 19, '4.8', 4, '8.0'),
(36, 4, 11, '3.6', 3, '6.0'),
(37, 4, 14, '3.6', 3, '6.0'),
(38, 4, 15, '3.6', 3, '6.0'),
(39, 4, 20, '3.6', 3, '6.0'),
(40, 5, 26, '16.8', 14, '28.0'),
(41, 5, 1, '10.8', 9, '18.0'),
(42, 5, 10, '10.8', 9, '18.0'),
(43, 5, 17, '10.8', 9, '18.0'),
(44, 5, 28, '8.4', 7, '14.0'),
(45, 5, 29, '8.4', 7, '14.0'),
(46, 5, 30, '8.4', 7, '14.0'),
(47, 5, 3, '7.2', 6, '12.0'),
(48, 5, 7, '6.0', 5, '10.0'),
(49, 5, 14, '6.0', 5, '10.0'),
(50, 6, 3, '6.0', 5, '10.0'),
(51, 6, 16, '6.0', 5, '10.0'),
(52, 6, 4, '4.8', 4, '8.0'),
(53, 6, 7, '4.8', 4, '8.0'),
(54, 6, 15, '4.8', 4, '8.0'),
(55, 6, 17, '4.8', 4, '8.0'),
(56, 6, 19, '4.8', 4, '8.0'),
(57, 6, 20, '4.8', 4, '8.0'),
(58, 6, 26, '4.8', 4, '8.0'),
(59, 6, 32, '4.8', 4, '8.0'),
(60, 7, 17, '8.4', 7, '14.0'),
(61, 7, 26, '8.4', 7, '14.0'),
(62, 7, 3, '7.2', 6, '12.0'),
(63, 7, 5, '6.0', 5, '10.0'),
(64, 7, 14, '6.0', 5, '10.0'),
(65, 7, 19, '6.0', 5, '10.0'),
(66, 7, 1, '4.8', 4, '8.0'),
(67, 7, 4, '4.8', 4, '8.0'),
(68, 7, 6, '4.8', 4, '8.0'),
(69, 7, 15, '4.8', 4, '8.0'),
(70, 8, 14, '9.4', 3, '64.0'),
(71, 8, 31, '7.0', 1, '60.0'),
(72, 8, 10, '4.8', 4, '8.0'),
(73, 8, 26, '3.6', 3, '6.0'),
(74, 8, 1, '2.4', 2, '4.0'),
(75, 8, 5, '2.4', 2, '4.0'),
(76, 8, 17, '2.4', 2, '4.0'),
(77, 8, 21, '2.4', 2, '4.0'),
(78, 8, 22, '2.4', 2, '4.0'),
(79, 8, 28, '2.4', 2, '4.0'),
(80, 9, 22, '15.8', 5, '108.0'),
(81, 9, 28, '13.4', 3, '104.0'),
(82, 9, 29, '13.4', 3, '104.0'),
(83, 9, 30, '13.4', 3, '104.0'),
(84, 9, 27, '12.2', 2, '102.0'),
(85, 9, 3, '7.2', 6, '12.0'),
(86, 9, 26, '6.0', 5, '10.0'),
(87, 9, 7, '3.6', 3, '6.0'),
(88, 9, 15, '3.6', 3, '6.0'),
(89, 9, 1, '2.4', 2, '4.0'),
(90, 10, 26, '12.0', 10, '20.0'),
(91, 10, 5, '10.8', 9, '18.0'),
(92, 10, 1, '7.2', 6, '12.0'),
(93, 10, 17, '7.2', 6, '12.0'),
(94, 10, 28, '7.2', 6, '12.0'),
(95, 10, 29, '7.2', 6, '12.0'),
(96, 10, 3, '6.0', 5, '10.0'),
(97, 10, 14, '6.0', 5, '10.0'),
(98, 10, 21, '6.0', 5, '10.0'),
(99, 10, 22, '6.0', 5, '10.0'),
(100, 11, 3, '3.6', 3, '6.0'),
(101, 11, 4, '3.6', 3, '6.0'),
(102, 11, 6, '3.6', 3, '6.0'),
(103, 11, 7, '3.6', 3, '6.0'),
(104, 11, 14, '3.6', 3, '6.0'),
(105, 11, 15, '3.6', 3, '6.0'),
(106, 11, 16, '3.6', 3, '6.0'),
(107, 11, 17, '3.6', 3, '6.0'),
(108, 11, 19, '3.6', 3, '6.0'),
(109, 11, 26, '3.6', 3, '6.0'),
(110, 12, 32, '6.0', 5, '10.0'),
(111, 12, 1, '3.6', 3, '6.0'),
(112, 12, 14, '3.6', 3, '6.0'),
(113, 12, 17, '3.6', 3, '6.0'),
(114, 12, 3, '2.4', 2, '4.0'),
(115, 12, 4, '2.4', 2, '4.0'),
(116, 12, 5, '2.4', 2, '4.0'),
(117, 12, 6, '2.4', 2, '4.0'),
(118, 12, 7, '2.4', 2, '4.0'),
(119, 12, 10, '2.4', 2, '4.0'),
(120, 14, 31, '13.8', 6, '78.0'),
(121, 14, 17, '9.6', 8, '16.0'),
(122, 14, 8, '9.4', 3, '64.0'),
(123, 14, 26, '7.2', 6, '12.0'),
(124, 14, 19, '6.8', 5, '18.0'),
(125, 14, 5, '6.0', 5, '10.0'),
(126, 14, 7, '6.0', 5, '10.0'),
(127, 14, 10, '6.0', 5, '10.0'),
(128, 14, 1, '4.8', 4, '8.0'),
(129, 14, 3, '4.8', 4, '8.0'),
(130, 15, 3, '8.4', 7, '14.0'),
(131, 15, 26, '7.2', 6, '12.0'),
(132, 15, 5, '6.0', 5, '10.0'),
(133, 15, 17, '6.0', 5, '10.0'),
(134, 15, 6, '4.8', 4, '8.0'),
(135, 15, 7, '4.8', 4, '8.0'),
(136, 15, 14, '4.8', 4, '8.0'),
(137, 15, 16, '4.8', 4, '8.0'),
(138, 15, 21, '4.8', 4, '8.0'),
(139, 15, 22, '4.8', 4, '8.0'),
(140, 16, 3, '6.0', 5, '10.0'),
(141, 16, 6, '6.0', 5, '10.0'),
(142, 16, 17, '6.0', 5, '10.0'),
(143, 16, 4, '4.8', 4, '8.0'),
(144, 16, 7, '4.8', 4, '8.0'),
(145, 16, 15, '4.8', 4, '8.0'),
(146, 16, 19, '4.8', 4, '8.0'),
(147, 16, 20, '4.8', 4, '8.0'),
(148, 16, 23, '4.8', 4, '8.0'),
(149, 16, 26, '4.8', 4, '8.0'),
(150, 17, 5, '10.8', 9, '18.0'),
(151, 17, 26, '10.8', 9, '18.0'),
(152, 17, 14, '9.6', 8, '16.0'),
(153, 17, 7, '8.4', 7, '14.0'),
(154, 17, 3, '7.2', 6, '12.0'),
(155, 17, 10, '7.2', 6, '12.0'),
(156, 17, 19, '7.2', 6, '12.0'),
(157, 17, 1, '6.0', 5, '10.0'),
(158, 17, 15, '6.0', 5, '10.0'),
(159, 17, 16, '6.0', 5, '10.0'),
(160, 18, 3, '2.4', 2, '4.0'),
(161, 18, 9, '2.4', 2, '4.0'),
(162, 18, 21, '2.4', 2, '4.0'),
(163, 18, 22, '2.4', 2, '4.0'),
(164, 18, 26, '2.4', 2, '4.0'),
(165, 18, 32, '2.4', 2, '4.0'),
(166, 18, 1, '1.2', 1, '2.0'),
(167, 18, 5, '1.2', 1, '2.0'),
(168, 18, 6, '1.2', 1, '2.0'),
(169, 18, 7, '1.2', 1, '2.0'),
(170, 19, 17, '7.2', 6, '12.0'),
(171, 19, 26, '7.2', 6, '12.0'),
(172, 19, 14, '6.8', 5, '18.0'),
(173, 19, 5, '6.0', 5, '10.0'),
(174, 19, 7, '6.0', 5, '10.0'),
(175, 19, 1, '4.8', 4, '8.0'),
(176, 19, 3, '4.8', 4, '8.0'),
(177, 19, 4, '4.8', 4, '8.0'),
(178, 19, 6, '4.8', 4, '8.0'),
(179, 19, 10, '4.8', 4, '8.0'),
(180, 20, 3, '4.8', 4, '8.0'),
(181, 20, 6, '4.8', 4, '8.0'),
(182, 20, 7, '4.8', 4, '8.0'),
(183, 20, 16, '4.8', 4, '8.0'),
(184, 20, 17, '4.8', 4, '8.0'),
(185, 20, 19, '4.8', 4, '8.0'),
(186, 20, 26, '4.8', 4, '8.0'),
(187, 20, 4, '3.6', 3, '6.0'),
(188, 20, 15, '3.6', 3, '6.0'),
(189, 20, 22, '3.6', 3, '6.0'),
(190, 21, 26, '8.4', 7, '14.0'),
(191, 21, 3, '6.0', 5, '10.0'),
(192, 21, 5, '6.0', 5, '10.0'),
(193, 21, 10, '6.0', 5, '10.0'),
(194, 21, 15, '4.8', 4, '8.0'),
(195, 21, 22, '4.8', 4, '8.0'),
(196, 21, 1, '3.6', 3, '6.0'),
(197, 21, 6, '3.6', 3, '6.0'),
(198, 21, 16, '3.6', 3, '6.0'),
(199, 21, 19, '3.6', 3, '6.0'),
(200, 22, 9, '15.8', 5, '108.0'),
(201, 22, 28, '14.6', 4, '106.0'),
(202, 22, 29, '14.6', 4, '106.0'),
(203, 22, 27, '13.4', 3, '104.0'),
(204, 22, 30, '13.4', 3, '104.0'),
(205, 22, 26, '8.4', 7, '14.0'),
(206, 22, 1, '6.0', 5, '10.0'),
(207, 22, 3, '6.0', 5, '10.0'),
(208, 22, 5, '6.0', 5, '10.0'),
(209, 22, 10, '6.0', 5, '10.0'),
(210, 23, 17, '6.0', 5, '10.0'),
(211, 23, 16, '4.8', 4, '8.0'),
(212, 23, 3, '3.6', 3, '6.0'),
(213, 23, 4, '3.6', 3, '6.0'),
(214, 23, 6, '3.6', 3, '6.0'),
(215, 23, 7, '3.6', 3, '6.0'),
(216, 23, 14, '3.6', 3, '6.0'),
(217, 23, 19, '3.6', 3, '6.0'),
(218, 23, 32, '3.6', 3, '6.0'),
(219, 23, 10, '2.4', 2, '4.0'),
(220, 24, 17, '3.6', 3, '6.0'),
(221, 24, 32, '3.6', 3, '6.0'),
(222, 24, 3, '2.4', 2, '4.0'),
(223, 24, 4, '2.4', 2, '4.0'),
(224, 24, 6, '2.4', 2, '4.0'),
(225, 24, 7, '2.4', 2, '4.0'),
(226, 24, 12, '2.4', 2, '4.0'),
(227, 24, 14, '2.4', 2, '4.0'),
(228, 24, 16, '2.4', 2, '4.0'),
(229, 24, 19, '2.4', 2, '4.0'),
(230, 25, 7, '1.2', 1, '2.0'),
(231, 25, 18, '1.2', 1, '2.0'),
(232, 26, 5, '16.8', 14, '28.0'),
(233, 26, 10, '12.0', 10, '20.0'),
(234, 26, 17, '10.8', 9, '18.0'),
(235, 26, 1, '9.6', 8, '16.0'),
(236, 26, 3, '9.6', 8, '16.0'),
(237, 26, 28, '9.6', 8, '16.0'),
(238, 26, 29, '9.6', 8, '16.0'),
(239, 26, 7, '8.4', 7, '14.0'),
(240, 26, 21, '8.4', 7, '14.0'),
(241, 26, 22, '8.4', 7, '14.0'),
(242, 27, 28, '17.0', 6, '110.0'),
(243, 27, 29, '17.0', 6, '110.0'),
(244, 27, 30, '15.8', 5, '108.0'),
(245, 27, 22, '13.4', 3, '104.0'),
(246, 27, 9, '12.2', 2, '102.0'),
(247, 27, 26, '6.0', 5, '10.0'),
(248, 27, 5, '4.8', 4, '8.0'),
(249, 27, 1, '3.6', 3, '6.0'),
(250, 27, 10, '3.6', 3, '6.0'),
(251, 27, 17, '3.6', 3, '6.0'),
(252, 28, 29, '20.6', 9, '116.0'),
(253, 28, 30, '19.4', 8, '114.0'),
(254, 28, 27, '17.0', 6, '110.0'),
(255, 28, 22, '14.6', 4, '106.0'),
(256, 28, 9, '13.4', 3, '104.0'),
(257, 28, 26, '9.6', 8, '16.0'),
(258, 28, 5, '8.4', 7, '14.0'),
(259, 28, 10, '7.2', 6, '12.0'),
(260, 28, 1, '6.0', 5, '10.0'),
(261, 28, 17, '3.6', 3, '6.0'),
(262, 29, 28, '20.6', 9, '116.0'),
(263, 29, 30, '19.4', 8, '114.0'),
(264, 29, 27, '17.0', 6, '110.0'),
(265, 29, 22, '14.6', 4, '106.0'),
(266, 29, 9, '13.4', 3, '104.0'),
(267, 29, 26, '9.6', 8, '16.0'),
(268, 29, 5, '8.4', 7, '14.0'),
(269, 29, 10, '7.2', 6, '12.0'),
(270, 29, 1, '6.0', 5, '10.0'),
(271, 29, 17, '3.6', 3, '6.0'),
(272, 30, 28, '19.4', 8, '114.0'),
(273, 30, 29, '19.4', 8, '114.0'),
(274, 30, 27, '15.8', 5, '108.0'),
(275, 30, 9, '13.4', 3, '104.0'),
(276, 30, 22, '13.4', 3, '104.0'),
(277, 30, 5, '8.4', 7, '14.0'),
(278, 30, 26, '8.4', 7, '14.0'),
(279, 30, 1, '6.0', 5, '10.0'),
(280, 30, 10, '6.0', 5, '10.0'),
(281, 30, 17, '3.6', 3, '6.0'),
(282, 31, 14, '13.8', 6, '78.0'),
(283, 31, 8, '7.0', 1, '60.0'),
(284, 31, 17, '6.0', 5, '10.0'),
(285, 31, 26, '6.0', 5, '10.0'),
(286, 31, 5, '4.8', 4, '8.0'),
(287, 31, 19, '4.4', 3, '14.0'),
(288, 31, 3, '3.6', 3, '6.0'),
(289, 31, 7, '3.6', 3, '6.0'),
(290, 31, 10, '3.6', 3, '6.0'),
(291, 31, 32, '3.6', 3, '6.0'),
(292, 32, 12, '6.0', 5, '10.0'),
(293, 32, 17, '6.0', 5, '10.0'),
(294, 32, 3, '4.8', 4, '8.0'),
(295, 32, 6, '4.8', 4, '8.0'),
(296, 32, 16, '4.8', 4, '8.0'),
(297, 32, 26, '4.8', 4, '8.0'),
(298, 32, 4, '3.6', 3, '6.0'),
(299, 32, 7, '3.6', 3, '6.0'),
(300, 32, 14, '3.6', 3, '6.0'),
(301, 32, 15, '3.6', 3, '6.0');

INSERT INTO "game_tags" ("game_id", "tag_id") VALUES
(4, 13),
(4, 18),
(4, 41),
(4, 40),
(4, 4),
(26, 17),
(26, 13),
(26, 5),
(26, 2),
(26, 18),
(26, 10),
(26, 21),
(26, 6),
(26, 23),
(26, 34),
(26, 11),
(26, 20),
(26, 22),
(26, 24),
(26, 3),
(26, 28),
(26, 16),
(26, 4),
(5, 17),
(5, 5),
(5, 2),
(5, 21),
(5, 23),
(5, 18),
(5, 6),
(5, 34),
(5, 19),
(5, 15),
(5, 7),
(5, 16),
(5, 3),
(5, 24),
(5, 22),
(5, 20),
(5, 4),
(27, 2),
(27, 1),
(27, 6),
(27, 20),
(27, 28),
(27, 22),
(6, 13),
(6, 18),
(6, 11),
(6, 40),
(6, 4),
(28, 2),
(28, 1),
(28, 6),
(28, 34),
(28, 16),
(28, 22),
(28, 3),
(28, 28),
(28, 20),
(7, 13),
(7, 27),
(7, 18),
(7, 21),
(7, 10),
(7, 2),
(7, 20),
(7, 26),
(7, 40),
(7, 4),
(29, 2),
(29, 1),
(29, 6),
(29, 34),
(29, 16),
(29, 20),
(29, 3),
(29, 28),
(29, 22),
(8, 18),
(8, 25),
(8, 29),
(8, 3),
(8, 28),
(30, 2),
(30, 1),
(30, 6),
(30, 34),
(30, 16),
(30, 20),
(30, 3),
(30, 22),
(9, 13),
(9, 10),
(9, 1),
(9, 14),
(9, 30),
(9, 2),
(9, 11),
(9, 16),
(31, 13),
(31, 33),
(31, 14),
(31, 39),
(31, 21),
(31, 29),
(31, 22),
(31, 24),
(31, 4),
(10, 5),
(10, 25),
(10, 2),
(10, 18),
(10, 34),
(10, 12),
(10, 16),
(10, 22),
(10, 3),
(10, 28),
(10, 24),
(10, 4),
(32, 13),
(32, 39),
(32, 32),
(32, 23),
(32, 43),
(32, 11),
(32, 31),
(32, 40),
(32, 4),
(11, 18),
(11, 13),
(11, 4),
(12, 32),
(12, 18),
(12, 39),
(12, 43),
(12, 8),
(12, 31),
(12, 4),
(14, 33),
(14, 13),
(14, 5),
(14, 18),
(14, 39),
(14, 2),
(14, 25),
(14, 21),
(14, 29),
(14, 4),
(15, 13),
(15, 17),
(15, 18),
(15, 2),
(15, 11),
(15, 15),
(15, 4),
(16, 13),
(16, 18),
(16, 37),
(16, 11),
(16, 40),
(16, 4),
(17, 13),
(17, 5),
(17, 18),
(17, 39),
(17, 23),
(17, 37),
(17, 2),
(17, 25),
(17, 21),
(17, 15),
(17, 22),
(17, 20),
(17, 40),
(17, 4),
(18, 11),
(18, 39),
(18, 16),
(18, 26),
(19, 13),
(19, 33),
(19, 5),
(19, 18),
(19, 34),
(19, 20),
(19, 40),
(19, 4),
(20, 13),
(20, 18),
(20, 11),
(20, 20),
(20, 40),
(21, 17),
(21, 18),
(21, 11),
(21, 16),
(21, 28),
(21, 34),
(21, 4),
(22, 13),
(22, 5),
(22, 1),
(22, 35),
(22, 18),
(22, 2),
(22, 43),
(22, 11),
(22, 7),
(22, 16),
(22, 28),
(1, 9),
(1, 5),
(1, 2),
(1, 18),
(1, 6),
(1, 8),
(1, 7),
(1, 16),
(1, 3),
(1, 20),
(1, 4),
(23, 13),
(23, 37),
(23, 25),
(23, 40),
(23, 36),
(23, 4),
(2, 9),
(2, 6),
(2, 3),
(24, 39),
(24, 40),
(24, 4),
(3, 13),
(3, 17),
(3, 10),
(3, 14),
(3, 2),
(3, 18),
(3, 11),
(3, 16),
(3, 15),
(3, 12),
(3, 40),
(3, 4),
(25, 26);