//Edited by Giani Ollivier
#include "BTS7960.h"

BTS7960::BTS7960(int LPWM,int RPWM,int L_EN,int R_EN,int PRESCALER)
{
  _RPWM = RPWM;
  _LPWM = LPWM;
  _L_EN = L_EN;
  _R_EN = R_EN;
  pinMode(_RPWM, OUTPUT);
  pinMode(_LPWM, OUTPUT);
  pinMode(_L_EN, OUTPUT);
  pinMode(_R_EN, OUTPUT);

  //setPwmFrequencyMEGA2560(_LPWM, PRESCALER);
  //setPwmFrequencyMEGA2560(_RPWM, PRESCALER);
}

void BTS7960::enable()
{
  digitalWrite(_R_EN,1);
  digitalWrite(_L_EN,1);
}

void BTS7960::disable()
{
  digitalWrite(_R_EN,0);
  digitalWrite(_L_EN,0);
}

void BTS7960::stop()
{
  analogWrite(_LPWM,0);
  analogWrite(_RPWM,0);
}

void BTS7960::setSpeed(int pwm)
{
	Serial.println("inside speed");
	Serial.println(pwm);
  if ((pwm < (-255)) || (pwm > 255))
  {
	  Serial.println("inside first if");
	  Serial.println(pwm);
    // out of range stop the motor
    stop();
  }
  else
  {
    if (pwm > 0 )
	{
		Serial.println("inside second if");
		Serial.println(pwm);
		analogWrite(_LPWM,0);
		analogWrite(_RPWM,pwm);
    }
	else
	{
		Serial.println("inside last else");
		Serial.println(pwm);
		analogWrite(_RPWM,0);
		analogWrite(_LPWM,-pwm);
    }
  }
}



void BTS7960::setPwmFrequencyMEGA2560(int pin, int divisor) 
{
  byte mode;
      switch(divisor) {
      case 1: mode = 0x01; break;
      case 2: mode = 0x02; break;
      case 3: mode = 0x03; break;
      case 4: mode = 0x04; break;
      case 5: mode = 0x05; break;
      case 6: mode = 0x06; break;
      case 7: mode = 0x07; break;
      default: return;
      }
      
        switch(pin) {	  
      case 2:  TCCR3B = TCCR3B  & 0b11111000 | mode; break;
      case 3:  TCCR3B = TCCR3B  & 0b11111000 | mode; break;
      case 4:  TCCR0B = TCCR0B  & 0b11111000 | mode; break;
      case 5:  TCCR3B = TCCR3B  & 0b11111000 | mode; break;
      case 6:  TCCR4B = TCCR4B  & 0b11111000 | mode; break;
      case 7:  TCCR4B = TCCR4B  & 0b11111000 | mode; break;
      case 8:  TCCR4B = TCCR4B  & 0b11111000 | mode; break;
      case 9:  TCCR2B = TCCR0B  & 0b11111000 | mode; break;
      case 10: TCCR2B = TCCR2B  & 0b11111000 | mode; break;
      case 11: TCCR1B = TCCR1B  & 0b11111000 | mode; break;  
      case 12: TCCR1B = TCCR1B  & 0b11111000 | mode; break;  
      case 13: TCCR0B = TCCR0B  & 0b11111000 | mode; break;
      default: return;
    }

}
