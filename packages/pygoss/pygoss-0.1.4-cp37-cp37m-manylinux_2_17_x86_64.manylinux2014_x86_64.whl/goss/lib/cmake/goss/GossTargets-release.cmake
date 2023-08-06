#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Goss::goss" for configuration "Release"
set_property(TARGET Goss::goss APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Goss::goss PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libgoss.so"
  IMPORTED_SONAME_RELEASE "libgoss.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS Goss::goss )
list(APPEND _IMPORT_CHECK_FILES_FOR_Goss::goss "${_IMPORT_PREFIX}/lib/libgoss.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
