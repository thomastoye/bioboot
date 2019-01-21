#include <Wire.h>
#include <TimerOne.h>
#include "lib/BTS7960.h"
#include "lib/BTS7960.cpp"

//Motordriver declarations
String motorSetting;
BTS7960 mL(2, 3, 4, 5, 1);
BTS7960 mR(6, 7, 8, 9, 1);

#define   LEFT_MOTOR    1
#define   RIGHT_MOTOR   2


//MPU declartions

#define    MPU9250_ADDRESS            0x68
#define    MAG_ADDRESS                0x0C

#define    GYRO_FULL_SCALE_250_DPS    0x00
#define    GYRO_FULL_SCALE_500_DPS    0x08
#define    GYRO_FULL_SCALE_1000_DPS   0x10
#define    GYRO_FULL_SCALE_2000_DPS   0x18

#define    ACC_FULL_SCALE_2_G        0x00
#define    ACC_FULL_SCALE_4_G        0x08
#define    ACC_FULL_SCALE_8_G        0x10
#define    ACC_FULL_SCALE_16_G       0x18

// This function read Nbytes bytes from I2C device at address Address.
// Put read bytes starting at register Register in the Data array.
void I2Cread(uint8_t Address, uint8_t Register, uint8_t Nbytes, uint8_t* Data)
{
  // Set register address
  Wire.beginTransmission(Address);
  Wire.write(Register);
  Wire.endTransmission();

  // Read Nbytes
  Wire.requestFrom(Address, Nbytes);
  uint8_t index = 0;
  while (Wire.available())
    Data[index++] = Wire.read();
}


// Write a byte (Data) in device (Address) at register (Register)
void I2CwriteByte(uint8_t Address, uint8_t Register, uint8_t Data)
{
  // Set register address
  Wire.beginTransmission(Address);
  Wire.write(Register);
  Wire.write(Data);
  Wire.endTransmission();
}

// Initial time
long int ti;
volatile bool intMpuFlag = false;

// Initializations
void setup()
{
  // Arduino initializations
  Wire.begin();
  Serial.begin(9600);

  // Set accelerometers low pass filter at 5Hz
  I2CwriteByte(MPU9250_ADDRESS, 29, 0x06);
  // Set gyroscope low pass filter at 5Hz
  I2CwriteByte(MPU9250_ADDRESS, 26, 0x06);


  // Configure gyroscope range
  I2CwriteByte(MPU9250_ADDRESS, 27, GYRO_FULL_SCALE_1000_DPS);
  // Configure accelerometers range
  I2CwriteByte(MPU9250_ADDRESS, 28, ACC_FULL_SCALE_4_G);
  // Set by pass mode for the magnetometers
  I2CwriteByte(MPU9250_ADDRESS, 0x37, 0x02);

  // Request continuous magnetometer measurements in 16 bits
  I2CwriteByte(MAG_ADDRESS, 0x0A, 0x16);

  pinMode(13, OUTPUT);
  Timer1.initialize(500000);         // initialize timer1, and set a 1/2 second period
  Timer1.attachInterrupt(callback);  // attaches callback() as a timer overflow interrupt


  // Store initial time
  ti = millis();


  //Motor drivers initialization
  // reserve 40 bytes for the motorSetting:
  motorSetting.reserve(40);
  mL.enable();
  mR.enable();
}





// Counter
long int cpt = 0;

void callback()
{
  intMpuFlag = true;
  digitalWrite(13, digitalRead(13) ^ 1);
}


void serialEvent()
{
  // Format:
  // "r 255\n" - Set right motor to 255
  // "l   0\n" - Set left motor to 0
  // "l-255\n" - Set left motor to -255
  // Length of input should always be 6 characters
  //  Character 0: 'r' or 'l' -- right or left motor
  //  Character 1: '-' or ' ' -- whether to negate. Ignore if not '-' (no negation)
  //  Character 2: left-most digit or ' ' if no left-most digit
  //  Character 3: middle digit or ' ' if no left-most digit
  //  Character 4: right-most digit
  //  Character 5: '\n'
  
  if (Serial.available() >= 6) {
    motorSetting = "";


    while (Serial.available() > 0) {
      int inChar = Serial.read();
      motorSetting += (char)inChar;

      if (inChar == '\n') {
        int whatMotor = 0;
        int whatSpeed = 0;
        String toParse = "";
        toParse.reserve(3);

        // Parse the incoming string
        if (motorSetting[0] == 'r') {
          whatMotor = RIGHT_MOTOR;
        } else if (motorSetting[0] == 'l') {
          whatMotor = LEFT_MOTOR;
        } else {
          Serial.println("{\"error\":\"Input didn't start with r or l\"}");
          Serial.println(motorSetting[0]);
        }

        if (isDigit(motorSetting[2])) {
          toParse += motorSetting[2]; // left-most digit
        }

        if (isDigit(motorSetting[3])) {
          toParse += motorSetting[3]; // middle digit
        }

        toParse += motorSetting[4]; // right-most digit

        whatSpeed = toParse.toInt();

        if (motorSetting[1] == '-') {
          whatSpeed *= -1;
        }

        if (whatMotor == LEFT_MOTOR) {
          Serial.print("{\"left\":");
          Serial.print(whatSpeed, DEC);
          Serial.println("}");
          
          mL.setSpeed(whatSpeed);
        }

        if (whatMotor == RIGHT_MOTOR) {
          Serial.print("{\"right\":");
          Serial.print(whatSpeed, DEC);
          Serial.println("}");
          
          mR.setSpeed(whatSpeed);
        }

        break;
      }
    }
  }
}

// Main loop, read and display data
void loop()
{
  if (intMpuFlag)
  {
    intMpuFlag = false;


    // _______________
    // ::: Counter :::

    // Display data counter
    //  Serial.print (cpt++,DEC);
    //  Serial.print ("\t");



    // ____________________________________
    // :::  accelerometer and gyroscope :::

    // Read accelerometer and gyroscope
    uint8_t Buf[14];
    I2Cread(MPU9250_ADDRESS, 0x3B, 14, Buf);

    // Create 16 bits values from 8 bits data

    // Accelerometer
    int16_t ax = -(Buf[0] << 8 | Buf[1]);
    int16_t ay = -(Buf[2] << 8 | Buf[3]);
    int16_t az = Buf[4] << 8 | Buf[5];

    // Gyroscope
    int16_t gx = -(Buf[8] << 8 | Buf[9]);
    int16_t gy = -(Buf[10] << 8 | Buf[11]);
    int16_t gz = Buf[12] << 8 | Buf[13];

    // Display values

    // Accelerometer
    Serial.print('{');
    Serial.print('"');
    Serial.print("ax");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print (ax, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');
    Serial.print("ay");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print (ay, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');
    Serial.print("az");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print (az, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');

    // Gyroscope
    Serial.print("gx");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print (gx, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');
    Serial.print("gy");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print (gy, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');
    Serial.print("gz");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print (gz, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');


    // _____________________
    // :::  Magnetometer :::


    // Read register Status 1 and wait for the DRDY: Data Ready

    uint8_t ST1;
    do
    {
      I2Cread(MAG_ADDRESS, 0x02, 1, &ST1);
    }
    while (!(ST1 & 0x01));

    // Read magnetometer data
    uint8_t Mag[7];
    I2Cread(MAG_ADDRESS, 0x03, 7, Mag);


    // Create 16 bits values from 8 bits data

    // Magnetometer
    int16_t mx = -(Mag[3] << 8 | Mag[2]);
    int16_t my = -(Mag[1] << 8 | Mag[0]);
    int16_t mz = -(Mag[5] << 8 | Mag[4]);


    // Magnetometer
    Serial.print("mx");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print(mx + 200, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');
    Serial.print("my");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print(my - 70, DEC);
    Serial.print('"');
    Serial.print(",");
    Serial.print('"');
    Serial.print("mz");
    Serial.print('"');
    Serial.print(":");
    Serial.print('"');
    Serial.print(mz - 700, DEC);
    Serial.print('"');
    Serial.print('}');



    // End of line
    Serial.println("");
    //  delay(100);
  }
}
