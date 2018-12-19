/*
	Giani Ollivier
*/
#ifndef BTS7960_h
#define BTS7960_h
#include "Arduino.h"

class BTS7960
{
  public:
    BTS7960(int RPWM,int LPWM,int L_EN,int R_EN,int _PRESCALER);
    void enable();
    void disable();
    void stop();
	void setSpeed(int pwm);
    

  private:
	void setPwmFrequencyMEGA2560(int pin, int divisor);
    int _RPWM;
    int _LPWM;
    int _L_EN;
    int _R_EN;
};
#endif
