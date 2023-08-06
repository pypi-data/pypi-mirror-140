#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "wrapper" for configuration "Release"
set_property(TARGET wrapper APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(wrapper PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lapkt/core/lib/libwrapper.dll.a"
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "Python::Python"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lapkt/core/lib/wrapper.cp39-win_amd64.pyd"
  )

list(APPEND _IMPORT_CHECK_TARGETS wrapper )
list(APPEND _IMPORT_CHECK_FILES_FOR_wrapper "${_IMPORT_PREFIX}/lapkt/core/lib/libwrapper.dll.a" "${_IMPORT_PREFIX}/lapkt/core/lib/wrapper.cp39-win_amd64.pyd" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
