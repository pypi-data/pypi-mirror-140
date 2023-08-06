# Load dependencies
import ovito.io
import ovito.io.stdobj
import ovito.io.mesh
import ovito.io.grid
import ovito.io.stdmod
import ovito.io.particles

# Load the native code modules
from ovito.plugins.CrystalAnalysisPython import CAImporter, ParaDiSImporter, CAExporter, VTKDislocationsExporter

# Register import formats.
ovito.io.import_file._formatTable["ca"] = CAImporter
ovito.io.import_file._formatTable["paradis"] = ParaDiSImporter

# Register export formats.
ovito.io.export_file._formatTable["ca"] = CAExporter
ovito.io.export_file._formatTable["vtk/disloc"] = VTKDislocationsExporter
