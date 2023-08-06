#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "core" for configuration "Release"
set_property(TARGET core APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(core PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lapkt/core/lib/libcore.dll.a"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lapkt/core/lib/libcore.dll"
  )

list(APPEND _IMPORT_CHECK_TARGETS core )
list(APPEND _IMPORT_CHECK_FILES_FOR_core "${_IMPORT_PREFIX}/lapkt/core/lib/libcore.dll.a" "${_IMPORT_PREFIX}/lapkt/core/lib/libcore.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
