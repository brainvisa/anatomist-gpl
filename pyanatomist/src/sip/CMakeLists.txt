BRAINVISA_GET_FILE_LIST_FROM_PRO( "${CMAKE_CURRENT_SOURCE_DIR}/sip.pro" "HEADERS" _headers "SOURCES" _sources )
BRAINVISA_COPY_AND_INSTALL_HEADERS( _headers pyanatomist headersTarget )
set(SIP_HEADERS ${_headers} PARENT_SCOPE)
file( GLOB _sipTemplates RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/*.tpl" )
BRAINVISA_COPY_FILES( ${PROJECT_NAME}-dev
                      anatypessub.py ${_sipTemplates}
                      SOURCE_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
                      DESTINATION "${ANATOMIST_RELATIVE_SIP_DIRECTORY}"
                      IMMEDIATE )

file( GLOB _sipSources "${CMAKE_CURRENT_SOURCE_DIR}/*.sip" )

file( MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/${ANATOMIST_RELATIVE_SIP_DIRECTORY}" )

if( SIP_MODULE )
  set( extra_defs "-D" "SIP_MODULE=\"${SIP_MODULE}\"" )
endif()
if( SIP_ABI )
  string( REGEX MATCH "[^.]*" SIP_ABI_MAJOR_VERSION "${SIP_ABI}")
  set( extra_defs "${extra_defs}" "-D"
       "SIP_ABI_MAJOR_VERSION=${SIP_ABI_MAJOR_VERSION}")
endif()

exec_program( "${PYTHON_HOST_EXECUTABLE}"
  ARGS "${AIMS-FREE_SIP_DIRECTORY}/maketemplates.py"
        -s "${AIMS-FREE_SIP_DIRECTORY}"
        -i "${CMAKE_CURRENT_SOURCE_DIR}/generatedtypes.py"
        -p "${CMAKE_CURRENT_SOURCE_DIR}"
        -o "${CMAKE_BINARY_DIR}/${ANATOMIST_RELATIVE_SIP_DIRECTORY}"
        -t "${AIMS-FREE_SIP_DIRECTORY}/typessub.py"
        -t "${CMAKE_CURRENT_SOURCE_DIR}/anatypessub.py"
        -l
        -m "${QT_MOC_EXECUTABLE}"
        -P "'${CMAKE_C_PREPROCESSOR}'"
        ${extra_defs}
  OUTPUT_VARIABLE _generatedSipFileList 
  RETURN_VALUE _returnValue )

if( NOT _returnValue EQUAL 0 )
  message( SEND_ERROR "The sip generation from ${PROJECT_NAME} templates with \"${AIMS-FREE_SIP_DIRECTORY}/maketemplates.py\" returned an error:\n${_generatedSipFileList}\n========================")
endif( NOT _returnValue EQUAL 0 )

BRAINVISA_ADD_SIP_PYTHON_MODULE( anatomistsip
  anatomist/cpp 
  "${CMAKE_BINARY_DIR}/${ANATOMIST_RELATIVE_SIP_DIRECTORY}/anatomist_VOID.sip"
  SIP_SOURCES ${_generatedSipFileList} ${_sipSources}
  SIP_INCLUDE "${CMAKE_BINARY_DIR}/${ANATOMIST_RELATIVE_SIP_DIRECTORY}"
    "${AIMS-FREE_SIP_DIRECTORY}" "${PYQT${DESIRED_QT_VERSION}_SIP_DIR}"
  SIP_INSTALL "${ANATOMIST_RELATIVE_SIP_DIRECTORY}" )
add_dependencies( anatomistsip ${headersTarget} )
target_link_libraries( anatomistsip 
  "${PYTHON_LIBRARY}"
  pyanatomistexports
  "${AIMS_PYAIMS_LIBRARY}" )
BRAINVISA_INSTALL( TARGETS anatomistsip 
                   DESTINATION ${PYTHON_INSTALL_DIRECTORY}/anatomist/cpp
                   COMPONENT ${PROJECT_NAME} )
