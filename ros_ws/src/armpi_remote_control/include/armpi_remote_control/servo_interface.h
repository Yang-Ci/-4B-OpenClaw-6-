#ifndef SERVO_INTERFACE_H
#define SERVO_INTERFACE_H

#include <ros/ros.h>
#include <hiwonder_servo_msgs/MultiRawIdPosDur.h>
#include <armpi_remote_control/ServoStateFull.h>
#include <vector>
#include <map>

namespace armpi_remote_control {

class ServoInterface {
public:
    ServoInterface(ros::NodeHandle& nh);
    ~ServoInterface();

    struct ServoState {
        uint8_t id;
        uint16_t position;
        int16_t deviation;
        uint8_t temperature;
        uint16_t voltage;
        uint8_t temp_limit;
        uint16_t angle_limit_min;
        uint16_t angle_limit_max;
        uint16_t voltage_limit_min;
        uint16_t voltage_limit_max;
        uint8_t torque_state;
    };

    bool setServoPosition(uint8_t servo_id, uint16_t position, uint16_t duration_ms);
    bool setMultipleServos(const std::vector<std::pair<uint8_t, uint16_t>>& servos, uint16_t duration_ms);
    bool setServoDeviation(uint8_t servo_id, int16_t deviation);
    bool saveServoDeviation(uint8_t servo_id);
    bool stopServo(uint8_t servo_id);
    bool unloadServo(uint8_t servo_id);

    ServoState getServoState(uint8_t servo_id);
    std::vector<ServoState> getAllServoStates(const std::vector<uint8_t>& servo_ids);

    bool setAngleLimit(uint8_t servo_id, uint16_t min_angle, uint16_t max_angle);
    bool setVoltageLimit(uint8_t servo_id, uint16_t min_voltage, uint16_t max_voltage);
    bool setTempLimit(uint8_t servo_id, uint8_t temp_limit);

private:
    ros::NodeHandle& nh_;
    ros::Publisher servo_pub_;
    
    ros::ServiceClient get_id_client_;
    ros::ServiceClient get_position_client_;
    ros::ServiceClient get_deviation_client_;
    ros::ServiceClient get_temp_client_;
    ros::ServiceClient get_voltage_client_;
    ros::ServiceClient get_angle_limit_client_;
    ros::ServiceClient get_voltage_limit_client_;
    ros::ServiceClient get_temp_limit_client_;
    ros::ServiceClient get_torque_state_client_;

    ros::ServiceClient set_id_client_;
    ros::ServiceClient set_deviation_client_;
    ros::ServiceClient save_deviation_client_;
    ros::ServiceClient set_angle_limit_client_;
    ros::ServiceClient set_voltage_limit_client_;
    ros::ServiceClient set_temp_limit_client_;
    ros::ServiceClient stop_client_;
    ros::ServiceClient unload_client_;

    std::map<uint8_t, ServoState> servo_states_cache_;
    ros::Time last_update_time_;

    bool initializeClients();
    bool callServiceWithRetry(ros::ServiceClient& client, const ros::ServiceEvent& request, 
                              ros::ServiceEvent& response, int max_retries = 3);
};

} 

#endif
