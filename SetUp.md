# Doodle Poll Game

- [Doodle Poll Game](#doodle-poll-game)
  - [Programming language](#programming-language)
  - [Type of programming](#type-of-programming)
  - [Structure](#structure)
    - [Design choices](#design-choices)
    - [Assumptions](#assumptions)
    - [Poll](#poll)
      - [Attributes](#attributes)
      - [Functions](#functions)
    - [Player](#player)
      - [Attributes](#attributes-1)
      - [Functions](#functions-1)
    - [Date](#date)
      - [Attributes](#attributes-2)
      - [Functions](#functions-2)


## Programming language

Python 

## Type of programming

Object oriented (I think)

## Structure 

three classes: Poll, Player, Date 

### Design choices

- Does the date have the score or is that stored in the poll? (currently it is stored in the date itself)
- Does the number of dates & voters get decided when creating the poll or afterwards (when creating probably makes more sense) (currently the number of dates gets decided when making the poll, but users get added one by one to make sure an adequately sized list of preferences can be created) 

### Assumptions 
- The dates do not change after the poll was created 


### Poll

#### Attributes

- Set of voters
- Set of dates
- Set of winning dates
  
#### Functions

- add player
- add date
- choose winner 
- get players
- get dates 
- get winners

### Player

#### Attributes 

- Vector of "ballots"
- Preferences
- Utility (based on Z. Sbratsova et al)
- Strategy
- ID 

#### Functions 

- set preferences 
- set vote 
- description thing which displays ID when the thing is printed

### Date 

#### Attributes

- Score
- ID 

#### Functions
- get score
- add to score 

