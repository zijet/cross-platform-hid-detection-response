/*
 Safe Scenario 1. Use only in an authorised VM with a text editor focused.
*/
#include <Keyboard.h>
const char MESSAGE[] = "FYP SAFE HUMAN LIKE TYPING TEST";
const int DELAYS[] = {120,180,95,210,140,165,110,230};
void setup() {
  delay(5000);
  Keyboard.begin();
  for (unsigned int i=0; i<sizeof(MESSAGE)-1; i++) {
    Keyboard.write(MESSAGE[i]);
    delay(DELAYS[i % 8]);
  }
  Keyboard.write(KEY_RETURN);
  Keyboard.end();
}
void loop() {}
