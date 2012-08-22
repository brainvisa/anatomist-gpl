BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/python"
                                 ${PROJECT_NAME} )
BRAINVISA_COPY_DIRECTORY( ${CMAKE_CURRENT_SOURCE_DIR}/tests
                          share/anatomist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}/tests
                          ${PROJECT_NAME} )
BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/doc/examples"
                          "share/doc/pyanatomist-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/examples"
                          ${PROJECT_NAME}-usrdoc )
BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/scripts"
                          "share/anatomist-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/scripts"
                          ${PROJECT_NAME} )
BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/share"
                          "share/anatomist-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}"
                          ${PROJECT_NAME} )
# pyqt translation files
if( anatomist-free_IS_BEING_COMPILED )
  # use source files in anatomist-free/share sources
  BRAINVISA_ADD_PYTRANSLATION( "share"
    "share/anatomist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}"
    ${PROJECT_NAME}
    "${anatomist-free_SOURCE_DIR}/shared/python_plugins" )
else()
  # anatomist already installed, use the binary dir
  BRAINVISA_ADD_PYTRANSLATION( "share"
    "share/anatomist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}"
    ${PROJECT_NAME}
    "${CMAKE_BINARY_DIR}/share/anatomist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}/python_plugins" )
endif()

add_subdirectory( bin )
add_subdirectory( src )

# find_package( Epydoc )
# BRAINVISA_GENERATE_EPYDOC_DOC( "${CMAKE_BINARY_DIR}/python/anatomist"
#      "share/doc/pyanatomist-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/epydoc" )

find_package( Doxygen )
IF ( DOXYGEN_FOUND )
  set( _doxygenInput ${HEADERS} )
  set( DOXYFILE_PREDEFINED "${ANATOMIST_DEFINITIONS}")
  set(aims-free_version "${aims-free_VERSION_MAJOR}.${aims-free_VERSION_MINOR}")
  set(anatomist-free_version "${anatomist-free_VERSION_MAJOR}.${anatomist-free_VERSION_MINOR}")
  set( DOXYFILE_TAGFILES "${CMAKE_BINARY_DIR}/share/doc/anatomist-${anatomist-free_version}/doxygen/anatomist.tag=../../anatomist-${anatomist-free_version}/doxygen  ${CMAKE_BINARY_DIR}/share/doc/aimsgui-${aims-free_version}/doxygen/aimsgui.tag=../../aimsgui-${aims-free_version}/doxygen  ${CMAKE_BINARY_DIR}/share/doc/aimsdata-${aims-free_version}/doxygen/aimsdata.tag=../../aimsdata-${aims-free_version}/doxygen  ${CMAKE_BINARY_DIR}/share/doc/graph-${aims-free_version}/doxygen/graph.tag=../../graph-${aims-free_version}/doxygen  ${CMAKE_BINARY_DIR}/share/doc/cartobase-${aims-free_version}/doxygen/cartobase.tag=../../cartobase-${aims-free_version}/doxygen  ${CMAKE_BINARY_DIR}/share/doc/cartodata-${aims-free_version}/doxygen/cartodata.tag=../../cartodata-${aims-free_version}/doxygen  ${CMAKE_BINARY_DIR}/share/doc/pyaims-${aims-free_version}/doxygen/pyaims.tag=../../pyaims-${aims-free_version}/doxygen" )
  BRAINVISA_GENERATE_DOXYGEN_DOC( _doxygenInput  
                                  INPUT_PREFIX "${CMAKE_BINARY_DIR}/include/pyanatomist"
                                  COMPONENT pyanatomist )
  add_dependencies( pyanatomist-doxygen anatomist-doxygen aimsgui-doxygen aimsdata-doxygen graph-doxygen cartobase-doxygen cartodata-doxygen pyaims-doxygen )
ENDIF ( DOXYGEN_FOUND )

find_package( Sphinx )
BRAINVISA_GENERATE_SPHINX_DOC( "doc/sphinx"
  "share/doc/pyanatomist-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/sphinx" )

