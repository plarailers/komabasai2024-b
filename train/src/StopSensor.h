#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* 
   BNO055 to ESP32 Connections
   ===========
   Connect SCL to 22
   Connect SDA to 21
   Connect VDD to 3.3V DC
   Connect GROUND to common ground
   =======
   2015/MAR/03  - First release (KTOWN)
*/

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS 100
#define G 9.798 //gravity in Tokyo
#define PI atan(1)*4

class StopSensor {
    private:
        double          acclt,acclt_bias,acclt_lp;
        bool            stop_flag,stop_flag2;
        // double        accl_lp[3],accl_lp_old[3]; //Low-pass filtered unbiased accleration for x-direction
        unsigned long   time, time_old;
        unsigned long   count;
        double          dt;//Cycle time
        double          F;//Cutoff frequency for low-pass filter which should be less than 50
        double          tau;//Time constant corresponding to cutoff frequency

        // Check I2C device address and correct line below (by default address is 0x29 or 0x28)
        //                                   id, address
        Adafruit_BNO055 bno = Adafruit_BNO055(-1, 0x28, &Wire);

    public:
        StopSensor();
        void    BNO055Setup();  //加速度センサ(BNO055)
        bool    getStopping(void);
        double  getAcclt(double acclt_bias);
        double  getBias();
        double  lowpass(double accle_lp, double acclt, double dt);
};