/*
 Safe Scenario 3. Use only in an authorised Windows 11 VM.
 Opens Notepad and types a marker. It does not save a file.
*/
#include <Keyboard.h>
void setup() {
  delay(5000);
  Keyboard.begin();
  Keyboard.press(KEY_LEFT_GUI);
  Keyboard.press('r');
  delay(100);
  Keyboard.releaseAll();
  delay(500);
  Keyboard.print("notepad");
  Keyboard.write(KEY_RETURN);
  delay(1500);
  Keyboard.print("FYP_SAFE_WINDOWS_NOTEPAD_TEST");
  Keyboard.write(KEY_RETURN);
  Keyboard.end();
}
void loop() {}
