BRAINVISA_GET_FILE_LIST_FROM_PRO( "${CMAKE_CURRENT_SOURCE_DIR}/pyanatomistmodule.pro" "HEADERS" _headers "SOURCES" _sources )
BRAINVISA_COPY_AND_INSTALL_HEADERS( _headers pyanatomist headersTarget )
set(PYANATOMISTMODULE_HEADERS ${_headers} PARENT_SCOPE)
BRAINVISA_ADD_MOC_FILES( _sources ${_headers} )

add_library( pyanatomistmodule MODULE ${_sources} )

if( APPLE )
  # Setting VERSION or SOVERSION on a MODULE cause a link error on MacOS 10.5 with cmake 2.6:
  #  i686-apple-darwin9-g++-4.0.1: -compatibility_version only allowed with -dynamiclib
  set_property( TARGET pyanatomistmodule PROPERTY OUTPUT_NAME pyanatomistmodule.${${PROJECT_NAME}_VERSION} )
else()
  # in cmake 3.5 on linux, making a "module" removes the version number in the
  # .so so the suffix has to be forced.
  set_target_properties( pyanatomistmodule
    PROPERTIES SOVERSION ${${PROJECT_NAME}_VERSION} SUFFIX ".so.${${PROJECT_NAME}_VERSION}" )
endif()

target_link_libraries( pyanatomistmodule pyanatomistexports "${PYTHON_LIBRARY}" )
BRAINVISA_INSTALL( TARGETS pyanatomistmodule
                   DESTINATION lib
                   COMPONENT ${PROJECT_NAME} )
