cmake_minimum_required(VERSION 2.8.9)

project(SlicerToKiwiExporter)

#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "https://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/SlicerToKiwiExporter")
set(EXTENSION_CATEGORY "Exporter")
set(EXTENSION_CONTRIBUTORS "Jean-Christophe Fillion-Robin (Kitware), Pat Marion (Kitware), Steve Pieper (Isomics), Atsushi Yamada (Shiga University of Medical Science)")
set(EXTENSION_DESCRIPTION "The ${PROJECT_NAME} module provides Slicer user with any easy way to export models into a KiwiViewer scene file.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/jcfr/SlicerToKiwiExporter/master/SlicerToKiwiExporterLogo.png")
set(EXTENSION_SCREENSHOTURLS "https://www.slicer.org/slicerWiki/images/9/9e/SlicerToKiwiExporter_Kiwiviewer_8.PNG https://www.slicer.org/slicerWiki/images/a/ab/SlicerToKiwiExporter_Kiwiviewer_9.PNG https://www.slicer.org/slicerWiki/images/9/9a/SlicerToKiwiExporter_SaveDialog_Select-file-format_1.png")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${PROJECT_NAME}
  SCRIPTS 
    ${PROJECT_NAME}.py
  RESOURCES
    ${PROJECT_NAME}Logo.png
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})

