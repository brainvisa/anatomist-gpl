
EXEC_PROGRAM(${CMAKE_COMMAND} ARGS -E copy_directory
	${CMAKE_CURRENT_SOURCE_DIR}
	${CMAKE_BINARY_DIR}/scripts)

INSTALL(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/ DESTINATION scripts
        PATTERN "CMakeLists.txt" EXCLUDE
	PATTERN "*.*~"           EXCLUDE)
