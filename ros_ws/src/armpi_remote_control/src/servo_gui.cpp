#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include <QSlider>
#include <QLabel>
#include <QGroupBox>
#include <QStatusBar>
#include <QTimer>
#include <ros/ros.h>
#include <armpi_remote_control/ServoControl.h>
#include <armpi_remote_control/ServoStateFull.h>

class ServoGUI : public QMainWindow {
    Q_OBJECT

public:
    ServoGUI(QWidget *parent = nullptr) : QMainWindow(parent) {
        setWindowTitle("ArmPi Servo Control");
        setGeometry(100, 100, 800, 600);

        // 中心窗口
        QWidget *centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);

        // 主布局
        QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

        // 状态栏
        statusBar = new QStatusBar(this);
        setStatusBar(statusBar);
        statusBar->showMessage("Initializing...");

        // 舵机控制组
        QGroupBox *controlGroup = new QGroupBox("Servo Control");
        QVBoxLayout *controlLayout = new QVBoxLayout(controlGroup);

        // 舵机滑块
        servoSliders.resize(6);
        servoLabels.resize(6);
        servoPositionLabels.resize(6);

        for (int i = 0; i < 6; ++i) {
            QHBoxLayout *sliderLayout = new QHBoxLayout();
            
            QLabel *label = new QLabel(QString("Servo %1:").arg(i+1));
            sliderLayout->addWidget(label);
            servoLabels[i] = label;

            QSlider *slider = new QSlider(Qt::Horizontal);
            slider->setRange(0, 1000);
            slider->setValue(500);
            slider->setTickPosition(QSlider::TicksBelow);
            slider->setTickInterval(100);
            sliderLayout->addWidget(slider);
            servoSliders[i] = slider;

            QLabel *posLabel = new QLabel("500");
            posLabel->setFixedWidth(50);
            sliderLayout->addWidget(posLabel);
            servoPositionLabels[i] = posLabel;

            controlLayout->addLayout(sliderLayout);

            connect(slider, &QSlider::valueChanged, this, [=](int value) {
                servoPositionLabels[i]->setText(QString::number(value));
            });
        }

        controlLayout->addStretch();
        mainLayout->addWidget(controlGroup);

        // 按钮组
        QHBoxLayout *buttonLayout = new QHBoxLayout();

        QPushButton *setButton = new QPushButton("Set Position");
        connect(setButton, &QPushButton::clicked, this, &ServoGUI::setPositions);
        buttonLayout->addWidget(setButton);

        QPushButton *homeButton = new QPushButton("Home Position");
        connect(homeButton, &QPushButton::clicked, this, &ServoGUI::goHome);
        buttonLayout->addWidget(homeButton);

        QPushButton *stopButton = new QPushButton("Stop All");
        connect(stopButton, &QPushButton::clicked, this, &ServoGUI::stopAll);
        buttonLayout->addWidget(stopButton);

        mainLayout->addLayout(buttonLayout);

        // 初始化ROS
        int argc = 0;
        char **argv = nullptr;
        ros::init(argc, argv, "servo_gui");
        nh = new ros::NodeHandle();

        // 发布器
        servoControlPub = nh->advertise<armpi_remote_control::ServoControl>("/armpi_remote/servo_control", 10);

        // 订阅器
        servoStateSub = nh->subscribe("/armpi_remote/servo_states", 10, &ServoGUI::servoStateCallback, this);

        // 定时器用于更新ROS
        rosTimer = new QTimer(this);
        connect(rosTimer, &QTimer::timeout, this, &ServoGUI::updateROS);
        rosTimer->start(100); // 100ms

        statusBar->showMessage("Ready");
    }

    ~ServoGUI() {
        delete nh;
    }

public slots:
    void setPositions() {
        armpi_remote_control::ServoControl msg;
        msg.header.stamp = ros::Time::now();

        for (int i = 0; i < 6; ++i) {
            msg.servo_ids.push_back(i+1);
            msg.positions.push_back(servoSliders[i]->value());
            msg.durations.push_back(500); // 500ms
        }

        msg.save_deviation = false;
        servoControlPub.publish(msg);

        statusBar->showMessage("Position set sent");
    }

    void goHome() {
        armpi_remote_control::ServoControl msg;
        msg.header.stamp = ros::Time::now();

        for (int i = 0; i < 6; ++i) {
            msg.servo_ids.push_back(i+1);
            msg.positions.push_back(500);
            msg.durations.push_back(1000); // 1s
        }

        msg.save_deviation = false;
        servoControlPub.publish(msg);

        for (int i = 0; i < 6; ++i) {
            servoSliders[i]->setValue(500);
            servoPositionLabels[i]->setText("500");
        }

        statusBar->showMessage("Going to home position");
    }

    void stopAll() {
        armpi_remote_control::ServoControl msg;
        msg.header.stamp = ros::Time::now();
        msg.save_deviation = false;
        servoControlPub.publish(msg);

        statusBar->showMessage("All servos stopped");
    }

    void servoStateCallback(const armpi_remote_control::ServoStateFull::ConstPtr& msg) {
        int servo_id = msg->servo_id;
        if (servo_id >= 1 && servo_id <= 6) {
            int index = servo_id - 1;
            servoPositionLabels[index]->setText(QString::number(msg->position));
            servoSliders[index]->setValue(msg->position);
        }
    }

    void updateROS() {
        if (ros::ok()) {
            ros::spinOnce();
        }
    }

private:
    QStatusBar *statusBar;
    std::vector<QSlider*> servoSliders;
    std::vector<QLabel*> servoLabels;
    std::vector<QLabel*> servoPositionLabels;

    ros::NodeHandle *nh;
    ros::Publisher servoControlPub;
    ros::Subscriber servoStateSub;
    QTimer *rosTimer;
};



int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    ServoGUI gui;
    gui.show();
    return app.exec();
}
