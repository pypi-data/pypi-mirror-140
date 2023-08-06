#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "wrapper" for configuration "Release"
set_property(TARGET wrapper APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(wrapper PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "Python::Python"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lapkt/core/lib/wrapper.cpython-39-x86_64-linux-gnu.so"
  IMPORTED_SONAME_RELEASE "wrapper.cpython-39-x86_64-linux-gnu.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS wrapper )
list(APPEND _IMPORT_CHECK_FILES_FOR_wrapper "${_IMPORT_PREFIX}/lapkt/core/lib/wrapper.cpython-39-x86_64-linux-gnu.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
