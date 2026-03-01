cmake_minimum_required(VERSION 3.10)
project(uav_planner)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 查找 ROS2 和其他依赖包
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(std_msgs REQUIRED)

# 查找其他依赖（如你需要）
find_package(Eigen3 REQUIRED)
find_package(GDAL REQUIRED)
find_package(octomap REQUIRED)
find_package(fcl REQUIRED)
find_package(OsqpEigen REQUIRED)
find_library(CCD_LIBRARY ccd REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development NumPy)
find_library(FFTW_LIBRARY fftw3 REQUIRED)

find_path(TBB_INCLUDE_DIR tbb/tbb.h)
find_library(TBB_LIBRARY tbb)

# 头文件目录
include_directories(
  include
  third_party/quickhull
  ${EIGEN3_INCLUDE_DIR}
  ${GDAL_INCLUDE_DIR}
  ${OCTOMAP_INCLUDE_DIRS}
  ${FCL_INCLUDE_DIR}
  ${TBB_INCLUDE_DIR}
  ${Python3_INCLUDE_DIRS}
  ${Python3_NumPy_INCLUDE_DIRS}
)

# 收集所有源文件
file(GLOB SOURCES "src/*.cpp")

set(QUICKHULL_SRC ${PROJECT_SOURCE_DIR}/third_party/quickhull/QuickHull.cpp)

# 添加可执行文件
add_executable(main_exec ${SOURCES} ${QUICKHULL_SRC})

# 链接库
target_link_libraries(main_exec
  ${GDAL_LIBRARY}
  ${OCTOMAP_LIBRARIES}
  ${CCD_LIBRARY}
  ${TBB_LIBRARY}
  ${Python3_LIBRARIES} 
  OsqpEigen::OsqpEigen
  fcl 
  ${FFTW_LIBRARY}
)

# 添加 ROS 依赖
ament_target_dependencies(main_exec
  rclcpp
  nav_msgs
  geometry_msgs
  visualization_msgs
  std_msgs
)

# 安装目标
install(TARGETS main_exec
  DESTINATION lib/${PROJECT_NAME}
)

# 安装头文件（如需要）
install(DIRECTORY include/
  DESTINATION include/
)

ament_package()