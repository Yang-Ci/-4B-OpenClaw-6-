#include <ros/ros.h>
#include <sensor_msgs/JointState.h>
#include <armpi_remote_control/ServoStateFull.h>
#include <hiwonder_servo_msgs/ServoStateList.h>
#include <vector>
#include <map>
#include <thread>
#include <chrono>
#include <mutex>

namespace armpi_remote_control {

class ServoStatePublisher {
public:
    ServoStatePublisher(ros::NodeHandle& nh);
    ~ServoStatePublisher();

    void start();
    void stop();
    void setUpdateRate(double rate_hz);
    void setServoIds(const std::vector<uint8_t>& servo_ids);

private:
    ros::NodeHandle& nh_;
    ros::Publisher servo_state_pub_;
    ros::Publisher joint_state_pub_;
    ros::Subscriber actual_servo_state_sub_;

    std::vector<uint8_t> servo_ids_;
    double update_rate_;
    bool running_;
    std::thread publisher_thread_;
    std::map<uint8_t, hiwonder_servo_msgs::ServoState> actual_servo_states_;
    std::mutex state_mutex_;

    void publishLoop();
    void publishServoStates();
    void publishJointStates();
    ServoStateFull createServoStateMessage(uint8_t servo_id);
    void actualServoStateCallback(const hiwonder_servo_msgs::ServoStateList::ConstPtr& msg);
};

} 
