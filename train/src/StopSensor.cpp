#include "StopSensor.h"

StopSensor::StopSensor() 
{
    this->acclt         = 0;
    this->acclt_bias    = 0;
    this->acclt_lp      = 0;
    this->stop_flag     = 1;
    this->stop_flag2    = 1;
    // this->accl_lp[3]    = {0,0,0};
    // this->accl_lp_old[3]= {0,0,0};
    this->time          = 0;
    this->time_old      = 0;
    this->count         = 0;
    this->dt            = 0;
    this->F             = 5; //カットオフ周波数　Hz
    this->tau           = 1.0/(2*PI*F);
}

void StopSensor::BNO055Setup(void)
{
    /* Initialise the sensor */
    if(!bno.begin())
    {
        /* There was a problem detecting the BNO055 ... check your connections */
        Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
        while(1);
    }

    delay(1000);

    bno.setExtCrystalUse(true);

    Serial.println("Calibration status values: 0=uncalibrated, 3=fully calibrated");

    delay(1000);//Wait for sensor inforamtion arrival

    //Get calibration data
    acclt_bias = getBias(); 
    acclt,acclt_lp = getAcclt(acclt_bias);
    Serial.println("Estimated bias for acclt:" + String(acclt_bias));
}

bool StopSensor::getStopping(void)
{
    //Measure cycle
    time_old = time;
    time = micros();
    dt = double(time - time_old)/1000000.0;
    Serial.print("dt:");
    Serial.print(dt);
    Serial.print(", ");

    // Possible vector values can be:
    // - VECTOR_ACCELEROMETER - m/s^2
    // - VECTOR_MAGNETOMETER  - uT
    // - VECTOR_GYROSCOPE     - rad/s
    // - VECTOR_EULER         - degrees
    // - VECTOR_LINEARACCEL   - m/s^2
    // - VECTOR_GRAVITY       - m/s^2

    acclt = getAcclt(acclt_bias);
    acclt_lp = lowpass(acclt_lp,acclt,dt); 

    if(abs(acclt_lp)< 0.03){
        stop_flag = 1;
    }else{
        stop_flag = 0;
    }

    if (stop_flag == 0){
        stop_flag2 = 0;
    }

    if(stop_flag == 1){
        if(count > 200){
        stop_flag2 = 1;
        count = 0;
        }
        count++;
    }

    Serial.print("5:");
    Serial.print(5);
    Serial.print(", -5:");
    Serial.print(-5);
    
    Serial.print(", Acclt:");
    Serial.print(acclt);
    Serial.print(", Acclt_lp:");
    Serial.print(acclt_lp);
    Serial.print(", Stop:");
    Serial.print(stop_flag);
    Serial.print(", Stop_flag2:");
    Serial.println(stop_flag2);

    delay(1);

    return stop_flag2;
}


double StopSensor::getAcclt(double acclt_bias){
    imu::Vector<3> accl = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    double acclt = sqrt(pow(double(accl.x()),2) + pow(double(accl.y()),2) + pow(double(accl.z()),2)) - acclt_bias;
    return acclt;
}

double StopSensor::getBias(){
    double acclt_bias = 0;   
    for(int i=0;i<10;++i){
        acclt_bias += getAcclt(0);
    }
    acclt_bias /= 10.0;
    return acclt_bias;
}

double StopSensor::lowpass(double acclt_lp,double acclt,double dt){
    double a = tau/(dt + tau);
    acclt_lp = a*acclt_lp + (1 - a)*acclt;
    return acclt_lp;
}