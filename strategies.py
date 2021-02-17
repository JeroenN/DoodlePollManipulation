from agent import Agent

# This is the standard strategy, agents with this strategy vote for all the time-slots for which the
# agent has a preference above or equal to the specified threshold
class Standard(Agent):
    __threshold = 0.7

    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)

    # vote for a time slot if the time slot preference for that time slot is above the threshold
    # Update also for the particular object that it voted on that specific time slot
    def vote(self):
        for i in range(self._n_time_slots):
            if self._time_slot_preference[i] >= self.__threshold:
                self.environment.vote_time_slot(i)
                self._time_slots_chosen.append(i)

# This is the popular strategy, agents with this strategy look at the most popular time slots and vote for
# the popular time slots that have the highest preference. For this strategy to work the agent has to wait
# for other agents to vote.
class Popular(Agent):
    __rank_popularity_time_slots = []

    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)

