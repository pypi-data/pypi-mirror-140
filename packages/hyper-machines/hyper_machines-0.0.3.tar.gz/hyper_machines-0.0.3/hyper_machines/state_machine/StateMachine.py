from itertools import product
from typing import Any

from AbstractStateMachine import AbstractStateMachine


class StateMachine(AbstractStateMachine):
    def __init__(
        self,
        num_attr: int,
        states: list[Any],
        allow_self_transition: bool = False,
        init_state: tuple = (),
    ):
        self.states = states
        super().__init__(num_attr, allow_self_transition)
        if init_state:
            self.current_state = init_state

    def compute_graph(self) -> None:
        permutation_list: list[tuple] = list(product(self.states, repeat=self.num_attr))
        self.compute_from_permutation_list(permutation_list)
