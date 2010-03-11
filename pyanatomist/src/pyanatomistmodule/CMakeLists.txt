BRAINVISA_GET_FILE_LIST_FROM_PRO( "${CMAKE_CURRENT_SOURCE_DIR}/pyanatomistmodule.pro" "HEADERS" _headers "SOURCES" _sources )
BRAINVISA_COPY_AND_INSTALL_HEADERS( _headers pyanatomist headersTarget )
BRAINVISA_ADD_MOC_FILES( _sources ${_headers} )

add_library( pyanatomistmodule MODULE ${_sources} )
set_property( TARGET pyanatomistmodule PROPERTY VERSION ${${PROJECT_NAME}_VERSION} )
target_link_libraries( pyanatomistmodule pyanatomistexports "${PYTHON_LIBRARY}" )
BRAINVISA_INSTALL( TARGETS pyanatomistmodule
                   DESTINATION lib
                   COMPONENT ${PROJECT_NAME} )
