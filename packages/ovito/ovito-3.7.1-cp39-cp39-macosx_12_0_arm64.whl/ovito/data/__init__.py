"""
This Python module defines various data object types, which are produced and processed within OVITO's data pipeline system.
It also provides the :py:class:`DataCollection` class as a container for such data objects as well as several utility classes for
computing neighbor lists and iterating over the bonds of connected to a particle.

**Data containers:**

  * :py:class:`DataObject` (base class for all data object types)
  * :py:class:`DataCollection` (an entire dataset made of several data objects)
  * :py:class:`PropertyContainer` (base container class storing a set of :py:class:`Property` arrays)
  * :py:class:`Particles` (specialized :py:class:`PropertyContainer` for particles)
  * :py:class:`Bonds` (specialized :py:class:`PropertyContainer` for bonds)
  * :py:class:`VoxelGrid` (specialized :py:class:`PropertyContainer` for 2d and 3d data grids)
  * :py:class:`DataTable` (specialized :py:class:`PropertyContainer` for tabulated data)

**Data objects:**

  * :py:class:`Property` (array of per-data-element property values)
  * :py:class:`SimulationCell` (simulation box geometry and boundary conditions)
  * :py:class:`SurfaceMesh` (polyhedral mesh representation of the boundary surface of a spatial volume)
  * :py:class:`TrajectoryLines` (set of particle trajectory lines)
  * :py:class:`TriangleMesh` (general mesh data structure made of vertices and triangular faces)
  * :py:class:`DislocationNetwork` (set of discrete dislocation lines with Burgers vector information)

**Auxiliary data objects:**

  * :py:class:`ElementType` (base class for element type definitions)
  * :py:class:`ParticleType` (describes a single particle or atom type)
  * :py:class:`BondType` (describes a single bond type)
  * :py:class:`DislocationSegment` (a dislocation line in a :py:class:`DislocationNetwork`)

**Utility classes:**

  * :py:class:`CutoffNeighborFinder` (find neighboring particles within a cutoff distance)
  * :py:class:`NearestNeighborFinder` (find *N* nearest neighbor particles)
  * :py:class:`BondsEnumerator` (efficiently iterate over the bonds connected to a particle)

"""

import numpy as np

# Load the native modules.
from ..plugins.PyScript import DataObject

# Load submodules.
from .data_collection import DataCollection
from .triangle_mesh import TriangleMesh

__all__ = ['DataCollection', 'DataObject', 'TriangleMesh']
