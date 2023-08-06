# Load dependencies
import ovito.io
import ovito.io.particles

# Load the native code module.
from ovito.plugins.NetCDFPluginPython import AMBERNetCDFImporter, AMBERNetCDFExporter

# Register import formats.
ovito.io.import_file._formatTable["netcdf/amber"] = AMBERNetCDFImporter

# Register export formats.
ovito.io.export_file._formatTable["netcdf/amber"] = AMBERNetCDFExporter
