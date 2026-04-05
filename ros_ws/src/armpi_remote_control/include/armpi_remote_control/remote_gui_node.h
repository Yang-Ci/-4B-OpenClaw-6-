#include <ros/ros.h>
#include <armpi_remote_control/ServoControl.h>
#include <armpi_remote_control/ServoStateFull.h>
#include <sensor_msgs/JointState.h>
#include <vector>
#include <map>
#include <thread>
#include <chrono>
#include <mutex>

namespace armpi_remote_control {

class RemoteGuiNode {
public:
    RemoteGuiNode(ros::NodeHandle& nh);
    ~RemoteGuiNode();

    void start();
    void stop();

    void setServoPosition(uint8_t servo_id, uint16_t position, uint16_t duration_ms = 1000);
    void setMultipleServos(const std::vector<std::pair<uint8_t, uint16_t>>& servos, uint16_t duration_ms = 1000);
    void stopAllServos();
    void resetToHome();

    std::map<uint8_t, uint16_t> getCurrentPositions() const;
    std::map<uint8_t, ServoStateFull> getServoStates() const;

private:
    ros::NodeHandle& nh_;
    ros::Publisher servo_control_pub_;
    ros::Subscriber servo_state_sub_;
    ros::Subscriber joint_state_sub_;

    mutable std::mutex state_mutex_;
    std::map<uint8_t, uint16_t> current_positions_;
    std::map<uint8_t, ServoStateFull> servo_states_;
    std::vector<uint8_t> servo_ids_;

    bool running_;

    void servoStateCallback(const armpi_remote_control::ServoStateFull::ConstPtr& msg);
    void jointStateCallback(const sensor_msgs::JointState::ConstPtr& msg);
    void publishServoControl(const std::vector<uint8_t>& servo_ids,
                               const std::vector<uint16_t>& positions,
                               const std::vector<uint16_t>& durations);
};

} 
