#include <WiFi.h>
#include <stdlib.h>

#define motor_0 2
#define motor_1 0
#define motor_2 4
#define motor_3 16

#define STEP_ANGLE 5.625

#define WIFI_SSID "esp32pls"
#define WIFI_PASSWORD "12345678"

#define PORT 5000
#define HOST "10.186.112.1"

uint8_t temp_flag = 0;

// only need 3 bits but uint3_t is not a thing :)
uint8_t rot_motor_state = 0;

// half step map:
// 1000, 1100, 0100, 0110, 0010, 0011, 0001, 1001

WiFiClient client;

// half steps forwards or backwards for more precision
// dir 0 -> clockwise, dir 1 -> counter clockwise

void rot_half_step(uint8_t* rot_motor_state, int dir){  

    // update pins
    if(dir == 0){
      // front step
      switch(*rot_motor_state){
      // case 0 means go to state 1
      case 0:
        digitalWrite(motor_1, HIGH);
        break;
      case 1:
        digitalWrite(motor_0, LOW);
        break;
      case 2:
        digitalWrite(motor_2, HIGH);
        break;
      case 3:
        digitalWrite(motor_1, LOW);
        break;
      case 4:
        digitalWrite(motor_3, HIGH);
        break;
      case 5:
        digitalWrite(motor_2, LOW);
        break;
      case 6:
        digitalWrite(motor_0, HIGH);
        break;
      case 7:
        digitalWrite(motor_3, LOW);
        break;
      }
    } else {
      // back step
      switch(*rot_motor_state){
      // case 0 means we must go to state 7
      case 0:
        digitalWrite(motor_3, HIGH);
        break;
      case 1
        digitalWrite(motor_1, LOW);
        break;
      case 2:
        digitalWrite(motor_0, HIGH);
        break;
      case 3:
        digitalWrite(motor_2, LOW);
        break;
      case 4:
        digitalWrite(motor_1, HIGH);
        break;
      case 5:
        digitalWrite(motor_3, LOW);
        break;
      case 6:
        digitalWrite(motor_2, HIGH);
        break;
      case 7:
        digitalWrite(motor_0, LOW);
        break;
      }
    }

    if(dir == 0){
      if(*rot_motor_state == 7){
        *rot_motor_state = 0;
      } else {
        (*rot_motor_state) += 1;
      }
    } else {
      if(*rot_motor_state == 0){
        *rot_motor_state = 7;
      } else {
        (*rot_motor_state) -= 1;
      }
    }

    delayMicroseconds(2500);
}

// will call rot_half_step to turn motor 'degrees' degrees
// dir 0 -> clockwise, dir 1 -> counter-clockwise
void drive_rotational_motor(int degrees, int dir){
  // the motor rotates 5.625 degrees every 64 steps,
  // hence the expression in the condition
  for(int i = 0; i < (degrees*64)/STEP_ANGLE; i++){
    rot_half_step(&rot_motor_state, dir);
  }

  // debug for loop, will only step 8 times to see whats going on
  /*
  for(int i = 0; i < 8; i++){
    rot_half_step(&rot_motor_state, dir);
  }
  */
}

void setup() {
  // put your setup code here, to run once:
  pinMode(motor_0, OUTPUT);
  pinMode(motor_1, OUTPUT);
  pinMode(motor_2, OUTPUT);
  pinMode(motor_3, OUTPUT);

  pinMode(23, OUTPUT);
  digitalWrite(motor_0, HIGH);

// MAC: C4:DD:57:C9:8A:F8

  Serial.begin(9600);
  Serial.print("Connecting to wifi...\n");
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int counter = 0;
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
    counter++
    if(counter >= 60){
      break;
    }
  }

  if(WiFi.status() != WL_CONNECTED){
    Serial.print("\nFailed...");
  } else {
    Serial.print("\nConnected with local IP: ");
    Serial.println(WiFi.localIP());
  }

  if(!client.connect(HOST, PORT)){
      Serial.print("\nFailed to connect to host...");
  } else {
      Serial.print("\nConnected to host...\n");
  }
  client.print("mc32");

}

int string_to_int(String s){
  int len = s.length();
  int total = 0;
  for(int i = 0; i < len; i++){
    total = total*10 + (s[i]-48);
  }
  Serial.print("\nTotal: ");
  Serial.println(total);
  return total;
}

// mc32
void loop() {
  // put your main code here, to run repeatedly:

  String s = client.readStringUntil('\r');
  int degrees = string_to_int(s);
  if(degrees != 0){
    drive_rotational_motor(degrees, 1);
  }

  Serial.print("\nDone reading host's message...");
  delay(5000); 

}