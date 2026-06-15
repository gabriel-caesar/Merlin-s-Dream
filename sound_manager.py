import pygame

class SoundManager():
  def __init__(self):
    self.sounds = {
      'button_click': None,
      'fire_bolt': {
        'cast': None,
        'impact': None
      }
    }

  def load_sounds(self) -> None:
    self.sounds['level_up'] = pygame.mixer.Sound('./assets/sound/levelup.wav')
    self.sounds['potion'] = pygame.mixer.Sound('./assets/sound/potion.wav')
    self.sounds['button_click'] = pygame.mixer.Sound('./assets/sound/button_click.wav')
    self.sounds['fire_bolt']['cast'] = pygame.mixer.Sound('./assets/sound/spells/fire_bolt/fire_bolt_cast.ogg')
    self.sounds['fire_bolt']['impact'] = pygame.mixer.Sound('./assets/sound/spells/fire_bolt/fire_bolt_impact.ogg')

  def set_global_sound_volume_to(self, volume: float) -> None:
    for sound in self.sounds.values():
      if isinstance(sound, dict):
        for inner_sound in sound.values():
          inner_sound.set_volume(volume)
      else:
          sound.set_volume(volume)