/*
  Safe Windows process-correlation test.
  Opens Command Prompt and prints a harmless marker.
  Use only in an authorised Windows 11 test VM.
*/

#include <Keyboard.h>

void setup() {
  delay(7000);

  Keyboard.begin();

  // Open Windows Run dialog.
  Keyboard.press(KEY_LEFT_GUI);
  Keyboard.press('r');
  delay(150);
  Keyboard.releaseAll();

  delay(700);

  // Open Command Prompt and keep it running.
  Keyboard.print("cmd /k echo FYP_SAFE_WINDOWS_PROCESS_TEST");
  Keyboard.write(KEY_RETURN);

  Keyboard.end();
}

void loop() {
}