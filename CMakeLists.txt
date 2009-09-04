cmake_minimum_required( VERSION 2.6 )
find_package( brainvisa-cmake REQUIRED )
BRAINVISA_PROJECT()

BRAINVISA_FIND_PACKAGE( aims-gpl REQUIRED )
BRAINVISA_FIND_PACKAGE( anatomist-free REQUIRED )
include( "${AIMS-GPL_USE_FILE}" )
include( "${ANATOMIST-FREE_USE_FILE}" )

find_package( PythonInterp )
if( PYTHONINTERP_FOUND )
  find_package( PythonLibs )
  find_package( SIP )
  find_package( Numpy )
  find_package( PyQt${DESIRED_QT_VERSION} REQUIRED )
endif( PYTHONINTERP_FOUND )

set( ANATOMIST-GPL_INCLUDE_DIRS "${CMAKE_BINARY_DIR}/include" )
if( PYTHONLIBS_FOUND )
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

if( PYTHONLIBS_FOUND AND SIP_FOUND AND NUMPY_FOUND AND PYQT${DESIRED_QT_VERSION}_FOUND )
  set( ANATOMIST_RELATIVE_SIP_DIRECTORY
       "share/sip/${PROJECT_NAME}-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}" )
  if( anatomist-free_FOUND AND aims-gpl_FOUND )
    add_subdirectory( pyanatomist )
  endif()
else()
  message( "WARNING: Not building pyanatomist due to missing dependency:\n  PYTHONLIBS_FOUND=${PYTHONLIBS_FOUND}\nSIP_FOUND=${SIP_FOUND}\nNUMPY_FOUND=${NUMPY_FOUND}\nPYQT${DESIRED_QT_VERSION}_FOUND=${PYQT${DESIRED_QT_VERSION}_FOUND}\n" )
endif()
