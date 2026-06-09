import pygame

class SoundManager():
  def __init__(self):
    self.sounds = {}

  def load_sounds(self) -> None:
    self.sounds['button_click'] = pygame.mixer.Sound('./assets/sound/button_click.wav')

  def set_global_sound_volume_to(self, volume: float) -> None:
    for sound in self.sounds.values():
      sound.set_volume(volume)