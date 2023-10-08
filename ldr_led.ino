
int led=13;
int ldr_input=A5;
unsigned long previousMillis = 0;  // variable to store the previous time
const long interval = 1000;  // interval to wait for (in milliseconds)

void setup() {

  // put your setup code here, to run once:
  pinMode(led,OUTPUT);
  pinMode(ldr_input,INPUT);
  Serial.begin(9600);
}

void loop() {

    // put your main code here, to run repeatedly:
  unsigned long currentMillis = millis();  // get the current time
  
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;  // save the current time for the next interval
   
  // put your main code here, to run repeatedly:
      //Control Bulb based on LDR
  int ldrStatus=analogRead(ldr_input);
  Serial.println(ldrStatus);
  if(ldrStatus<=30)   //when it's dark less conductivity(low voltage)
  {
    digitalWrite(led,1);
    Serial.println("Dark outside, Bulb is ON");
  }
  else
  {
    digitalWrite(led,0);
    Serial.println("Bright outside");
  }
//  Serial.println(ldrStatus);
}
}