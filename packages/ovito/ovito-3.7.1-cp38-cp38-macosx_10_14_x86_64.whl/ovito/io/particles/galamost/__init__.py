# Load dependencies
import ovito.io
import ovito.io.particles

# Load the native code module.
from ovito.plugins.GalamostPython import GALAMOSTImporter

# Register import formats.
ovito.io.import_file._formatTable["galamost"] = GALAMOSTImporter
