# calliope
# Copyright (C) 2020  Sam Thursfield <sam@afuera.me.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import simpleai
import simpleai.search

import logging
import random

log = logging.getLogger(__name__)


class AppendAction():
    def __init__(self, song):
        self.song = song

    def __repr__(self):
        song_id = self.song.id()
        return f"<{self.__class__.__name__}(id={song_id})>"

    def apply(self, state):
        return state + (self.song,)


class RemoveAction():
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return f"<{self.__class__.__name__}(index={self.index})>"

    def apply(self, state):
        return state[0:self.index] + state[self.index+1:]



class PlaylistGenerationProblem(simpleai.search.SearchProblem):  # pylint: disable=abstract-method
    """Create a playlist using local search algorithm."""
    def __init__(self, collection, constraints, initial_length=0):
        super().__init__(initial_state=tuple())
        self.collection = collection
        self.constraints = constraints
        self.initial_length = initial_length

        self.previous_state = None

        # Create partitions once. This is expensive if input corpus is large.
        self.partitions_good, self.partitions_bad = self.create_input_partitions()

    def create_input_partitions(self):
        """Divide the dataset into one 'good' and some 'bad' partitions.

        This is done per constraint as the constraints will contradict each
        other somewhat.

        """
        partitions_good = dict()
        partitions_bad = dict()
        for constraint in self.constraints:
            good, bad = constraint.partition(self.collection)
            partitions_good[constraint] = good
            partitions_bad[constraint] = bad
        return partitions_good, partitions_bad

    def return_item_to_input_partitions(self, item):
        """Return an item to the partitioned set of input data."""
        for constraint in self.constraints:
            good, bad = constraint.partition([item])
            log.debug("Returning %s to input partitions: %s, %s", item, good, bad)
            if good:
                self.partitions_good[constraint].append(good[0])
            if bad:
                self.partitions_bad[constraint].append(bad[0])

    def generate_random_state(self):
        state = tuple(random.sample(self.collection, self.initial_length))
        log.debug("initial state: %s", state)
        return state

    def make_append_actions_for_partition(self, state, partition, count=None):
        result = []
        duplicates = []
        for item in partition:
            if item in state:
                duplicates.append(item)
            else:
                result += [AppendAction(item)]
            if len(result) >= count:
                break
        return result, duplicates

    def make_remove_actions(self, state, count=None):
        result = []
        options = list(range(0, len(state)))
        random.shuffle(options)
        count = count or len(state)
        while len(result) < count and options:
            pos = options.pop()
            result.append(RemoveAction(pos))
        return result

    def post_iteration_hook(self, state):
        if self.previous_state:
            removed = set(self.previous_state).difference(set(state))
            for item in removed:
                self.return_item_to_input_partitions(item)
        self.previous_state = state

    def actions(self, state):
        # This function is called once per iteration, so we can run a post-hook
        # for the previous iteration.
        self.post_iteration_hook(state)

        append = []
        for p in self.partitions_bad.values():
            actions, duplicates = self.make_append_actions_for_partition(state, p, count=1)
            append += actions
            for item in duplicates:
                p.remove(item)
        for p in self.partitions_good.values():
            actions, duplicates = self.make_append_actions_for_partition(state, p, count=4)
            append += actions
            for item in duplicates:
                p.remove(item)

        remove = self.make_remove_actions(state, count=len(append))

        possible_actions = append + remove
        #random.shuffle(possible_actions)
        log.debug("actions for %s: %s", state, possible_actions)
        return possible_actions

    def result(self, state, action):
        result = action.apply(state)
        return result

    def value(self, state):
        score = sum(c.score_playlist(state) for c in self.constraints) / len(self.constraints)
        log.debug("value %f for playlist %s", score, state)
        return score


def solve(problem, iterations_limit=1000):
    viewer = None

    # This can go pretty wrong, with a duration constraint of 40 and iteration
    # limit of 1000, making playlist with length 1540 !?!    10K iterations better.
    #result = simpleai.search.local.simulated_annealing(problem, iterations_limit=None, viewer=viewer)

    # Works OK! With 1K iterations, still produces randomly bad results, e.g.
    # duration of 1000 for a constraint of 800.
    #result = simpleai.search.local.hill_climbing_stochastic(problem, iterations_limit=1000, viewer=viewer)

    # Works OK! For simple cases goes straight and predictably to the right result.
    result = simpleai.search.local.hill_climbing(problem, iterations_limit=1000, viewer=viewer)

    # Bad results with duration constraint of 40.
    #result = simpleai.search.local.hill_climbing_random_restarts(problem,
    #           restarts_limit=100, iterations_limit=1000, viewer=viewer)

    # These algorithms seem more expensive than the others.
    #result = simpleai.search.local.beam(problem, iterations_limit=100, viewer=viewer)
    #result = simpleai.search.local.beam_best_first(problem, iterations_limit=100, viewer=viewer)

    log.info(result.state)
    log.info(result.path())

    return result
