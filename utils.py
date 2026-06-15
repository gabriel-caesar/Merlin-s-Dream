from __future__ import annotations
from os import path, listdir
import pygame
import pygame_gui
import random
from typing import TYPE_CHECKING
from enemy import Enemy

if TYPE_CHECKING:
  from main import Player
  from sound_manager import SoundManager


# Manages events like damage bubbles in the main.py file
event_manager = []

def run_events(display: pygame.Surface):
  for event in event_manager:
      if event.timer > 0:
        event.timer -= 1

        # Makes the rect move per decimal instead of forcing integers
        event.pos[1] -= event.speed

        event.rect.center = event.pos
        display.blit(event.text_surf, event.rect)
      else:
        event_manager.remove(event)

def get_sprites(main_directory: list, file_prefix: str) -> dict[str, pygame.Surface]:
  base = path.dirname(__file__)
  sprite_path = path.join(base, 'assets', *main_directory)
  files = listdir(sprite_path)

  sheet = {}

  for f  in files:
    if file_prefix in f:
      prop_name = f.split('.png')[0]
      img_path = path.join(sprite_path, f)
      img_surf = pygame.image.load(img_path)
      sheet[prop_name] = img_surf

  return sheet

def filter_dead_from(enemies_list: list[Enemy]) -> None:
  for e in enemies_list:
    if e.vanish_timer <= 0:
      enemies_list.remove(e)

# Shows the enemy hpbar on overlapping the player sprite
def show_enemy_hpbar_onhover(
    map_data: dict,
    mouse_click_area: pygame.Rect,
    enemies_list: list,
    player: Player
) -> None:
  for data in map_data:
    hover_area = data['hover_area']

    if hover_area.colliderect(mouse_click_area):
      for e in enemies_list:
        if e.rect.midbottom == hover_area.center or e.rect.colliderect(mouse_click_area):
          # Show enemy being hovered health bar if there is no target
          if not player.target:
            e.show_hp_bar()


def create_ui_manager(wind_size: tuple) -> pygame_gui.UIManager:
  ui_manager = pygame_gui.UIManager(wind_size, theme_path='./gui_theme.json')
  ui_manager.add_font_paths(
    font_name='avqest',
    regular_path='./font/Avqest-eeel.ttf'
  )
  ui_manager.get_theme().load_theme('gui_theme.json')

  return ui_manager

def run_fragment_map(fragment_list: list, display: pygame.Surface, DISPLAY_SIZE: tuple) -> None:

  for frag in fragment_list:
    if frag.spawn_timer > 0:
      frag.spawn_timer -= 1

    else:
      pygame.draw.rect(display, frag.color, frag.rect)
      frag.rect.y -= frag.speed

      # Move horizontally
      # Keeping a pseudo movement var to increment the movement slowly since
      # pygame.Rect only receives integers to alter its position
      pseudo_frag_mov = frag.x_movement
      pseudo_frag_mov += frag.rect.x + frag.x_movement
      frag.rect.x = int(pseudo_frag_mov)

      # ============== SPAWN FRAGMENT BACK TO THE BOTTOM ==============
      if frag.rect.top <= 0:
        frag.rect.top = DISPLAY_SIZE[1]
        frag.rect.x = random.randint(0, DISPLAY_SIZE[0])

def play_music_theme(vol: float, type: str) -> None:

  if type == 'maintheme':
    pygame.mixer.music.load('./assets/sound/menu_theme.mp3')
  elif type == 'gameplay':
    pygame.mixer.music.load('./assets/sound/gameplay_theme.mp3')
  else: 
    return
  
  pygame.mixer.music.set_volume(vol)
  pygame.mixer.music.play(-1)

def add_n_enemies(
  map_data: list,
  n: int, 
  enemy_group: pygame.sprite.Group,
  enemy_name: str,
  atk_range: int,
  display: pygame.Surface,
  sound_manager: SoundManager,
  wave: int = 1
) -> list:
  
  # Adding different attribute values for different stronger creatures
  match enemy_name:
    case 'orc_axe':
      enemy_strength = 30
      enemy_hp = random.randint(200, 250) + (wave * 2)

    case _: # Default
      enemy_strength = 10
      enemy_hp = random.randint(30,60) + (wave * 2)

  for _ in range(n):
    enemy_group.add(
      Enemy(
        tile=map_data[random.randint(50, 255)], 
        name=enemy_name, 
        hp=enemy_hp,
        atk_range=atk_range,
        display=display,
        wave=wave,
        strength=enemy_strength,
        sound_manager=sound_manager
      )
    )
  
  return enemy_group.sprites()

def check_dead_enemy_for_xp(enemies_list: list[Enemy]) -> int:
  for enemy in enemies_list:
    # Checking the vanish_timer since that number will only occur once,
    # preventing this event to run constantly until enemy disappear
    if not enemy.alive and enemy.vanish_timer == 179:
      return enemy.xp_value
    
def get_merlins_spells_library() -> dict:
  firebolt_surf = pygame.image.load('./assets/ui/fire_bolt_portrait.png')
  firebolt_surf = pygame.transform.scale(firebolt_surf, (20,20))

  tp_surf = pygame.image.load('./assets/ui/tp_portrait.png')
  tp_surf = pygame.transform.scale(tp_surf, (20,20))

  merlins_spells = {
    'fire_bolt': {
      'img_surf': firebolt_surf,
      'name': 'fire_bolt',
      'title': "Fire Bolt",
      'info_text': """<font color='#f2bd29'>Merlin</font> has remembered <font color='#ff0000'>Fire Bolt</font>, a devastating spell whose cooldown is far greater than that of his magic bolt, but whose destructive power is unmatched.<br><br><font color='#f2bd29'>Merlin</font> can recall up to 4 spells during this dream. Fire Bolt is always the first to return to his memory; as the battle rages on, he may recover other powerful incantations once used to vanquish these creatures in ages past.<br><br><font color='#f2bd29'>This spell must be cast using a keyboard key.</font>
      """,
      'cooldown_text': 'Cooldown: 30s'
    },

    'teletransport': {
      'img_surf': tp_surf,
      'name': 'teletransport',
      'title': "Teletransport",
      'info_text': """<font color='#f2bd29'>Merlin</font> remembered <font color='#8528d1'>Teletransport</font>, a rare spell mastered by only a handful of mages. It allows the caster to instantly travel to a target location within range, disappearing and reappearing in the blink of an eye.<br><br><font color='#f2bd29'>This spell must be cast using a keyboard key.</font>
      """,
      'cooldown_text': 'Cooldown: 30s'
    }
  }

  return merlins_spells

def change_cursor_to(state=str) -> tuple:
  match state:
    case 'target':
      image_asset = './assets/cursor/cursor_target.png'
    case 'normal':
      image_asset = './assets/cursor/cursor_white.png'
    case 'attack':
      image_asset = './assets/cursor/cursor_attack.png'
      

  mouse_img = pygame.image.load(image_asset)
  mouse_rect = mouse_img.get_rect()
  mouse_click_area = pygame.Rect(
    mouse_rect.center[0],
    mouse_rect.center[1],
    4,4
  )

  return mouse_img, mouse_rect, mouse_click_area
