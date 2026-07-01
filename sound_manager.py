import pygame

class SoundManager():
  def __init__(self):
    self.sounds = {
      'button_click': None,
      'click_1_sound': None,
      'click_3_sound': None,
      'activate_all_spells': None,
      'spell_channeling': None,
      'boss_laugh': None,
      'warning_sound': None,
      'notice_sound': None,

      'swing': None,

      'ogre': {
        'roar': None,
        'impact': None
      },

      'arrow': {
        'cast': None,
        'impact': None
      },

      'orc_death_sounds': {
        '0': None,
        '1': None,
        '2': None,
      },

      'shadow_death_sounds': {
        '0': None,
        '1': None,
        '2': None,
      },

      'text_bleep': {
        '0': None,
        '1': None,
        '2': None,
      },

      'fire_bolt': {
        'cast': None,
        'impact': None
      },

      'shadow_bolt': {
        'cast': None,
        'impact': None
      },

      'magic_bolt': {
        'impact': None
      },

      'teletransport': {
        'cast': None
      }
    }

  def load_sounds(self) -> None:
    # ======= UI =======
    self.sounds['button_click'] = pygame.mixer.Sound('./assets/sound/button_click.wav')
    self.sounds['button_click_2'] = pygame.mixer.Sound('./assets/sound/button_click_2.wav')

    # ======= GAMEPLAY =======
    self.sounds['potion'] = pygame.mixer.Sound('./assets/sound/potion.wav')
    self.sounds['level_up'] = pygame.mixer.Sound('./assets/sound/levelup.wav')
    self.sounds['merlin_death'] = pygame.mixer.Sound('./assets/sound/merlin_death.wav')
    self.sounds['activate_all_spells'] = pygame.mixer.Sound('./assets/sound/activate_all_spells.flac')
    self.sounds['warning_sound']= pygame.mixer.Sound('./assets/sound/warning_sound.wav')
    self.sounds['notice_sound']= pygame.mixer.Sound('./assets/sound/notice_sound.wav')

    # ======= SPELLS =======
    self.sounds['fire_bolt']['cast'] = pygame.mixer.Sound('./assets/sound/spells/fire_bolt/cast.ogg')
    self.sounds['fire_bolt']['impact'] = pygame.mixer.Sound('./assets/sound/spells/fire_bolt/impact.ogg')
    self.sounds['shadow_bolt']['impact'] = pygame.mixer.Sound('./assets/sound/spells/shadow_bolt/impact.ogg')
    self.sounds['shadow_bolt']['cast'] = pygame.mixer.Sound('./assets/sound/spells/shadow_bolt/cast.wav')
    self.sounds['magic_bolt']['impact'] = pygame.mixer.Sound('./assets/sound/spells/magic_bolt/impact.wav')
    self.sounds['teletransport']['cast'] = pygame.mixer.Sound('./assets/sound/spells/tp/cast.wav')
    self.sounds['spell_channeling'] = pygame.mixer.Sound('./assets/sound/spells/channeling.ogg')

    # ======= CURSOR =======
    self.sounds['click_1_sound'] = pygame.mixer.Sound('./assets/sound/click_1_sound.wav')
    self.sounds['click_3_sound'] = pygame.mixer.Sound('./assets/sound/click_3_sound.wav')

    # ======= ENEMIES =======
    self.sounds['swing'] = pygame.mixer.Sound('./assets/sound/enemies/default/melee_swing.wav')
    self.sounds['arrow']['cast'] = pygame.mixer.Sound('./assets/sound/enemies/default/arrow/cast.wav')
    self.sounds['arrow']['impact'] = pygame.mixer.Sound('./assets/sound/enemies/default/arrow/impact.wav')
    self.sounds['boss_laugh'] = pygame.mixer.Sound('./assets/sound/boss_laugh.mp3')
    self.sounds['ogre']['impact'] = pygame.mixer.Sound('./assets/sound/enemies/ogre/impact.mp3')
    self.sounds['ogre']['roar'] = pygame.mixer.Sound('./assets/sound/enemies/ogre/roar.ogg')

    # ======= DIFFERENT TEXT BLEEP SOUNDS =======
    for k,_ in self.sounds['text_bleep'].items():
      self.sounds['text_bleep'][k] = pygame.mixer.Sound(f'./assets/sound/text_bleep/bleep{k}.mp3')

    # ======= DIFFERENT ORC DEATH SOUNDS =======
    for k,_ in self.sounds['orc_death_sounds'].items():
      self.sounds['orc_death_sounds'][k] = pygame.mixer.Sound(f'./assets/sound/enemies/orc/death{k}.mp3')

    # ======= DIFFERENT SHADOW DEATH SOUNDS =======
    for k,_ in self.sounds['shadow_death_sounds'].items():
      self.sounds['shadow_death_sounds'][k] = pygame.mixer.Sound(f'./assets/sound/enemies/shadow/death{k}.wav')


  def set_global_sound_volume_to(self, volume: float) -> None:
    for k, sound in self.sounds.items():
      if isinstance(sound, dict):
        for inner_sound in sound.values():

          if k == 'text_bleep':
            inner_sound.set_volume(volume + 0.5)
          elif k == 'arrow':
            inner_sound.set_volume(volume - 0.2)
          else:
            inner_sound.set_volume(volume)

      else:
          # Slight lower volume sound effects
          if k == 'click_1_sound' or k == 'click_3_sound':
            sound.set_volume(volume - 0.29)
          elif k == 'spell_channeling':
            sound.set_volume(volume - 0.15)
          else:
            sound.set_volume(volume)

  def play_bleep_sound(self, play: int) -> None:
    for bleep in self.sounds['text_bleep'].values():
      if play:
        bleep.play()
      else:
        bleep.stop()
        