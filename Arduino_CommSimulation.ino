/*Code injecter dans l'arduino pour fonctionner avec le fichier CommSimulation.py

Il renvoie le rapport cyclique a obtenue grâce à l'algorithme PAO et analyse les entrées issuent de python.
*/
const byte numChars = 64; //Nombre de caractère maximum possible en entrer
char StrVm[numChars];  

unsigned char PWM = 50; int i = 0;
long P[5] = {0,0,0,0,0}; long Pmoy; long Pprec = -1;long Ptemp; //Puissance en umW
int V[5] = {0,0,0,0,0}; int Vmoy = 0; int Vtemp = 0; int Vprec = -1; //Voltage en mV
//Méthode de MPPT
int PAO(unsigned char PWM, long Pmoy, long Pp, int Vm, int Vprec){
  long dP = Pmoy-Pp; int dV = Vmoy-Vprec;
  if(dP < 0){
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

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  Serial.println(PWM);
}

void loop() {
  static byte ndx = 0;
    char endMarker = 'f';
    char rc;
    bool go = false;
    
    //Lecture des caractère si il y en a
    while(Serial.available() > 0) {
        rc = Serial.read();

        if (rc != endMarker) {
            caractereRecu[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            caractereRecu[ndx] = '\0'; // Caractère de fin
            ndx = 0;
            go = true;
        }
    }

    if(go){

    //Analyse des caractere pour lire la puissance et la tension

    char caracterePuissance[int(numChars/2)];
    char caractereTension[int(numChars/2)];

    bool PuissanceLect = true;
    unsigned char j = 0; 
    unsigned char rcc = 0;

    //Separation en 2 chaines de caractères
    while(caractereRecu[j] != '\0'){
      if(PuissanceLect){
        if(caractereRecu[j] == ';'){
          caracterePuissance[j] = '\0';
          PuissanceLect = false;
        }else{
          caracterePuissance[j] = caractereRecu[j];
        }
      }else{
          caractereTension[rcc] = caractereRecu[j];
          rcc++;
      }
      j++;
    }
    caractereTension[j] = '\0';


    int Vtemp = atoi(caractereTension);
    long Ptemp = atol(caracterePuissance);

    //Serial.print("V temp : "); Serial.println(Vtemp); DEBOGAGE SEULEMENT
    //Serial.print(" P temp : "); Serial.println(Ptemp); DEBOGAGE SEULEMENT

    //

    P[i] = Ptemp; V[i] = Vtemp;
    i++;
    if(i==5){
    i = 0;
    Pmoy = long((P[0]+P[1]+P[2]+P[3]+P[4])/5);
    Vmoy = int((V[0]+V[1]+V[2]+V[3]+V[4])/5);
    /*Serial.println("P liste : ");
    for(int k  = 0; k < 5; k++){
      Serial.println(P[k]);
    }
    Serial.println("V liste : ");
    for(int k  = 0; k < 5; k++){
      Serial.println(V[k]);
    } DEBGOGAGE SEULEMENT */

    //Serial.print("Puissance moyenne : "); Serial.println(Pmoy); DEBOGAGE SEULEMENT
    //Serial.print("Tension moyenne : "); Serial.println(Vmoy); DEBOGAGE SEULEMENT
    PWM = PAO(PWM, Pmoy, Pprec, Vmoy, Vprec);
    Pprec = Pmoy; Vprec = Vmoy;
    Serial.println(PWM);
    }
}
}
