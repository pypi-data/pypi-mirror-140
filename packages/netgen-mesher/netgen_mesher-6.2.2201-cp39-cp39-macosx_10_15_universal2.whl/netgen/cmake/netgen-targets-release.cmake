#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ngcore" for configuration "Release"
set_property(TARGET ngcore APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(ngcore PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libngcore.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libngcore.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS ngcore )
list(APPEND _IMPORT_CHECK_FILES_FOR_ngcore "${_IMPORT_PREFIX}/netgen/libngcore.dylib" )

# Import target "mesh" for configuration "Release"
set_property(TARGET mesh APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mesh PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libmesh.so"
  IMPORTED_SONAME_RELEASE "@rpath/libmesh.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS mesh )
list(APPEND _IMPORT_CHECK_FILES_FOR_mesh "${_IMPORT_PREFIX}/netgen/libmesh.so" )

# Import target "visual" for configuration "Release"
set_property(TARGET visual APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(visual PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libvisual.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libvisual.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS visual )
list(APPEND _IMPORT_CHECK_FILES_FOR_visual "${_IMPORT_PREFIX}/netgen/libvisual.dylib" )

# Import target "csg" for configuration "Release"
set_property(TARGET csg APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(csg PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libcsg.so"
  IMPORTED_SONAME_RELEASE "@rpath/libcsg.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS csg )
list(APPEND _IMPORT_CHECK_FILES_FOR_csg "${_IMPORT_PREFIX}/netgen/libcsg.so" )

# Import target "csgvis" for configuration "Release"
set_property(TARGET csgvis APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(csgvis PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libcsgvis.so"
  IMPORTED_SONAME_RELEASE "@rpath/libcsgvis.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS csgvis )
list(APPEND _IMPORT_CHECK_FILES_FOR_csgvis "${_IMPORT_PREFIX}/netgen/libcsgvis.so" )

# Import target "geom2d" for configuration "Release"
set_property(TARGET geom2d APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(geom2d PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libgeom2d.so"
  IMPORTED_SONAME_RELEASE "@rpath/libgeom2d.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS geom2d )
list(APPEND _IMPORT_CHECK_FILES_FOR_geom2d "${_IMPORT_PREFIX}/netgen/libgeom2d.so" )

# Import target "geom2dvis" for configuration "Release"
set_property(TARGET geom2dvis APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(geom2dvis PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libgeom2dvis.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libgeom2dvis.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS geom2dvis )
list(APPEND _IMPORT_CHECK_FILES_FOR_geom2dvis "${_IMPORT_PREFIX}/netgen/libgeom2dvis.dylib" )

# Import target "occ" for configuration "Release"
set_property(TARGET occ APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(occ PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libocc.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libocc.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS occ )
list(APPEND _IMPORT_CHECK_FILES_FOR_occ "${_IMPORT_PREFIX}/netgen/libocc.dylib" )

# Import target "occvis" for configuration "Release"
set_property(TARGET occvis APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(occvis PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/liboccvis.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/liboccvis.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS occvis )
list(APPEND _IMPORT_CHECK_FILES_FOR_occvis "${_IMPORT_PREFIX}/netgen/liboccvis.dylib" )

# Import target "stl" for configuration "Release"
set_property(TARGET stl APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(stl PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libstl.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libstl.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS stl )
list(APPEND _IMPORT_CHECK_FILES_FOR_stl "${_IMPORT_PREFIX}/netgen/libstl.dylib" )

# Import target "stlvis" for configuration "Release"
set_property(TARGET stlvis APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(stlvis PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libstlvis.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libstlvis.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS stlvis )
list(APPEND _IMPORT_CHECK_FILES_FOR_stlvis "${_IMPORT_PREFIX}/netgen/libstlvis.dylib" )

# Import target "interface" for configuration "Release"
set_property(TARGET interface APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(interface PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libinterface.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libinterface.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS interface )
list(APPEND _IMPORT_CHECK_FILES_FOR_interface "${_IMPORT_PREFIX}/netgen/libinterface.dylib" )

# Import target "gui" for configuration "Release"
set_property(TARGET gui APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(gui PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libgui.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libgui.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS gui )
list(APPEND _IMPORT_CHECK_FILES_FOR_gui "${_IMPORT_PREFIX}/netgen/libgui.dylib" )

# Import target "nglib" for configuration "Release"
set_property(TARGET nglib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(nglib PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/netgen/libnglib.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libnglib.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS nglib )
list(APPEND _IMPORT_CHECK_FILES_FOR_nglib "${_IMPORT_PREFIX}/netgen/libnglib.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
