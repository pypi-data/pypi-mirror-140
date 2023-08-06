"""Unit tests for :class:`esmf_regrid.experimental.unstructured_regrid.MeshInfo`."""

import numpy as np
from numpy import ma

from esmf_regrid.esmf_regridder import GridInfo, Regridder
from esmf_regrid.experimental.unstructured_regrid import MeshInfo
from esmf_regrid.tests import get_result_path, make_grid_args


def _make_small_mesh_args():
    ugrid_node_coords = np.array(
        [[0.0, 0.0], [0.0, 10.0], [10.0, 0.0], [10.0, 10.0], [10.0, 20.0]]
    )
    ugrid_face_node_connectivity = ma.array(
        [[0, 2, 3, -1], [3, 0, 1, 4]],
        mask=np.array([[0, 0, 0, 1], [0, 0, 0, 0]]),
    )
    node_start_index = 0
    return ugrid_node_coords, ugrid_face_node_connectivity, node_start_index


def test_make_mesh():
    """Basic test for creating :meth:`~esmf_regrid.esmf_regridder.GridInfo.make_esmf_field`."""
    coords, nodes, _ = _make_small_mesh_args()
    mesh_0 = MeshInfo(coords, nodes, 0)
    esmf_mesh_0 = mesh_0.make_esmf_field()
    esmf_mesh_0.data[:] = 0

    relative_path = (
        "experimental",
        "unstructured_regrid",
        "test_MeshInfo",
        "small_mesh.txt",
    )
    fname = get_result_path(relative_path)
    with open(fname) as file:
        expected_repr = file.read()

    one_indexed_nodes = nodes + 1
    mesh_1 = MeshInfo(coords, one_indexed_nodes, 1)
    esmf_mesh_1 = mesh_1.make_esmf_field()
    esmf_mesh_1.data[:] = 0

    assert esmf_mesh_0.__repr__() == esmf_mesh_1.__repr__() == expected_repr


def test_regrid_with_mesh():
    """Basic test for regridding with :meth:`~esmf_regrid.esmf_regridder.GridInfo.make_esmf_field`."""
    mesh_args = _make_small_mesh_args()
    mesh = MeshInfo(*mesh_args)

    grid_args = make_grid_args(2, 3)
    grid = GridInfo(*grid_args)

    mesh_to_grid_regridder = Regridder(mesh, grid)
    mesh_input = np.array([3, 2])
    grid_output = mesh_to_grid_regridder.regrid(mesh_input)
    expected_grid_output = np.array(
        [
            [2.671294712940605, 3.0],
            [2.0885553467353097, 2.9222786250561574],
            [2.0, 2.3397940801753307],
        ]
    )
    assert ma.allclose(expected_grid_output, grid_output)

    grid_to_mesh_regridder = Regridder(grid, mesh)
    grid_input = np.array([[0, 0], [1, 0], [2, 1]])
    mesh_output = grid_to_mesh_regridder.regrid(grid_input)
    expected_mesh_output = np.array([0.1408245341331448, 1.19732762534643])
    assert ma.allclose(expected_mesh_output, mesh_output)

    def _give_extra_dims(array):
        result = np.stack([array, array + 1])
        result = np.stack([result, result + 10, result + 100])
        return result

    extra_dim_mesh_input = _give_extra_dims(mesh_input)
    extra_dim_grid_output = mesh_to_grid_regridder.regrid(extra_dim_mesh_input)
    extra_dim_expected_grid_output = _give_extra_dims(expected_grid_output)
    assert ma.allclose(extra_dim_expected_grid_output, extra_dim_grid_output)

    extra_dim_grid_input = _give_extra_dims(grid_input)
    extra_dim_mesh_output = grid_to_mesh_regridder.regrid(extra_dim_grid_input)
    extra_dim_expected_mesh_output = _give_extra_dims(expected_mesh_output)
    assert ma.allclose(extra_dim_expected_mesh_output, extra_dim_mesh_output)
