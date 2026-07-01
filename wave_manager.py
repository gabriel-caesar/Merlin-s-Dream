from __future__ import annotations
import utils
import pygame

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from screen_veil import ScreenVeil
  from sound_manager import SoundManager

class WaveManager():
  def __init__(
    self,
    map_data: list,
    enemies_list: list,
    gui_elements: dict,
    pause_menu_elements: dict,
    screen_veil: ScreenVeil,
    sound_manager: SoundManager,
    wave: int = 1,
  ):
    self.current_wave = wave
    self.wave_timer = 180
    self.enemies_list = enemies_list
    self.map_data = map_data  
    self.enemy_names = ['orc']
    self.gui_elements = gui_elements
    self.pause_menu_elements = pause_menu_elements
    self.screen_veil = screen_veil
    self.sound_manager = sound_manager
    self.boss_wave = self.current_wave % 5 == 0
    self.wave_display_timer = 120 if not self.boss_wave else 180

  def display_current_wave(self):
    wave_label = self.gui_elements['wave_label']
    wave_label.set_text(f'Wave {self.current_wave}')

    # Wave display is inside pause_menu_elements because of layering
    # and so that it can show up on top of the screen veil
    wave_display = self.pause_menu_elements['wave_display']
    if self.boss_wave:
      wave_display.set_text(f'Boss Wave {self.current_wave}')
    else:
      wave_display.set_text(f'Wave {self.current_wave}')

    wave_display.show()
    self.screen_veil.toggle = True

  def handle_enemy_addition(
    self,
    index: int,
    enemy_name: str,
    current_wave: str
  ):

    if 'orc' in enemy_name:
      if int(current_wave[index]) == 1:
        self.enemy_names = ['orc']
      elif int(current_wave[index]) == 2:
        self.enemy_names.append('orc_archer')
      elif int(current_wave[index]) == 3:
        self.enemy_names.append('orc_axe')

    elif 'shadow' in enemy_name:
      if int(current_wave[index]) == 6:
        self.enemy_names = ['shadow']
      elif int(current_wave[index]) == 7:
        self.enemy_names.append('shadow_archer')
      elif int(current_wave[index]) == 8:
        self.enemy_names.append('shadow_caster')

  def update_enemies(self) -> None:
    # Transforming to string so we can index it
    current_wave = str(self.current_wave)

    # Conditions for one number integers
    if len(current_wave) == 1:
      if (
        int(current_wave[0]) >= 1 and 
        int(current_wave[0]) <= 5
      ):
        # Updating what creatures will be spawned based on the wave length
        self.handle_enemy_addition(
          index=0,
          enemy_name='orc',
          current_wave=current_wave
        )

      elif (
        int(current_wave[0]) >= 6 and 
        int(current_wave[0]) <= 9
      ):
        # Updating what creatures will be spawned based on the wave length
        self.handle_enemy_addition(
          index=0,
          enemy_name='shadow',
          current_wave=current_wave
        )

    # Conditions for two number integers
    else:
      if (
        int(current_wave[1]) >= 1 and 
        int(current_wave[1]) <= 5
      ):
        # Updating what creatures will be spawned based on the wave length
        self.handle_enemy_addition(
          index=1,
          enemy_name='orc',
          current_wave=current_wave
        )

      elif (
        int(current_wave[1]) >= 6 and 
        int(current_wave[1]) <= 9
      ):
        # Updating what creatures will be spawned based on the wave length
        self.handle_enemy_addition(
          index=1,
          enemy_name='shadow',
          current_wave=current_wave
        )
    

  def update(self, enemies_group: pygame.sprite.Group, display: pygame.Surface):

    if self.pause_menu_elements['wave_display'].visible and self.wave_display_timer > 0:
      self.wave_display_timer -= 1

      if self.wave_display_timer == 0:
        self.pause_menu_elements['wave_display'].hide()
        self.wave_display_timer = 120 if not self.boss_wave else 180
        self.screen_veil.toggle = False

    if len(self.enemies_list) == 0:

      if self.wave_timer > 0:
        self.wave_timer -= 1

      if self.wave_timer == 0:

        # Checking if the previous wave was a boss fight and if
        # it was, change the song back to the gameplay track
        if self.boss_wave:
          pygame.event.post(pygame.event.Event(pygame.USEREVENT + 13, track='gameplay'))

          if self.current_wave % 10 == 0:
              biome_type = 'grass'
          elif self.current_wave % 5 == 0:
              biome_type = 'stone'
          else:
              biome_type = 'grass'

          # Changing the map biome accordingly as Merlin defeats different bosses
          pygame.event.post(pygame.event.Event(pygame.USEREVENT + 8, biome=biome_type))

        self.current_wave += 1 # Advance current wave

        # Updating these important signals every time
        self.boss_wave = self.current_wave % 5 == 0
        self.wave_display_timer = 120 if not self.boss_wave else 180          

        # Announce the wave advancement
        self.display_current_wave() 

        # Add different enemies per wave
        self.update_enemies()

        # Updating what creatures will be spawned based on the wave length
        if self.current_wave == 2:
          self.enemy_names.append('orc_archer')
        elif self.current_wave == 3:
          self.enemy_names.append('orc_axe')


        # If it is a boss wave
        if self.boss_wave:
          self.enemies_list = utils.add_n_enemies(
            map_data=self.map_data,
            n=1,
            enemy_group=enemies_group,
            enemy_name='shadow_caster_boss' if len(str(self.current_wave)) > 1 and str(self.current_wave)[1] == '0' else 'orc_boss',
            display=display,
            wave=self.current_wave,
            sound_manager=self.sound_manager,
            is_boss=True
          )
          pygame.event.post(pygame.event.Event(pygame.USEREVENT + 13, track='boss'))
        
        else:
          for name in self.enemy_names:
            self.enemies_list = utils.add_n_enemies(
              map_data=self.map_data,
              # n=self.current_wave if self.current_wave < 5 else 5, # Max. 15 enemies per wave
              n=1,
              enemy_group=enemies_group,
              enemy_name=name,
              display=display,
              wave=self.current_wave,
              sound_manager=self.sound_manager
            )

        self.wave_timer = 180
