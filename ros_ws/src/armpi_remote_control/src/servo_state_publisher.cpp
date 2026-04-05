#include <ros/ros.h>
#include <armpi_remote_control/servo_state_publisher.h>
#include <hiwonder_servo_msgs/ServoStateList.h>

using namespace armpi_remote_control;

ServoStatePublisher::ServoStatePublisher(ros::NodeHandle& nh)
    : nh_(nh), update_rate_(10.0), running_(false) {
    
    servo_state_pub_ = nh_.advertise<armpi_remote_control::ServoStateFull>(
        "/armpi_remote/servo_states", 10);
    
    joint_state_pub_ = nh_.advertise<sensor_msgs::JointState>(
        "/joint_states", 10);

    // 订阅实际的舵机状态话题
    actual_servo_state_sub_ = nh_.subscribe(
        "/servo_controllers/port_id_1/servo_states", 10,
        &ServoStatePublisher::actualServoStateCallback, this);

    nh_.param("update_rate", update_rate_, 10.0);
    
    std::vector<int> default_servo_ids = {1, 2, 3, 4, 5, 6};
    std::vector<int> param_servo_ids;
    if (nh_.getParam("servo_ids", param_servo_ids)) {
        for (int id : param_servo_ids) {
            servo_ids_.push_back(static_cast<uint8_t>(id));
        }
    } else {
        for (int id : default_servo_ids) {
            servo_ids_.push_back(static_cast<uint8_t>(id));
        }
    }
}

ServoStatePublisher::~ServoStatePublisher() {
    stop();
}

void ServoStatePublisher::start() {
    if (!running_) {
        running_ = true;
        publisher_thread_ = std::thread(&ServoStatePublisher::publishLoop, this);
        ROS_INFO("Servo state publisher started");
    }
}

void ServoStatePublisher::stop() {
    if (running_) {
        running_ = false;
        if (publisher_thread_.joinable()) {
            publisher_thread_.join();
        }
        ROS_INFO("Servo state publisher stopped");
    }
}

void ServoStatePublisher::setUpdateRate(double rate_hz) {
    update_rate_ = rate_hz;
}

void ServoStatePublisher::setServoIds(const std::vector<uint8_t>& servo_ids) {
    servo_ids_ = servo_ids;
}

void ServoStatePublisher::publishLoop() {
    ros::Rate rate(update_rate_);
    
    while (running_ && ros::ok()) {
        try {
            publishServoStates();
            publishJointStates();
        } catch (const std::exception& e) {
            ROS_ERROR("Error publishing servo states: %s", e.what());
        }
        rate.sleep();
    }
}

void ServoStatePublisher::publishServoStates() {
    for (uint8_t servo_id : servo_ids_) {
        try {
            armpi_remote_control::ServoStateFull msg = createServoStateMessage(servo_id);
            servo_state_pub_.publish(msg);
        } catch (const std::exception& e) {
            ROS_WARN("Failed to read servo %d state: %s", servo_id, e.what());
        }
    }
}

void ServoStatePublisher::publishJointStates() {
    sensor_msgs::JointState joint_msg;
    joint_msg.header.stamp = ros::Time::now();
    
    for (uint8_t servo_id : servo_ids_) {
        std::string joint_name = "servo_" + std::to_string(servo_id);
        joint_msg.name.push_back(joint_name);
        
        try {
            armpi_remote_control::ServoStateFull servo_msg = createServoStateMessage(servo_id);
            double position = static_cast<double>(servo_msg.position) / 1000.0 * 3.14159;
            joint_msg.position.push_back(position);
            joint_msg.velocity.push_back(0.0);
            joint_msg.effort.push_back(0.0);
        } catch (const std::exception& e) {
            joint_msg.position.push_back(0.0);
            joint_msg.velocity.push_back(0.0);
            joint_msg.effort.push_back(0.0);
        }
    }
    
    joint_state_pub_.publish(joint_msg);
}

void ServoStatePublisher::actualServoStateCallback(const hiwonder_servo_msgs::ServoStateList::ConstPtr& msg) {
    std::lock_guard<std::mutex> lock(state_mutex_);
    for (const auto& servo_state : msg->servo_states) {
        actual_servo_states_[static_cast<uint8_t>(servo_state.id)] = servo_state;
    }
}

armpi_remote_control::ServoStateFull ServoStatePublisher::createServoStateMessage(uint8_t servo_id) {
    armpi_remote_control::ServoStateFull msg;
    msg.header.stamp = ros::Time::now();
    msg.header.frame_id = "servo_" + std::to_string(servo_id);
    
    msg.servo_id = servo_id;
    
    // 从实际状态话题获取状态
    std::lock_guard<std::mutex> lock(state_mutex_);
    auto it = actual_servo_states_.find(servo_id);
    if (it != actual_servo_states_.end()) {
        const auto& actual_state = it->second;
        msg.position = actual_state.position;
        msg.deviation = actual_state.error;  // 使用error字段作为deviation
        msg.temperature = 25;  // 状态话题中没有温度信息
        msg.voltage = actual_state.voltage;
        msg.temp_limit = 85;  // 状态话题中没有温度限制信息
        msg.angle_limit_min = 0;  // 状态话题中没有角度限制信息
        msg.angle_limit_max = 1000;  // 状态话题中没有角度限制信息
        msg.voltage_limit_min = 4500;  // 状态话题中没有电压限制信息
        msg.voltage_limit_max = 8000;  // 状态话题中没有电压限制信息
        msg.torque_state = 1;  // 状态话题中没有扭矩状态信息
    } else {
        // 使用默认值
        msg.position = 500;
        msg.deviation = 0;
        msg.temperature = 25;
        msg.voltage = 6000;
        msg.temp_limit = 85;
        msg.angle_limit_min = 0;
        msg.angle_limit_max = 1000;
        msg.voltage_limit_min = 4500;
        msg.voltage_limit_max = 8000;
        msg.torque_state = 1;
    }
    
    return msg;
}

int main(int argc, char** argv) {
    ros::init(argc, argv, "servo_state_publisher");
    ros::NodeHandle nh("~");
    
    ServoStatePublisher publisher(nh);
    publisher.start();
    
    ROS_INFO("Servo State Publisher Node started");
    
    ros::spin();
    
    publisher.stop();
    return 0;
}
