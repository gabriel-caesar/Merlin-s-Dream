from __future__ import annotations
import utils
import pygame
import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from screen_veil import ScreenVeil

class WaveManager():
  def __init__(
    self,
    map_data: list,
    enemies_list: list,
    gui_elements: dict,
    pause_menu_elements: dict,
    screen_veil: ScreenVeil,
    wave: int = 1,
  ):
    self.current_wave = wave
    self.wave_timer = 180
    self.wave_display_timer = 120
    self.enemies_list = enemies_list
    self.map_data = map_data  
    self.enemy_names = ['orc']
    self.gui_elements = gui_elements
    self.pause_menu_elements = pause_menu_elements
    self.screen_veil = screen_veil

  def display_current_wave(self, wave_length):
    wave_label = self.gui_elements['wave_label']
    wave_label.set_text(f'Wave {wave_length}')

    # Wave display is inside pause_menu_elements because of layering
    # and so that it can show up on top of the screen veil
    wave_display = self.pause_menu_elements['wave_display']
    wave_display.set_text(f'Wave {wave_length}')

    wave_display.show()
    self.screen_veil.toggle = True

  def update(self, enemies_group: pygame.sprite.Group, display: pygame.Surface):

    if self.pause_menu_elements['wave_display'].visible and self.wave_display_timer > 0:
      self.wave_display_timer -= 1

      if self.wave_display_timer == 0:
        self.pause_menu_elements['wave_display'].hide()
        self.wave_display_timer = 120
        self.screen_veil.toggle = False

    if len(self.enemies_list) == 0:

      if self.wave_timer > 0:
        self.wave_timer -= 1

      if self.wave_timer == 0:
        self.current_wave += 1 # Advance current wave
        self.display_current_wave(self.current_wave) # Announce the wave advancement

        # Updating what creatures will be spawned based on the wave length
        if self.current_wave == 2:
          self.enemy_names.append('orc_archer')
        elif self.current_wave == 3:
          self.enemy_names.append('orc_axe')

        for name in self.enemy_names:
          self.enemies_list = utils.add_n_enemies(
            map_data=self.map_data,
            n= self.current_wave + 1,
            enemy_group=enemies_group,
            enemy_name=name,
            display=display,
            atk_range=90 if name == 'orc_archer' else 20,
            wave=self.current_wave
          )

        self.wave_timer = 180