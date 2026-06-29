from __future__ import annotations
import pygame
import pygame_gui
import utils
import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from sound_manager import SoundManager
  from screen_veil import ScreenVeil

DISPLAY_SIZE = (640, 360)

def load(
  menu_manager: pygame_gui.UIManager, 
  delta: float,
  display: pygame.Surface,
  fragment_list: list,
  menu_elements: dict,
  sound_manager: SoundManager
) -> tuple:
  """
  Loads and controls the main menu screen and returns a boolean value to 
  control if the player is in the main menu or otherwise.
  """
  
  utils.run_fragment_map(fragment_list, display, DISPLAY_SIZE)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    if event.type == pygame_gui.UI_BUTTON_PRESSED:
      if event.ui_element == menu_elements['play_button']:
        sound_manager.sounds['button_click'].play()
        # Plays the gameplay music theme
        music_vol = round(menu_elements['music_slider'].get_current_value() / 100, ndigits=2)

        utils.play_music_theme(vol=music_vol, type='gameplay')
        return False
      
      if event.ui_element == menu_elements['quit_button']:
        sound_manager.sounds['button_click'].play()
        pygame.quit()
        sys.exit()

      if event.ui_element == menu_elements['back_button']:
        sound_manager.sounds['button_click'].play() # Play button sound

        menu_elements['play_button'].show()
        menu_elements['options_button'].show()
        menu_elements['quit_button'].show()

        menu_elements['sound_label'].hide()
        menu_elements['sound_slider'].hide()
        menu_elements['music_label'].hide()
        menu_elements['music_slider'].hide()
        menu_elements['back_button'].hide()

      if event.ui_element == menu_elements['options_button']:
        sound_manager.sounds['button_click'].play() # Play button sound

        menu_elements['play_button'].hide()
        menu_elements['options_button'].hide()
        menu_elements['quit_button'].hide()

        menu_elements['sound_slider'].show()
        menu_elements['sound_slider'].rebuild()
        menu_elements['music_slider'].show()
        menu_elements['music_slider'].rebuild()
        menu_elements['back_button'].show()
        menu_elements['music_label'].show()
        menu_elements['sound_label'].show()

    menu_manager.process_events(event)

  # PygameGUI essentials
  menu_manager.update(delta)
  menu_manager.draw_ui(display)

  # Returning true means the user still is in the main menu
  return True