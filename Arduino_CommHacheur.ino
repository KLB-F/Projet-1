/*Code injecter dans l'arduino lié au fichier CommHacheur.py

Calcule et applique le rapport cyclique a selon l'algorithme PAO.
De plus, il prend en entré la tension et la puissance issue d'un multimètre DFRobot INA219
*/

/*!
  Liste des adresses possible pour le wattmètre
   INA219_I2C_ADDRESS1  0x40   A0 = 0  A1 = 0
   INA219_I2C_ADDRESS2  0x41   A0 = 1  A1 = 0
   INA219_I2C_ADDRESS3  0x44   A0 = 0  A1 = 1
   INA219_I2C_ADDRESS4  0x45   A0 = 1  A1 = 1
*/

#include <Wire.h>
#include "DFRobot_INA219.h"
#include <floatToString.h>

DFRobot_INA219_IIC     ina219(&Wire, INA219_I2C_ADDRESS4);

// Paramètres nécessaires pour la calibration
float ina219Reading_mA = 10;
float extMeterReading_mA = 10;

unsigned char PWM = 127;
unsigned int PWM_PIN = 3; //Pin PWM

char StrVm[20]; char StrPm[20]; //Chaine contenant les listes de caractères de Vm et Pm

float Pm = 0; float Vmoy = 0; float Vp = 0; float Pprec=0; //Initialisation des variables de puissance et de tensions

int PAO(unsigned char PWM, float Pmoy, float Pp, float Vm, float Vprec){ //Algorithme PAO
  float dP = Pmoy-Pp; float dV = Vm-Vprec;
  if(dP > 0){
    if(dV > 0){
        return min(255, PWM+1);
    }else{
      return max(0, PWM-1);
    }
  }else{
    if(dV < 0){
        return min(255, PWM+1);
    }else{
      return max(0, PWM-1);
    }
  }
  return min(255, PWM+1);
}

void setup(void){

    Serial.begin(115200);

    while(!Serial);
    
    while(ina219.begin() != true) {
        Serial.println("INA219 begin faild");
        delay(2000);
    }
    ina219.linearCalibrate(ina219Reading_mA, extMeterReading_mA);
    pinMode(PWM_PIN, OUTPUT);
}

void loop(void)
{
  //Acquisition des paramètres
  Vp = Vmoy;
  Pprec = Pm;

  Vmoy = ina219.getBusVoltage_V();
  Pm = ina219.getPower_mW();
  
  PWM = PAO(PWM, Pm, Pprec, Vmoy, Vp);
  
  digitalWrite(PWM_PIN, PWM);

  //Communication à python
  Serial.println(floatToString(Vmoy, StrVm, sizeof(StrVm), 3)+String("S")+floatToString(Pm, StrPm, sizeof(StrPm), 3));

}
