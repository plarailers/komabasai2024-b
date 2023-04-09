#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* This driver reads raw data from the BNO055

   Connections
   ===========
   Connect SCL to analog 5
   Connect SDA to analog 4
   Connect VDD to 3.3V DC
   Connect GROUND to common ground

   History
   =======
   2015/MAR/03  - First release (KTOWN)
*/

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (100)
#define PI atan(1)*4
#define G 9.798//gravity in Tokyo

double acclt,acclt_bias,acclt_lp = 0;
bool stop_flag,stop_flag2 = 1;
//double accl_lp[3],accl_lp_old[3] = {0,0,0};//Low-pass filtered unbiased accleration for x-direction
unsigned long time, time_old;
unsigned long count;
double dt = 0;//Cycle time
const double F = 5;//Cutoff frequency for low-pass filter which should be less than 50
const double  tau = 1.0/(2*PI*F);//Time constant corresponding to cutoff frequency


// Check I2C device address and correct line below (by default address is 0x29 or 0x28)
//                                   id, address
Adafruit_BNO055 bno = Adafruit_BNO055(-1, 0x28, &Wire);

void Train::BNO055Setup(void)
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

void Train::getStopping(void)
{
  //Measure cycle
  time_old = time;
  time = micros();
  dt = double(time - time_old)/1000000.0;

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

  
  Serial.print("Acclt:");
  Serial.print(acclt);
  Serial.print(", Acclt_lp:");
  Serial.print(acclt_lp);
  Serial.print(", Stop:");
  Serial.print(stop_flag);
  Serial.print(", Stop_flag2:");
  Serial.println(stop_flag2);

  delay(1);

  return stop_frag2;
}


double getAcclt(double acclt_bias){
  imu::Vector<3> accl = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  double acclt = sqrt(pow(double(accl.x()),2) + pow(double(accl.y()),2) + pow(double(accl.z()),2)) - acclt_bias;
  return acclt;  
}

double getBias(){
  double acclt_bias = 0;   
  for(int i=0;i<10;++i){
    acclt_bias += getAcclt(0);
  }
  acclt_bias /= 10.0;
  return acclt_bias;
}

double lowpass(double acclt_lp,double acclt,double dt){
  double a = tau/(dt + tau);
  acclt_lp = a*acclt_lp + (1 - a)*acclt;
  return acclt_lp;
}
