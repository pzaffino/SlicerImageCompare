cmake_minimum_required(VERSION 3.13.4)

project(SyntheticCT_evaluation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/SyntheticCT_evaluation")
set(EXTENSION_CATEGORY "Synthetic CT evaluation")
set(EXTENSION_CONTRIBUTORS "Paolo Zaffino (Magna Graecia University of Catanzaro, Italy), Maria Francesca Spadea (Magna Graecia University of Catanzaro, Italy)")
set(EXTENSION_DESCRIPTION "This extenson quantifies the similarity between synthetic CT and the true one")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SyntheticCT_evaluation.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SyntheticCT_evaluation/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SyntheticCT_evaluation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
