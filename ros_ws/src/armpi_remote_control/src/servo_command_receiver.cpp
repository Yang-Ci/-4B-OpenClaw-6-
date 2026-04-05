#include <ros/ros.h>
#include <hiwonder_servo_msgs/MultiRawIdPosDur.h>
#include <hiwonder_servo_msgs/RawIdPosDur.h>
#include <armpi_remote_control/servo_command_receiver.h>

using namespace armpi_remote_control;

ServoCommandReceiver::ServoCommandReceiver(ros::NodeHandle& nh)
    : nh_(nh) {
    
    servo_control_sub_ = nh_.subscribe(
        "/armpi_remote/servo_control", 10,
        &ServoCommandReceiver::servoControlCallback, this);
    
    // 使用正确的舵机控制话题
    servo_pub_ = nh_.advertise<hiwonder_servo_msgs::MultiRawIdPosDur>(
        "/servo_controllers/port_id_1/multi_id_pos_dur", 10);
    
    ROS_INFO("Servo command receiver initialized");
}

ServoCommandReceiver::~ServoCommandReceiver() {
    stop();
}

void ServoCommandReceiver::start() {
    ROS_INFO("Servo command receiver started");
}

void ServoCommandReceiver::stop() {
    ROS_INFO("Servo command receiver stopped");
}

void ServoCommandReceiver::servoControlCallback(const armpi_remote_control::ServoControl::ConstPtr& msg) {
    ROS_INFO("Received servo control command for %zu servos", msg->servo_ids.size());
    
    if (!executeServoCommand(*msg)) {
        ROS_ERROR("Failed to execute servo control command");
    }
}

bool ServoCommandReceiver::executeServoCommand(const armpi_remote_control::ServoControl& msg) {
    if (msg.servo_ids.size() != msg.positions.size() || 
        msg.servo_ids.size() != msg.durations.size()) {
        ROS_ERROR("Servo control message size mismatch");
        return false;
    }
    
    if (msg.servo_ids.empty()) {
        ROS_WARN("Empty servo control message");
        return false;
    }
    
    return setMultipleServos(msg.servo_ids, msg.positions, msg.durations);
}

bool ServoCommandReceiver::setMultipleServos(const std::vector<uint8_t>& servo_ids, 
                                              const std::vector<uint16_t>& positions,
                                              const std::vector<uint16_t>& durations) {
    // 使用正确的MultiRawIdPosDur消息格式
    hiwonder_servo_msgs::MultiRawIdPosDur servo_msg;
    
    // 填充id_pos_dur_list数组
    for (size_t i = 0; i < servo_ids.size(); ++i) {
        hiwonder_servo_msgs::RawIdPosDur raw_msg;
        raw_msg.id = servo_ids[i];
        raw_msg.position = positions[i];
        raw_msg.duration = durations[i] / 1000.0;  // 转换为秒
        servo_msg.id_pos_dur_list.push_back(raw_msg);
    }
    
    // 发布控制命令
    servo_pub_.publish(servo_msg);
    
    ROS_INFO("Published servo control command for %zu servos", servo_ids.size());
    
    for (size_t i = 0; i < servo_ids.size(); ++i) {
        ROS_INFO("Servo %d -> Position %d (%d ms)", 
                 servo_ids[i], positions[i], durations[i]);
    }
    
    return true;
}

int main(int argc, char** argv) {
    ros::init(argc, argv, "servo_command_receiver");
    ros::NodeHandle nh("~");
    
    ServoCommandReceiver receiver(nh);
    receiver.start();
    
    ROS_INFO("Servo Command Receiver Node started");
    
    ros::spin();
    
    receiver.stop();
    return 0;
}
