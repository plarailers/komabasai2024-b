class GetWheelSpeed
{
    public:
        int     MOTOR_CURRENT_PIN;
        int     MOTOR_VOLTAGE_PIN;
        float   wheelSpeed;
        GetWheelSpeed();
        float   getWheelSpeed(int MOTOR_CURRENT_PIN);
};

GetWheelSpeed::GetWheelSpeed() {
    this->MOTOR_CURRENT_PIN     = 32;
    this->MOTOR_VOLTAGE_PIN     = 33;
    this->wheelSpeed            = 0;
}

float GetWheelSpeed::getWheelSpeed(int MOTOR_CURRENT_PIN) {
    return wheelSpeed;
}