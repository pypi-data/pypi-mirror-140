# Load dependencies
import ovito.io
import ovito.io.particles

# Load the native code module.
from ovito.plugins.oxDNAPython import OXDNAImporter

# Register import formats.
ovito.io.import_file._formatTable["oxdna"] = OXDNAImporter