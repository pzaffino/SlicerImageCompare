cmake_minimum_required(VERSION 3.13.4)

project(SyntheticCTEvaluation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/SyntheticCTEvaluation")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Paolo Zaffino (Magna Graecia University of Catanzaro, Italy), Maria Francesca Spadea (Magna Graecia University of Catanzaro, Italy)")
set(EXTENSION_DESCRIPTION "This extenson quantifies the similarity between synthetic CT and the ground truth one")
set(EXTENSION_ICONURL "https://github.com/pzaffino/SlicerSyntheticCTEvaluation/blob/master/SyntheticCTEvaluation.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/pzaffino/SlicerSyntheticCTEvaluation/blob/master/SyntheticCTEvaluation_screenshot.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SyntheticCTEvaluation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
