cmake_minimum_required( VERSION 2.8 )

project(BambooExecutor LANGUAGES CXX)

if(EXISTS "$ENV{CMAKE_PREFIX_PATH}/include/boost")
    message(STATUS "Will use $ENV{CMAKE_PREFIX_PATH} as base path for boost")
    set(BOOST_ROOT $ENV{CMAKE_PREFIX_PATH})
    set(Boost_NO_BOOST_CMAKE ON)
endif()

find_package(Filesystem REQUIRED)
find_package(ROOT REQUIRED COMPONENTS ROOTDataFrame GenVector)
find_package(Boost REQUIRED COMPONENTS program_options)
# BAMBOO_INSERT findpackages
find_package(bamboo REQUIRED COMPONENTS
  # BAMBOO_INSERT bamboocomponents
  )

add_executable(bambooExecutor main.cc)
# BAMBOO_INSERT includedirs
# BAMBOO_INSERT linkdirs
target_link_libraries(bambooExecutor Boost::program_options std::filesystem
  # BAMBOO_INSERT libdependencies
  )
