# Load dependencies
import ovito.io
import ovito.io.stdobj
import ovito.io.stdmod
import ovito.io.mesh

# Load the native code module
from ovito.plugins.GridPython import ParaViewVTIGridImporter, ParaViewVTSGridImporter, VTKVoxelGridExporter

# Register import formats.
ovito.io.import_file._formatTable["vtk/vti/grid"] = ParaViewVTIGridImporter
ovito.io.import_file._formatTable["vtk/vts/grid"] = ParaViewVTSGridImporter

# Register export formats.
ovito.io.export_file._formatTable["vtk/grid"] = VTKVoxelGridExporter
