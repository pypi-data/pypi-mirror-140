from .nxx import (
    enumerate_cliques_with_weights,
    enumerate_cliques_with_weights_noprune,
    maxclique_decompose_with_weights,
    enumerate_cliques_with_weights_edgeonly,
) # from Rust `src/lib.rs`

import numpy as np
from scipy.spatial import distance_matrix
from typing import Literal, Union, List

def geom2frag(
    coords,
    *,
    cutoff: Union[float, List[float], None] = None,
    jl: Union[float, bool] = False,
    clique_method: Literal['enumerate', 'decompose'] ='enumerate',
    maxrank: int = 2,
    edge_quickpath: bool = True,
):
    """Generate a graph from a geometry, then extract a list of cliques with their corresponding
    overlap weights.

    Args:
        coords: coordinates of the nodes
        cutoff: (for graph construction) distance cutoff, or a list of cutoff for each node
        jl: (for graph construction) Junjie's algorithm. If truthy, the zero items in the
            ``cutoff`` param will be replaced by ``jl * min(edges of this node)``; True implies
            the default value of 1.1.
        clique_method: (for clique extraction) method ``enumerate`` starts from nodes and works
            upwards, while ``decompose`` starts from the maximal cliques and works down. Method
            ``enumerate`` is faster and is preferred in most cases.
        maxrank: (for clique extraction) maximum rank of the cliques to be extracted. Note that
            the rank convention is 1-based, i.e. nodes count as rank 1.
        edge_quickpath: (for clique extraction) Use heuristic when ``maxrank=2``.

    Returns:
        a list of cliques (list[tuple[int]]) generated, along with a list of corresponding weights
        (list[int])
    """
    dist = distance_matrix(coords, coords)
    if jl:
        dist[np.diag_indices_from(dist)] = 1000.0
        jl = 1.1 if jl is True else jl # for O-O, 1.1
        cutoff_jl = np.amin(dist, axis=1) * jl
        if cutoff:
            cutoff = np.array(cutoff)
            cutoff_jl[cutoff>0] = cutoff[cutoff>0]
        cutoff = cutoff_jl
    elif cutoff is None:
        raise ValueError("At least one of cutoff and jl need to be specified")
    if maxrank == 2 and edge_quickpath:
        cq, w = enumerate_cliques_with_weights_edgeonly(_adj(dist, cutoff))
    elif clique_method == 'enumerate':
        cq, w = enumerate_cliques_with_weights(_nbr(dist, cutoff), maxrank)
    elif clique_method == 'decompose':
        cq, w = maxclique_decompose_with_weights(_adj(dist, cutoff), maxrank)
    else:
        raise ValueError(f'clique extration method {clique_method!r} is not supported')
    return list(map(tuple, cq)), w

def _nbr(dist, cutoff):
    if hasattr(cutoff, '__getitem__'):
        cutoff = np.maximum.outer(cutoff, cutoff)
    conn = np.triu(dist < cutoff, 1)
    return [np.nonzero(u)[0] for u in conn]

def _adj(dist, cutoff):
    if hasattr(cutoff, '__getitem__'):
        cutoff = np.maximum.outer(cutoff, cutoff)
    conn = dist < cutoff
    conn[np.diag_indices_from(conn)] = False
    return [np.nonzero(u)[0] for u in conn]
