"""Algorithms which are related to US-American linguist N. Chomsky."""


import dataclasses
import typing

import treelib

from mutwo import core_utilities


__all__ = ("NonTerminal", "Terminal", "ContextFreeGrammarRule", "ContextFreeGrammar")


class NonTerminal(object):
    """Can be used as a Mixin to define context-free grammar."""

    pass


class Terminal(object):
    """Can be used as a Mixin to define context-free grammar."""

    pass


@dataclasses.dataclass
class ContextFreeGrammarRule(object):
    """Describe a context_free_grammar_rule for a :class:`ContextFreeGrammar`"""

    left_side: NonTerminal
    right_side: tuple[typing.Union[NonTerminal, Terminal], ...]


class ContextFreeGrammar(object):
    """Describe a context-free grammar and resolve non-terminals

    :param context_free_grammar_rule_sequence: A sequence of :class:`ContextFreeGrammarRule` objects. It is
        allowed to provide multiple context_free_grammar_rules with the same :attribute:`left_side`.
    :type context_free_grammar_rule_sequence: typing.Sequence[ContextFreeGrammarRule]

    This is a very reduced implementation of a context-free grammar
    which only provides the most basic functions. It is not made for
    the purpose of parsing text but rather as a technique to generate
    algorithmic data (for the sake of art creation). Therefore it is
    all about the resolution of start objects to variants of this start.
    """

    def __init__(
        self,
        context_free_grammar_rule_sequence: typing.Sequence[ContextFreeGrammarRule],
    ):
        self._non_terminal_tuple = core_utilities.uniqify_sequence(
            tuple(
                context_free_grammar_rule.left_side
                for context_free_grammar_rule in context_free_grammar_rule_sequence
            )
        )
        divided_context_free_grammar_rule_list = [[] for _ in self._non_terminal_tuple]
        for context_free_grammar_rule in context_free_grammar_rule_sequence:
            index = self._non_terminal_tuple.index(  # type: ignore
                context_free_grammar_rule.left_side
            )
            divided_context_free_grammar_rule_list[index].append(
                context_free_grammar_rule
            )
        self._divided_context_free_grammar_rule_tuple = tuple(
            tuple(context_free_grammar_rule_list)
            for context_free_grammar_rule_list in divided_context_free_grammar_rule_list
        )

    def get_context_free_grammar_rule_tuple(
        self, non_terminal: NonTerminal
    ) -> tuple[ContextFreeGrammarRule, ...]:
        """Find all defined context_free_grammar_rules for the provided :class:`NonTerminal`.

        :param non_terminal: The left side element of the :class:`ContextFreeGrammarRule`.
        :type non_terminal: NonTerminal
        """
        index = self._non_terminal_tuple.index(non_terminal)  # type: ignore
        return self._divided_context_free_grammar_rule_tuple[index]

    def _data_to_tag(
        self, data: tuple[typing.Union[NonTerminal, Terminal], ...]
    ) -> str:
        return str(data)

    def _add_node(
        self,
        tree: treelib.Tree,
        data: tuple[typing.Union[NonTerminal, Terminal], ...],
        parent: typing.Optional[treelib.Node] = None,
    ):
        tree.create_node(self._data_to_tag(data), data=data, parent=parent)

    def _resolve_content(
        self, content: tuple[typing.Union[NonTerminal, Terminal], ...]
    ) -> tuple[tuple[typing.Union[NonTerminal, Terminal], ...], ...]:
        new_data_list = []
        for nth_element, element in enumerate(content):
            if isinstance(element, NonTerminal):
                context_free_grammar_rule_tuple = (
                    self.get_context_free_grammar_rule_tuple(element)
                )
                for context_free_grammar_rule in context_free_grammar_rule_tuple:
                    data = (
                        content[:nth_element]
                        + context_free_grammar_rule.right_side
                        + content[nth_element + 1 :]
                    )
                    new_data_list.append(data)
        return tuple(new_data_list)

    def resolve_one_layer(self, tree: treelib.Tree) -> bool:
        """Resolve all leaves of the tree.

        :param tree: The tree from which all leaves should
            be resolved.
        :type tree: treelib.Tree
        :return: `True` if any leaf has been resolved and `False`
            if no resolution has happened (e.g. if there are only
            :class:`Terminal` left).
        """

        new_node = False
        for leaf in tree.leaves():
            data_tuple = self._resolve_content(leaf.data)
            for data in data_tuple:
                self._add_node(tree, data, leaf)
                new_node = True
        return new_node

    def resolve(
        self, start: NonTerminal, limit: typing.Optional[int] = None
    ) -> treelib.Tree:
        """Resolve until only :class:`Terminal` are left or the limit is reached.

        :param start: The start value.
        :type start: NonTerminal
        :param limit: The maximum node levels until the function returns a tree.
            If it is set to `None` it will only stop once all nodes are
            :class:`Terminal`.
        :type limit: typing.Optional[int]
        """

        def is_limit_reached() -> bool:
            if limit is None:
                return False
            else:
                return limit <= counter

        tree = treelib.Tree()
        self._add_node(tree, (start,))
        is_not_resolved = True
        counter = 0
        while is_not_resolved and not is_limit_reached():
            is_not_resolved = self.resolve_one_layer(tree)
            counter += 1
        return tree
