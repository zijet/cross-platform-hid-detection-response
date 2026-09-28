/*
 Safe Scenario 2. Types harmless rapid text into an already focused editor.
*/
#include <Keyboard.h>
void setup() {
  delay(5000);
  Keyboard.begin();
  Keyboard.print("FYP_SAFE_RAPID_HID_TEST_0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZ");
  Keyboard.write(KEY_RETURN);
  Keyboard.end();
}
void loop() {}
