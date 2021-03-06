import pytest
from test_digraph import diamond_cross_graph, diamond_graph  # type: ignore

from nr.util.digraph import DiGraph
from nr.util.digraph.algorithm.remove_with_predecessors import remove_with_predecessors
from nr.util.digraph.algorithm.topological_sort import topological_sort


def test_topological_sort(diamond_graph: DiGraph):
  assert list(topological_sort(diamond_graph)) == ['a', 'b', 'c', 'd']


def test_topological_sort_diamong_cross(diamond_cross_graph: DiGraph):
  assert list(topological_sort(diamond_cross_graph)) == ['a', 'b', 'c', 'd']


def test_remove_with_predecessors_1(diamond_graph: DiGraph):
  remove_with_predecessors(diamond_graph, ['b'])
  assert set(diamond_graph.nodes) == {'a', 'c', 'd'}
  remove_with_predecessors(diamond_graph, ['c'])
  assert set(diamond_graph.nodes) == {'d'}


def test_remove_with_predecessors_2(diamond_graph: DiGraph):
  remove_with_predecessors(diamond_graph, ['b', 'c'])
  assert set(diamond_graph.nodes) == {'d'}


def test_remove_with_predecessors_3(diamond_cross_graph: DiGraph):
  remove_with_predecessors(diamond_cross_graph, ['b', 'c'])
  assert set(diamond_cross_graph.nodes) == {'a', 'd'}


def test_topological_sort_cycle(diamond_graph: DiGraph):
  diamond_graph.add_node('f', None)
  diamond_graph.add_edge('f', 'a', None)
  diamond_graph.add_edge('d', 'a', None)
  with pytest.raises(RuntimeError):
    list(topological_sort(diamond_graph))
