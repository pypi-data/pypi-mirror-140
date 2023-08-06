cmake_minimum_required( VERSION 2.8 )

project(BambooExt LANGUAGES CXX)

include(GNUInstallDirs)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)

if(EXISTS "$ENV{CMAKE_PREFIX_PATH}/include/boost")
    message(STATUS "Will use $ENV{CMAKE_PREFIX_PATH} as base path for boost")
    set(BOOST_ROOT $ENV{CMAKE_PREFIX_PATH})
    set(Boost_NO_BOOST_CMAKE ON)
endif()

find_package(ROOT REQUIRED COMPONENTS MathCore Hist ROOTVecOps Physics)
find_package(Boost REQUIRED)

install(DIRECTORY include/ DESTINATION bamboo/include)

install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../cpp/bamboohelpers.h ${CMAKE_CURRENT_SOURCE_DIR}/../cpp/range.h ${CMAKE_CURRENT_SOURCE_DIR}/../cpp/scalefactors.h ${CMAKE_CURRENT_SOURCE_DIR}/../cpp/printprogress.h DESTINATION bamboo/include)

add_library(BambooRandom SHARED src/bamboorandom.cc)
target_include_directories(BambooRandom PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
target_link_libraries(BambooRandom ROOT::MathCore)
install(TARGETS BambooRandom EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)

add_library(BinnedValues SHARED src/BinnedValues.cc src/BinnedValuesJSONParser.cc src/BTagCalibrationStandalone.cpp)
target_compile_definitions(BinnedValues PRIVATE NO_CHECK_ALL_FORMULAS)
target_include_directories(BinnedValues PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
target_link_libraries(BinnedValues ROOT::Hist Boost::boost)
install(TARGETS BinnedValues EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)

add_library(BambooLumiMask SHARED src/LumiMask.cc)
target_include_directories(BambooLumiMask PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
target_link_libraries(BambooLumiMask Boost::boost)
install(TARGETS BambooLumiMask EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)

add_library(RoccoR SHARED src/RoccoR.cc src/RochesterCorrectionCalculator.cc)
target_include_directories(RoccoR PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
target_link_libraries(RoccoR ROOT::ROOTVecOps Boost::boost BambooRandom)
install(TARGETS RoccoR EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)

## ML extensions

find_package(TensorflowC)
if(TensorflowC_FOUND)
  add_library(BambooTensorflowC SHARED src/bambootensorflowc.cc)
  target_compile_features(BambooTensorflowC PRIVATE cxx_std_17)
  target_include_directories(BambooTensorflowC
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
  target_link_libraries(BambooTensorflowC TensorflowC)
  install(TARGETS BambooTensorflowC EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)
  message(STATUS "Building Tensorflow C API integration (from ${TENSORFLOWC_INCLUDE_DIR})")
else()
  message(STATUS "Tensorflow C API integration will not be built. Specify CMAKE_PREFIX_PATH with the correct prefix to include it")
endif()

find_package(Torch)
if(Torch_FOUND)
  add_library(BambooTorch SHARED src/bambootorch.cc)
  target_compile_features(BambooTorch PRIVATE cxx_std_17)
  target_include_directories(BambooTorch
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
  target_link_libraries(BambooTorch torch)
  install(TARGETS BambooTorch EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)
  message(STATUS "Building libTorch integration with libTorch from ${TORCH_INSTALL_PREFIX}")
else()
  message(STATUS "libTorch integration will not be built. Specify CMAKE_PREFIX_PATH with the libTorch prefix to include it")
endif()

find_package(lwtnn)
if(lwtnn_FOUND)
  add_library(BambooLwtnn SHARED src/bamboolwtnn.cc)
  target_compile_features(BambooLwtnn PRIVATE cxx_std_17)
  target_include_directories(BambooLwtnn
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
  target_link_libraries(BambooLwtnn lwtnn::lwtnn)
  install(TARGETS BambooLwtnn EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)
  message(STATUS "Building lwtnn integration with lwtnn from ${lwtnn_INSTALL_DIR}")
else()
  message(STATUS "lwtnn integration will not be built")
endif()

find_package(ONNXRuntime)
if(ONNXRuntime_FOUND)
  add_library(BambooONNXRuntime SHARED src/bambooonnxruntime.cc)
  target_compile_features(BambooONNXRuntime PRIVATE cxx_std_17)
  target_include_directories(BambooONNXRuntime
    PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:bamboo/include>)
  target_link_libraries(BambooONNXRuntime ONNXRuntime)
  install(TARGETS BambooONNXRuntime EXPORT bamboo-targets LIBRARY DESTINATION bamboo/lib)
  message(STATUS "Building ONNX Runtime integration with ONNX Runtime from ${ONNXRUNTIME_INCLUDE_DIR}")
else()
  message(STATUS "ONNX Runtime integration will not be built")
endif()

install(EXPORT bamboo-targets FILE bamboo-targets.cmake DESTINATION bamboo/cmake)
include(CMakePackageConfigHelpers)
configure_package_config_file(${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/bambooConfig.cmake"
  INSTALL_DESTINATION "bamboo/cmake"
  NO_SET_AND_CHECK_MACRO NO_CHECK_REQUIRED_COMPONENTS_MACRO
  )
write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/bambooConfigVersion.cmake"
  VERSION "${Tutorial_VERSION_MAJOR}.${Tutorial_VERSION_MINOR}"
  COMPATIBILITY AnyNewerVersion
  )
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/bambooConfig.cmake DESTINATION bamboo/cmake)
