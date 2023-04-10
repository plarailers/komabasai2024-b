class GetWheelSpeed
{
    public:
        int     MOTOR_CURRENT_SENSOR_PIN;
        GetWheelSpeed();
        double  getWheelSpeed(int MOTOR_CURRENT_SENSOR_PIN);
};

GetWheelSpeed::GetWheelSpeed() {
    this->MOTOR_CURRENT_SENSOR_PIN = 4;
}

double GetWheelSpeed::getWheelSpeed(int MOTOR_CURRENT_SENSOR_PIN) {
    double  wheelSpeed;
    return wheelSpeed;
}