Retrosheet Data Structure
-------------------------
- first column indicates data type

- "id" type breaks the csv into game sections
- The "id" value is 3 letter team abbreviation (DET) YYYYMMDDX where I believe X is the game number of the day i.e. double headers

- "version" type
- integer (version number)

- "info" type
- the subsequent 2 keys are a key-value pair that should be treated as strings

- "start" type
- followed by: player id, name in quoted, integer, integer, integer

- "play" and "sub" are mixed together, and appear sequential
  - "play" type
  - integer, integer, player id, string, string, string
  - "sub" type
  - player id, name, integer, integer, integer

- "data" type
- string, player id, integer

Description (http://www.retrosheet.org/eventfile.htm)

Base Tables
- Starter table
  - game_id (string), player id, name, integer, integer, integer

- Play-by-play table
  - game_id, player id, play sequence, play type (play or sub), ? flatten data 

- Game Info table
  - game_id (string), visiting team, hometeam, site, date, info (json) 
