#include <ros/ros.h>
#include <armpi_remote_control/ServoControl.h>
#include <hiwonder_servo_msgs/MultiRawIdPosDur.h>
#include <hiwonder_servo_msgs/RawIdPosDur.h>
#include <vector>

namespace armpi_remote_control {

class ServoCommandReceiver {
public:
    ServoCommandReceiver(ros::NodeHandle& nh);
    ~ServoCommandReceiver();

    void start();
    void stop();

private:
    ros::NodeHandle& nh_;
    ros::Subscriber servo_control_sub_;
    ros::Publisher servo_pub_;

    void servoControlCallback(const armpi_remote_control::ServoControl::ConstPtr& msg);
    bool executeServoCommand(const armpi_remote_control::ServoControl& msg);
    bool setMultipleServos(const std::vector<uint8_t>& servo_ids, 
                           const std::vector<uint16_t>& positions,
                           const std::vector<uint16_t>& durations);
};

} 
