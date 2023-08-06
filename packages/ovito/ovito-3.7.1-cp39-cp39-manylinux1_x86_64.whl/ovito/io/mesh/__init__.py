# Load dependencies
import ovito.io
import ovito.io.stdobj

# Load the native code module
from ovito.plugins.MeshPython import STLImporter, WavefrontOBJImporter, VTKFileImporter, ParaViewPVDImporter, ParaViewVTMImporter, ParaViewVTPMeshImporter
from ovito.plugins.MeshPython import VTKTriangleMeshExporter

# Register import formats.
ovito.io.import_file._formatTable["stl"] = STLImporter
ovito.io.import_file._formatTable["obj"] = WavefrontOBJImporter
ovito.io.import_file._formatTable["vtk/legacy/mesh"] = VTKFileImporter
ovito.io.import_file._formatTable["vtk/pvd"] = ParaViewPVDImporter
ovito.io.import_file._formatTable["vtk/vtm"] = ParaViewVTMImporter
ovito.io.import_file._formatTable["vtk/vtp/mesh"] = ParaViewVTPMeshImporter

# Register export formats.
ovito.io.export_file._formatTable["vtk/trimesh"] = VTKTriangleMeshExporter
