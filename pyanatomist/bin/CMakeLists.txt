
# Add python commands as executables
file( GLOB _commands "${CMAKE_CURRENT_SOURCE_DIR}/*.py" )
foreach(_command ${_commands})
  get_filename_component( _command_path "${_command}" ABSOLUTE)
  get_filename_component( _command_name "${_command}" NAME)
  # message("Add pyanatomist command ${_command_name}, _command_path ${_command_path}")
  BRAINVISA_ADD_EXECUTABLE( ${_command_name} "${_command_path}" IS_SCRIPT )
endforeach()

get_filename_component( _command_path "${CMAKE_CURRENT_SOURCE_DIR}/anatomist" ABSOLUTE)
BRAINVISA_ADD_EXECUTABLE( anatomist-py "${_command_path}" IS_SCRIPT OUTPUT_NAME anatomist )

unset(_commands)
unset(_command_path)
unset(_command_name)

