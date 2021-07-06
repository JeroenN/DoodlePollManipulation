# DoodlePoolManipulation

This model was made for the Bachelor Project of Jeroen Niemendal and Isabelle Tilleman. Specifically, this version was made for the Bachelor Project of Isabelle Tilleman. 

None of its contents can be used for any other purpose than work for this project or grading by the supervisor unless explicit permission was given by the contributors. 

## Contents
Below you will find a rough description of the contents of this repository. 

### agent.py
Contains the "agent" class. This class stores all information relevant to the agent, such as utility, willingness, and time slot preference, and contains functions that calculate utility, and create and change time slot preference. 

### environment.py
Contains the "environment" class. This class stores all information relevant to the environment, such at the number of time slots and the number of votes per time slot. This class contains functions that allow agents to vote and to determine the most popular time slot. 

### games.py
Contains the "game" class and the following subclasses of the game class: 
- Normal
- KM
- Agent_slot
- Threshold
- Agent_type

These games are used to run the model and to run experiments related to the effect of different parameters on welfare. 

### main.py
The main part of the program that allows the model to be initiated and the games to be run. 

### normal_distribution.py
Contains functions to calculate the mean and standard deviation of elements in a list. 

### plots.py 
Contains functions used to plot the results of the different games. 

### quick_sort.py
Contains the quick sort function and its required functions. 

### random_number_generator.py
Contains a function to randomly generate number using a normal distribution. 

### strategies.py
Contain all strategies, which are subclasses of "agent":
- Sincere
- Social Sincere
- Popular
- Social Popular
- Popular Prediction
- Social Popular Prediction