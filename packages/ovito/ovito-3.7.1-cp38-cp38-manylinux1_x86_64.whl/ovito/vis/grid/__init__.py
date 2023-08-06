# Load dependencies
import ovito.vis.stdobj
import ovito.vis.stdmod
import ovito.vis.mesh

# Load the native code module.
from ovito.plugins.GridPython import VoxelGridVis

# Inject selected classes into parent module.
ovito.vis.VoxelGridVis = VoxelGridVis
ovito.vis.__all__ += ['VoxelGridVis']