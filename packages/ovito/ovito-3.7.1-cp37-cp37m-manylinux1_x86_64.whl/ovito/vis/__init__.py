"""
This module contains classes related to :ref:`data visualization and rendering <rendering_intro>`.

**Rendering:**

  * :py:class:`Viewport`

**Rendering engines:**

  * :py:class:`OpenGLRenderer`
  * :py:class:`TachyonRenderer`
  * :py:class:`OSPRayRenderer`

**Data visualization elements:**

  * :py:class:`DataVis` (base class for all visual elements)
  * :py:class:`BondsVis`
  * :py:class:`DislocationVis`
  * :py:class:`ParticlesVis`
  * :py:class:`SimulationCellVis`
  * :py:class:`SurfaceMeshVis`
  * :py:class:`TrajectoryVis`
  * :py:class:`TriangleMeshVis`
  * :py:class:`VectorVis`
  * :py:class:`VoxelGridVis`

**Viewport overlays:**

  * :py:class:`ViewportOverlay` (base class for all overlay types)
  * :py:class:`ColorLegendOverlay`
  * :py:class:`CoordinateTripodOverlay`
  * :py:class:`PythonViewportOverlay`
  * :py:class:`TextLabelOverlay`

"""

# Load the native modules.
from ..plugins.PyScript import (RenderSettings, ViewportConfiguration, OpenGLRenderer,
                                CoordinateTripodOverlay, PythonViewportOverlay, TextLabelOverlay,
                                FrameBuffer, ViewportOverlay, TriangleMeshVis)

# Load submodules.
from .data_vis import DataVis
from .viewport import Viewport

import ovito

__all__ = ['RenderSettings', 'Viewport', 'ViewportConfiguration', 'OpenGLRenderer', 'DataVis',
        'CoordinateTripodOverlay', 'PythonViewportOverlay', 'TextLabelOverlay', 'ViewportOverlay',
        'TriangleMeshVis']

# Here only for backward compatibility with OVITO 2.9.0:
def _get_RenderSettings_custom_range(self):
    """
    Specifies the range of animation frames to render if :py:attr:`range` is set to ``CustomInterval``.

    :Default: ``(0,100)``
    """
    return (self.custom_range_start, self.custom_range_end)
def _set_RenderSettings_custom_range(self, range):
    if len(range) != 2: raise TypeError("Tuple or list of length two expected.")
    self.custom_range_start = range[0]
    self.custom_range_end = range[1]
RenderSettings.custom_range = property(_get_RenderSettings_custom_range, _set_RenderSettings_custom_range)

# Here only for backward compatibility with OVITO 2.9.0:
def _get_RenderSettings_size(self):
    """
    The size of the image or movie to be generated in pixels.

    :Default: ``(640,480)``
    """
    return (self.output_image_width, self.output_image_height)
def _set_RenderSettings_size(self, size):
    if len(size) != 2: raise TypeError("Tuple or list of length two expected.")
    self.output_image_width = size[0]
    self.output_image_height = size[1]
RenderSettings.size = property(_get_RenderSettings_size, _set_RenderSettings_size)

# Here only for backward compatibility with OVITO 2.9.0:
def _get_RenderSettings_filename(self):
    """
    A string specifying the file path under which the rendered image or movie should be saved.

    :Default: ``None``
    """
    if self.save_to_file and self.output_filename: return self.output_filename
    else: return None
def _set_RenderSettings_filename(self, filename):
    if filename:
        self.output_filename = filename
        self.save_to_file = True
    else:
        self.save_to_file = False
RenderSettings.filename = property(_get_RenderSettings_filename, _set_RenderSettings_filename)

# Implement FrameBuffer.image property (requires conversion to a Shiboken object).
def _get_FrameBuffer_image(self):
    from ovito.qt_compat import shiboken
    from ovito.qt_compat import QtGui
    return QtGui.QImage(shiboken.wrapInstance(self._image, QtGui.QImage))
FrameBuffer.image = property(_get_FrameBuffer_image)

# Here only for backward compatibility with OVITO 2.9.0:
def _ViewportConfiguration__len__(self):
    return len(self.viewports)
ViewportConfiguration.__len__ = _ViewportConfiguration__len__

# Here only for backward compatibility with OVITO 2.9.0:
def _ViewportConfiguration__iter__(self):
    return self.viewports.__iter__()
ViewportConfiguration.__iter__ = _ViewportConfiguration__iter__

# Here only for backward compatibility with OVITO 2.9.0:
def _ViewportConfiguration__getitem__(self, index):
    return self.viewports[index]
ViewportConfiguration.__getitem__ = _ViewportConfiguration__getitem__
