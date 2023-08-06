# Load dependencies
import ovito.modifiers.stdobj
import ovito.modifiers.mesh
import ovito.modifiers.grid
import ovito.modifiers.stdmod
import ovito.modifiers.particles

# Load the native code modules.
from ovito.plugins.CrystalAnalysisPython import DislocationAnalysisModifier, ElasticStrainModifier, GrainSegmentationModifier

# Inject modifier classes into parent module.
ovito.modifiers.DislocationAnalysisModifier = DislocationAnalysisModifier
ovito.modifiers.ElasticStrainModifier = ElasticStrainModifier
ovito.modifiers.GrainSegmentationModifier = GrainSegmentationModifier
ovito.modifiers.__all__ += ['DislocationAnalysisModifier', 'ElasticStrainModifier', 'GrainSegmentationModifier']

# Copy enum lists.
import types
ElasticStrainModifier.Lattice = types.SimpleNamespace()
ElasticStrainModifier.Lattice.Other = DislocationAnalysisModifier.Lattice.Other
ElasticStrainModifier.Lattice.FCC = DislocationAnalysisModifier.Lattice.FCC
ElasticStrainModifier.Lattice.HCP = DislocationAnalysisModifier.Lattice.HCP
ElasticStrainModifier.Lattice.BCC = DislocationAnalysisModifier.Lattice.BCC
ElasticStrainModifier.Lattice.CubicDiamond = DislocationAnalysisModifier.Lattice.CubicDiamond
ElasticStrainModifier.Lattice.HexagonalDiamond = DislocationAnalysisModifier.Lattice.HexagonalDiamond

GrainSegmentationModifier.Type = types.SimpleNamespace()
GrainSegmentationModifier.Type.OTHER = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.OTHER
GrainSegmentationModifier.Type.FCC = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.FCC
GrainSegmentationModifier.Type.HCP = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.HCP
GrainSegmentationModifier.Type.BCC = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.BCC
GrainSegmentationModifier.Type.ICO = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.ICO
GrainSegmentationModifier.Type.SC = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.SC
GrainSegmentationModifier.Type.CUBIC_DIAMOND = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.CUBIC_DIAMOND
GrainSegmentationModifier.Type.HEX_DIAMOND = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.HEX_DIAMOND
GrainSegmentationModifier.Type.GRAPHENE = ovito.modifiers.PolyhedralTemplateMatchingModifier.Type.GRAPHENE
