cmake_minimum_required( VERSION 2.6 )
find_package( brainvisa-cmake REQUIRED )
BRAINVISA_PROJECT()

BRAINVISA_FIND_PACKAGE( aims-gpl REQUIRED )
BRAINVISA_FIND_PACKAGE( anatomist-free REQUIRED )

BRAINVISA_DEPENDENCY( DEV DEPENDS "${BRAINVISA_PACKAGE_NAME}" RUN "= ${${BRAINVISA_PACKAGE_NAME}_VERSION}" )

BRAINVISA_DEPENDENCY( RUN DEPENDS anatomist-free RUN "= ${anatomist-free_VERSION}" )
BRAINVISA_DEPENDENCY( DEV DEPENDS anatomist-free DEV )

include( "${AIMS-GPL_USE_FILE}" )
include( "${ANATOMIST-FREE_USE_FILE}" )

if( NOT anatomist-free_VERSION_MAJOR EQUAL ${${PROJECT_NAME}_VERSION_MAJOR}
   AND NOT anatomist-free_VERSION_MINOR EQUAL ${${PROJECT_NAME}_VERSION_MINOR} )
  message( "WARNING: anatomist-gpl has version ${${PROJECT_NAME}_VERSION} whereas anatomist-free has version ${anatomist-free_VERSION}. This can be a problem at runtime because shared files are all supposed to be in a directory called anatomist-${anatomist-free_VERSION_MAJOR}.${anatomist-free_VERSION_MINOR}." )
endif()
find_package( python )
if( PYTHON_FOUND )
  find_package( SIP )
  find_package( Numpy )
  find_package( PyQt${DESIRED_QT_VERSION} REQUIRED )
endif()

set( ANATOMIST-GPL_INCLUDE_DIRS "${CMAKE_BINARY_DIR}/include" )
if( PYTHON_INCLUDE_PATH )
  set( ANATOMIST-GPL_INCLUDE_DIRS ${ANATOMIST-GPL_INCLUDE_DIRS}
       "${PYTHON_INCLUDE_PATH}" )
endif()
if( NUMPY_FOUND )
  set( ANATOMIST-GPL_INCLUDE_DIRS ${ANATOMIST-GPL_INCLUDE_DIRS}
       "${NUMPY_INCLUDE_DIR}" )
endif()
if( SIP_FOUND )
  set( ANATOMIST-GPL_INCLUDE_DIRS ${ANATOMIST-GPL_INCLUDE_DIRS}
       "${SIP_INCLUDE_DIR}" )
endif()
include_directories( ${ANATOMIST-GPL_INCLUDE_DIRS} )

configure_file( "${CMAKE_CURRENT_SOURCE_DIR}/config/info.py.in" "${CMAKE_BINARY_DIR}/python/anatomist/info.py" @ONLY )
BRAINVISA_INSTALL( FILES "${CMAKE_BINARY_DIR}/python/anatomist/info.py"
                   DESTINATION "python/anatomist"
                   COMPONENT ${PROJECT_NAME} )

if( PYTHON_FOUND AND SIP_FOUND AND NUMPY_FOUND AND PYQT${DESIRED_QT_VERSION}_FOUND )
  if( DESIRED_QT_VERSION EQUAL 4 )
    foreach( component python python-numpy python-qt4 python-sip4 )
      BRAINVISA_DEPENDENCY( RUN DEPENDS ${component} RUN )
      BRAINVISA_DEPENDENCY( DEV DEPENDS ${component} DEV )
    endforeach()
  elseif( DESIRED_QT_VERSION EQUAL 5 )
    # TODO
  endif()
  BRAINVISA_DEPENDENCY( RUN RECOMMANDS "python-matplotlib" RUN )
  set( ANATOMIST_RELATIVE_SIP_DIRECTORY
       "share/anatomist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}/sip" )
  if( anatomist-free_FOUND AND aims-gpl_FOUND )
    add_subdirectory( pyanatomist )
  endif()
else()
  message( "WARNING: Not building pyanatomist due to missing dependency:\n  PYTHON_FOUND=${PYTHON_FOUND}\nSIP_FOUND=${SIP_FOUND}\nNUMPY_FOUND=${NUMPY_FOUND}\nPYQT${DESIRED_QT_VERSION}_FOUND=${PYQT${DESIRED_QT_VERSION}_FOUND}\n" )
endif()

BRAINVISA_CREATE_CMAKE_CONFIG_FILES()
