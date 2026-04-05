cmake_minimum_required(VERSION 3.0.2)
project(armpi_remote_control)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  sensor_msgs
  message_generation
  hiwonder_servo_msgs
)

add_message_files(
  FILES
  ServoControl.msg
  ServoStateFull.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
  sensor_msgs
)

catkin_package(
  CATKIN_DEPENDS
    roscpp
    rospy
    std_msgs
    sensor_msgs
    message_runtime
    hiwonder_servo_msgs
)

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${PROJECT_SOURCE_DIR}/include
)

add_executable(servo_state_publisher src/servo_state_publisher.cpp)
target_link_libraries(servo_state_publisher ${catkin_LIBRARIES})
add_dependencies(servo_state_publisher ${PROJECT_NAME}_generate_messages_cpp)

add_executable(servo_command_receiver src/servo_command_receiver.cpp)
target_link_libraries(servo_command_receiver ${catkin_LIBRARIES})
add_dependencies(servo_command_receiver ${PROJECT_NAME}_generate_messages_cpp)

add_executable(remote_gui_node src/remote_gui_node.cpp)
target_link_libraries(remote_gui_node ${catkin_LIBRARIES})
add_dependencies(remote_gui_node ${PROJECT_NAME}_generate_messages_cpp)
