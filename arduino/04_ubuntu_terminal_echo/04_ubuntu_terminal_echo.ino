/*
 Safe Scenario 4. Use only in an authorised Ubuntu desktop VM.
 Opens a terminal and runs only a harmless echo command.
*/
#include <Keyboard.h>
void setup() {
  delay(5000);
  Keyboard.begin();
  Keyboard.press(KEY_LEFT_CTRL);
  Keyboard.press(KEY_LEFT_ALT);
  Keyboard.press('t');
  delay(100);
  Keyboard.releaseAll();
  delay(1500);
  Keyboard.print("echo FYP_SAFE_UBUNTU_TERMINAL_TEST");
  Keyboard.write(KEY_RETURN);
  Keyboard.end();
}
void loop() {}
