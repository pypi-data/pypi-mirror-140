"""Algorithms which are related to the mutwo author L.E. Zimmermann"""

from __future__ import annotations
import itertools
import typing

import primesieve
import treelib

from mutwo import common_generators
from mutwo import core_utilities
from mutwo import music_parameters

__all__ = (
    "PitchBasedContextFreeGrammar",
    "JustIntonationPitchTerminal",
    "JustIntonationPitchNonTerminal",
)


class JustIntonationPitchNonTerminal(
    music_parameters.JustIntonationPitch, common_generators.NonTerminal
):
    pass


class JustIntonationPitchTerminal(
    music_parameters.JustIntonationPitch, common_generators.Terminal
):
    pass


class PitchBasedContextFreeGrammar(common_generators.ContextFreeGrammar):
    """Create `JustIntonationPitch` sequences from single intervals.

    This class is a simple :class:`mutwo.common_generators.ContextFreeGrammar`
    with alternative constructor methods and an additional filter function
    which avoids adding undesired parts to the resulting :class:`treelib.Tree`.
    The implementation is based on the text "Bewegungen im unendlichen Tonraum"
    (2018) from L.E. Zimmermann.

    **Example**:

    >>> from mutwo import zimmermann_generators
    >>> pitch_based_context_free_grammar = (
    >>>     zimmermann_generators.PitchBasedContextFreeGrammar.from_constraints(
    >>>         prime_number_to_maximum_exponent_dict={3: 1, 5: 1},
    >>>         maximum_cent_deviation=550,
    >>>     )
    >>> )
    >>> resolution = pitch_based_context_free_grammar.resolve(
    >>>     zimmermann_generators.JustIntonationPitchNonTerminal("5/4"),
    >>>     limit=3
    >>> )
    >>> resolution.show()
    (5/4)
    ├── (15/16 4/3)
    │   └── (15/16 5/4 16/15)
    │       └── (15/16 15/16 4/3 16/15)
    └── (4/3 15/16)
        └── (16/15 5/4 15/16)
            └── (16/15 4/3 15/16 15/16)
    """

    @staticmethod
    def _maximum_exponent_to_allowed_exponent_tuple(
        maximum_exponent: int,
    ) -> tuple[int, ...]:
        return tuple(range(1, maximum_exponent + 1)) + tuple(
            range(-maximum_exponent, 0)
        )

    @staticmethod
    def _add_pitch_to_terminal_list_or_non_terminal_list(
        minimal_barlow_harmonicity_non_terminal: float,
        minimal_barlow_harmonicity_terminal: float,
        prime_number_tuple: tuple[int, ...],
        exponent_tuple: tuple[int, ...],
        ascending_prime_tuple: tuple[int, ...],
        non_terminal_list: list[JustIntonationPitchNonTerminal],
        terminal_list: list[JustIntonationPitchTerminal],
        octave: int,
        maximum_cent_deviation: float,
    ):
        complete_exponent_list = [
            exponent_tuple[prime_number_tuple.index(prime)]
            if prime in prime_number_tuple
            else 0
            for prime in ascending_prime_tuple
        ]
        just_intonation_pitch = music_parameters.JustIntonationPitch(
            complete_exponent_list
        ).register(octave)
        if abs(just_intonation_pitch.cents) <= maximum_cent_deviation:
            harmonicity_simplified_barlow = (
                just_intonation_pitch.harmonicity_simplified_barlow
            )
            if harmonicity_simplified_barlow >= minimal_barlow_harmonicity_non_terminal:
                non_terminal_list.append(
                    JustIntonationPitchNonTerminal(just_intonation_pitch.exponent_tuple)
                )
            elif harmonicity_simplified_barlow >= minimal_barlow_harmonicity_terminal:
                terminal_list.append(
                    JustIntonationPitchTerminal(just_intonation_pitch.exponent_tuple)
                )

    @staticmethod
    def _get_terminal_tuple_and_non_terminal_tuple(
        minimal_barlow_harmonicity_non_terminal: float,
        minimal_barlow_harmonicity_terminal: float,
        prime_number_to_maximum_exponent_dict: dict[int, int],
        allowed_octave_sequence: typing.Sequence[int],
        maximum_cent_deviation: float,
    ) -> tuple[
        tuple[JustIntonationPitchNonTerminal, ...],
        tuple[JustIntonationPitchTerminal, ...],
    ]:
        terminal_list = []
        non_terminal_list = []

        prime_number_tuple = tuple(prime_number_to_maximum_exponent_dict.keys())
        prime_number_to_allowed_exponent_tuple_dict = {
            prime_number: PitchBasedContextFreeGrammar._maximum_exponent_to_allowed_exponent_tuple(
                maximum_exponent
            )
            for prime_number, maximum_exponent in prime_number_to_maximum_exponent_dict.items()
        }
        # All occuring primes until the highest prime
        ascending_prime_tuple = tuple(primesieve.primes(max(prime_number_tuple)))

        for n_prime_numbers in range(1, len(prime_number_to_maximum_exponent_dict) + 1):
            for combined_prime_number_tuple in itertools.combinations(
                prime_number_tuple, n_prime_numbers
            ):
                for exponent_tuple in itertools.product(
                    *[
                        prime_number_to_allowed_exponent_tuple_dict[prime_number]
                        for prime_number in combined_prime_number_tuple
                    ]
                ):
                    for octave in allowed_octave_sequence:
                        PitchBasedContextFreeGrammar._add_pitch_to_terminal_list_or_non_terminal_list(
                            minimal_barlow_harmonicity_non_terminal,
                            minimal_barlow_harmonicity_terminal,
                            combined_prime_number_tuple,
                            exponent_tuple,
                            ascending_prime_tuple,
                            non_terminal_list,
                            terminal_list,
                            octave,
                            maximum_cent_deviation,
                        )
        return tuple(non_terminal_list), tuple(terminal_list)

    @classmethod
    def from_constraints(
        cls,
        minimal_barlow_harmonicity_non_terminal: float = 0.1,
        minimal_barlow_harmonicity_terminal: float = 0.05,
        prime_number_to_maximum_exponent_dict: dict[int, int] = {
            3: 2,
            5: 1,
            7: 1,
            11: 1,
        },
        allowed_octave_sequence: typing.Sequence[int] = (-1, 0),
        maximum_cent_deviation: float = 500,
    ) -> PitchBasedContextFreeGrammar:
        """Create rules based on various constraints.

        :param minimal_barlow_harmonicity:
        :param prime_number_sequence:
        :param allowed_octave_sequence:
        :param maximum_cent_deviation:
        """

        assert (
            minimal_barlow_harmonicity_non_terminal
            > minimal_barlow_harmonicity_terminal
        )

        (
            non_terminal_tuple,
            terminal_tuple,
        ) = cls._get_terminal_tuple_and_non_terminal_tuple(
            minimal_barlow_harmonicity_non_terminal,
            minimal_barlow_harmonicity_terminal,
            prime_number_to_maximum_exponent_dict,
            allowed_octave_sequence,
            maximum_cent_deviation,
        )

        element_tuple = non_terminal_tuple + terminal_tuple
        rule_list = []
        for element0, element1 in itertools.combinations(element_tuple, 2):
            summed = element0 + element1
            if summed in non_terminal_tuple:
                non_terminal = non_terminal_tuple[non_terminal_tuple.index(summed)]
                rule_list.extend(
                    (
                        common_generators.ContextFreeGrammarRule(
                            non_terminal, (element0, element1)
                        ),
                        common_generators.ContextFreeGrammarRule(
                            non_terminal, (element1, element0)
                        ),
                    )
                )
        return cls(rule_list)

    def _data_to_tag(
        self,
        data: tuple[
            typing.Union[JustIntonationPitchTerminal, JustIntonationPitchNonTerminal],
            ...,
        ],
    ) -> str:
        return "({})".format(
            " ".join([f"{pitch.numerator}/{pitch.denominator}" for pitch in data])
        )

    def _add_node(
        self,
        tree: treelib.Tree,
        data: tuple[
            typing.Union[JustIntonationPitchTerminal, JustIntonationPitchNonTerminal],
            ...,
        ],
        parent: typing.Optional[treelib.Node] = None,
    ):
        pitch_accumulation = tuple(
            core_utilities.accumulate_from_n(
                data, music_parameters.JustIntonationPitch("1/1")
            )
        )
        if len(core_utilities.uniqify_sequence(pitch_accumulation)) == len(
            pitch_accumulation
        ):
            super()._add_node(tree, data, parent)
