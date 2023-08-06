# Load dependencies
import ovito.vis.stdobj
import ovito.vis.mesh
import ovito.vis.grid
import ovito.vis.stdmod
import ovito.vis.particles

# Load the native code modules.
from ovito.plugins.CrystalAnalysisPython import DislocationVis
import ovito.plugins.PyScript

# Inject selected classes into parent module.
ovito.vis.DislocationVis = DislocationVis
ovito.vis.__all__ += ['DislocationVis']

# Inject enum types.
import types
DislocationVis.Shading = types.SimpleNamespace()
DislocationVis.Shading.Normal = ovito.plugins.PyScript.ArrowShadingMode.Normal
DislocationVis.Shading.Flat = ovito.plugins.PyScript.ArrowShadingMode.Flat
#DislocationVis.Shading = ovito.plugins.PyScript.ArrowShadingMode
