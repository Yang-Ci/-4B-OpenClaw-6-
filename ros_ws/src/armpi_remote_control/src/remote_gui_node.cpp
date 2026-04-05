#include <ros/ros.h>
#include <armpi_remote_control/remote_gui_node.h>
#include <iostream>
#include <iomanip>

using namespace armpi_remote_control;

RemoteGuiNode::RemoteGuiNode(ros::NodeHandle& nh)
    : nh_(nh), running_(false) {
    
    servo_control_pub_ = nh_.advertise<armpi_remote_control::ServoControl>(
        "/armpi_remote/servo_control", 10);
    
    servo_state_sub_ = nh_.subscribe(
        "/armpi_remote/servo_states", 10,
        &RemoteGuiNode::servoStateCallback, this);
    
    joint_state_sub_ = nh_.subscribe(
        "/joint_states", 10,
        &RemoteGuiNode::jointStateCallback, this);

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

    for (uint8_t id : servo_ids_) {
        current_positions_[id] = 500;
    }
    
    ROS_INFO("Remote GUI Node initialized with %zu servos", servo_ids_.size());
}

RemoteGuiNode::~RemoteGuiNode() {
    stop();
}

void RemoteGuiNode::start() {
    if (!running_) {
        running_ = true;
        ROS_INFO("Remote GUI Node started");
    }
}

void RemoteGuiNode::stop() {
    if (running_) {
        running_ = false;
        ROS_INFO("Remote GUI Node stopped");
    }
}

void RemoteGuiNode::setServoPosition(uint8_t servo_id, uint16_t position, uint16_t duration_ms) {
    std::vector<uint8_t> servo_ids = {servo_id};
    std::vector<uint16_t> positions = {position};
    std::vector<uint16_t> durations = {duration_ms};
    
    publishServoControl(servo_ids, positions, durations);
}

void RemoteGuiNode::setMultipleServos(const std::vector<std::pair<uint8_t, uint16_t>>& servos, 
                                        uint16_t duration_ms) {
    std::vector<uint8_t> servo_ids;
    std::vector<uint16_t> positions;
    std::vector<uint16_t> durations;
    
    for (const auto& servo : servos) {
        servo_ids.push_back(servo.first);
        positions.push_back(servo.second);
        durations.push_back(duration_ms);
    }
    
    publishServoControl(servo_ids, positions, durations);
}

void RemoteGuiNode::stopAllServos() {
    ROS_INFO("Stopping all servos");
    armpi_remote_control::ServoControl msg;
    msg.header.stamp = ros::Time::now();
    msg.save_deviation = false;
    servo_control_pub_.publish(msg);
}

void RemoteGuiNode::resetToHome() {
    ROS_INFO("Resetting to home position");
    std::vector<std::pair<uint8_t, uint16_t>> home_positions;
    
    for (uint8_t id : servo_ids_) {
        home_positions.push_back({id, 500});
    }
    
    setMultipleServos(home_positions, 1500);
}

std::map<uint8_t, uint16_t> RemoteGuiNode::getCurrentPositions() const {
    std::lock_guard<std::mutex> lock(state_mutex_);
    return current_positions_;
}

std::map<uint8_t, ServoStateFull> RemoteGuiNode::getServoStates() const {
    std::lock_guard<std::mutex> lock(state_mutex_);
    return servo_states_;
}

void RemoteGuiNode::servoStateCallback(const armpi_remote_control::ServoStateFull::ConstPtr& msg) {
    std::lock_guard<std::mutex> lock(state_mutex_);
    current_positions_[msg->servo_id] = msg->position;
    servo_states_[msg->servo_id] = *msg;
}

void RemoteGuiNode::jointStateCallback(const sensor_msgs::JointState::ConstPtr& msg) {
    std::lock_guard<std::mutex> lock(state_mutex_);
    
    for (size_t i = 0; i < msg->name.size(); ++i) {
        std::string joint_name = msg->name[i];
        if (joint_name.find("servo_") == 0) {
            uint8_t servo_id = std::stoi(joint_name.substr(6));
            double position_rad = msg->position[i];
            uint16_t position = static_cast<uint16_t>(position_rad / 3.14159 * 1000.0);
            current_positions_[servo_id] = position;
        }
    }
}

void RemoteGuiNode::publishServoControl(const std::vector<uint8_t>& servo_ids,
                                          const std::vector<uint16_t>& positions,
                                          const std::vector<uint16_t>& durations) {
    armpi_remote_control::ServoControl msg;
    msg.header.stamp = ros::Time::now();
    msg.servo_ids = servo_ids;
    msg.positions = positions;
    msg.durations = durations;
    msg.save_deviation = false;
    
    servo_control_pub_.publish(msg);
    
    for (size_t i = 0; i < servo_ids.size(); ++i) {
        ROS_INFO("Control command: Servo %d -> Position %d (%d ms)", 
                 servo_ids[i], positions[i], durations[i]);
    }
}

void printServoStatus(const RemoteGuiNode& gui_node) {
    auto positions = gui_node.getCurrentPositions();
    auto states = gui_node.getServoStates();
    
    std::cout << "\n=== Servo Status ===" << std::endl;
    std::cout << std::setw(8) << "ID" 
              << std::setw(12) << "Position" 
              << std::setw(10) << "Temp(C)" 
              << std::setw(10) << "Voltage(V)" << std::endl;
    std::cout << std::string(40, '-') << std::endl;
    
    for (const auto& pos : positions) {
        uint8_t id = pos.first;
        uint16_t position = pos.second;
        
        std::cout << std::setw(8) << static_cast<int>(id)
                  << std::setw(12) << position;
        
        auto it = states.find(id);
        if (it != states.end()) {
            const auto& state = it->second;
            std::cout << std::setw(10) << static_cast<int>(state.temperature)
                      << std::setw(10) << std::fixed << std::setprecision(1) 
                      << (state.voltage / 1000.0);
        } else {
            std::cout << std::setw(10) << "N/A"
                      << std::setw(10) << "N/A";
        }
        std::cout << std::endl;
    }
    std::cout << std::string(40, '=') << std::endl;
}

void printMenu() {
    std::cout << "\n=== Remote Control Menu ===" << std::endl;
    std::cout << "1. Set single servo position" << std::endl;
    std::cout << "2. Set multiple servo positions" << std::endl;
    std::cout << "3. Stop all servos" << std::endl;
    std::cout << "4. Reset to home position" << std::endl;
    std::cout << "5. Show servo status" << std::endl;
    std::cout << "6. Exit" << std::endl;
    std::cout << "=========================" << std::endl;
    std::cout << "Select option: ";
}

int main(int argc, char** argv) {
    ros::init(argc, argv, "remote_gui_node");
    ros::NodeHandle nh("~");
    
    RemoteGuiNode gui_node(nh);
    gui_node.start();
    
    ROS_INFO("Remote GUI Node started");
    
    std::thread spinner([]() {
        ros::spin();
    });
    
    int choice;
    while (ros::ok()) {
        printMenu();
        std::cin >> choice;
        
        switch (choice) {
            case 1: {
                int servo_id_int;
                uint16_t position;
                uint16_t duration;
                
                std::cout << "Enter servo ID (1-6): ";
                std::cin >> servo_id_int;
                
                // 验证ID范围
                if (servo_id_int < 1 || servo_id_int > 6) {
                    std::cout << "Invalid servo ID. Please enter 1-6." << std::endl;
                    break;
                }
                
                uint8_t servo_id = static_cast<uint8_t>(servo_id_int);
                
                std::cout << "Enter position (0-1000): ";
                std::cin >> position;
                std::cout << "Enter duration (ms): ";
                std::cin >> duration;
                
                gui_node.setServoPosition(servo_id, position, duration);
                break;
            }
            case 2: {
                int num_servos;
                std::cout << "Enter number of servos: ";
                std::cin >> num_servos;
                
                std::vector<std::pair<uint8_t, uint16_t>> servos;
                for (int i = 0; i < num_servos; ++i) {
                    int id_int;
                    uint16_t pos;
                    std::cout << "Servo " << (i+1) << " ID: ";
                    std::cin >> id_int;
                    
                    // 验证ID范围
                    if (id_int < 1 || id_int > 6) {
                        std::cout << "Invalid servo ID. Please enter 1-6." << std::endl;
                        break;
                    }
                    
                    uint8_t id = static_cast<uint8_t>(id_int);
                    
                    std::cout << "Servo " << (i+1) << " Position: ";
                    std::cin >> pos;
                    servos.push_back({id, pos});
                }
                
                uint16_t duration;
                std::cout << "Enter duration (ms): ";
                std::cin >> duration;
                
                gui_node.setMultipleServos(servos, duration);
                break;
            }
            case 3:
                gui_node.stopAllServos();
                break;
            case 4:
                gui_node.resetToHome();
                break;
            case 5:
                printServoStatus(gui_node);
                break;
            case 6:
                gui_node.stop();
                ros::shutdown();
                break;
            default:
                std::cout << "Invalid option" << std::endl;
        }
        
        if (choice == 6) {
            break;
        }
    }
    
    if (spinner.joinable()) {
        spinner.join();
    }
    
    return 0;
}
