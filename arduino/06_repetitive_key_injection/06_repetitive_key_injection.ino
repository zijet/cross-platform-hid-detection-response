/*
  Safe repetitive-key HID scenario.
  Produces a rapid and regular sequence of one harmless character.
  Use only inside an authorised Windows 11 or Ubuntu test VM.
*/

#include <Keyboard.h>

void setup() {
  delay(7000);

  Keyboard.begin();

  for (int i = 0; i < 80; i++) {
    Keyboard.write('a');
    delay(10);
  }

  Keyboard.write(KEY_RETURN);
  Keyboard.end();
}

void loop() {
}