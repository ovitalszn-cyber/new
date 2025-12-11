V6 - UNFIED ENPOINT FOR AI DEVS

3 PILLARS
Stats Engine
Odds Engine
Props Engine
Export Engine


(DONE) Stats Engine 
Games
Date/Time
Teams
Players
Box Score
Game Totals
Final Scores
(TheScores API provides all of this)

(DONE) Odds Engine (Live+Pregame)
Live Odds
EU + US Books
Multiple Markets + Multiple Sports
Timestamps For Line History
(Use the current data aggregator and break them down into individual books)
Prop Engine (Player + Markets)
All Markets
Needs To Be Normalized 
Team Props


(Working/ Export Engine (CSV/JSON)
Live Odds
Historical Odds
Game Stats
Prop Markets


- They need to be able to call whatever date they want.
- We dont have historical odds stored.
- We dont have historical props stored.
- We dont have live odds stored.




Dont Forget The Ability To Call Data For A Team and Get All Props and Main Markets For That Game (This All Comes Fromm The Sttored Ccache To Make It Instanttly Fast)

Example

Warriors vs Laker

 Lakers
 market: moneyline
 odds:+123
 Market: spread 
 Line: +3.5
 odds: -112
 Market: total points
 Line: 215
 odds: -112
book:betmgm (whatever book available)
 - Lebron James
prop: Over 25.5 Points
prop: Over 10.5 Rebounds
- Luka Doncic
prop: Over 25.5 Points
prop: Over 10.5 Assists
 

 Warriors
 Market: moneyline
 odds:-123
 Market: spread
 Line: -3.5
 odds: +112
 Market: total points
 Line: 215
 odds: +112

 Stephen Curry
prop: Over 25.5 Points
prop: Over 10.5 Assists
book:prizepicks
Draymond Green
Prop: Over 7.5 Rebounds
Prop: Over 8.5 Assists
 book:prizepicks (whatever book available)

  Stephen Curry
prop: Over 25.5 Points
prop: Over 10.5 Assists
book:prizepicks
Draymond Green
Prop: Over 7.5 Rebounds
Prop: Over 9.5 Assists
 book:underdog (whatever book available)

this isnt polished its the core idea of what we need to build.





Also still need to add my own scrapers, books like rebet, dabble, splashsports etc.

+ dabble
+ rebet
+ splashsports
+ fliff
+ prizepicks
+ underdog

- add them to the props endpoint





-v6/odds is retuurning player props when it only should return main markets (fixed)
- props working when calling a prop markeet like NBA_POINTS it returns the props for that game + requested books has a little dup issue but that fine for now (fixed)
- we still need to setup the docs page (pending)
- problem in main.py, weree only starting lunosoft + background worker, we need to start all sources, create more workers if we have too (pending)
- one thing im noticing is the endpoints are too slow, ensure were using cache and populating it fast and consistently. (in-progess)
- we need to add the dfs books from the props to the book list (NEEEDED)




- verify that the new book still uses our inhouse event generator and not theirs.