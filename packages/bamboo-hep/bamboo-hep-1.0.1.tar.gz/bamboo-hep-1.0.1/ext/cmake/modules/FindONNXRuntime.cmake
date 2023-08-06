# Try to find the Tensorflow C bindings
# This will define
#  ONNXRUNTIME_FOUND
#  ONNXRUNTIME_INCLUDE_DIRS
#  ONNXRUNTIME_LIBRARIES

find_path(ONNXRUNTIME_INCLUDE_DIR onnxruntime_cxx_api.h PATH_SUFFIXES onnxruntime/core/session/ core/session/)
find_library(ONNXRUNTIME_LIBRARY onnxruntime)
set(ONNXRUNTIME_LIBRARIES ${ONNXRUNTIME_LIBRARY})

include(FindPackageHandleStandardArgs)
# handle the QUIETLY and REQUIRED arguments and set ONNXRUNTIME_FOUND to TRUE
# if all listed variables are TRUE
find_package_handle_standard_args(ONNXRuntime DEFAULT_MSG ONNXRUNTIME_LIBRARIES ONNXRUNTIME_INCLUDE_DIR)
mark_as_advanced(ONNXRUNTIME_INCLUDE_DIR ONNXRUNTIME_LIBRARY )

add_library(ONNXRuntime SHARED IMPORTED)
set_property(TARGET ONNXRuntime PROPERTY IMPORTED_LOCATION "${ONNXRUNTIME_LIBRARY}")
set_property(TARGET ONNXRuntime PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${ONNXRUNTIME_INCLUDE_DIR}")
