import math
import pygame
import pygame_gui
import sys
import random
import utils
import user_interface
import main_menu

from wave_manager import WaveManager
from entity import Entity
from screen_veil import ScreenVeil
from sound_manager import SoundManager
from spell_caster import SpellCaster
from events.damage_bubble import XPBubble, RegenBubble

pygame.mixer.pre_init(44100, -16, 2, 512) 
pygame.init()
pygame.mixer.set_num_channels(64) # Handles more sounds at once
clock = pygame.Clock()

in_main_menu = True
game_paused = False
in_transition = False
info_screen_page = 1
play_text_bleep = False
player_died_game_over = False
keyboard_key = pygame.key.get_pressed()

WINDOW_SIZE = (1280, 720)
DISPLAY_SIZE = (640, 360)
HPBAR_WIDTH = 115
PLAYER_DIED = pygame.USEREVENT + 6 # Fired when player dies to render certain UI elements
GO_TO_MAIN_MENU = pygame.USEREVENT + 7 # When player goes from the gameplay screen to the main menu
WAVE_CHANGED = pygame.USEREVENT + 8 # Fires when waves advance
FADE_IN = pygame.USEREVENT + 9
FADE_OUT = pygame.USEREVENT + 10
LEVEL_UP = pygame.USEREVENT + 11

# Sound manager
sound_manager = SoundManager()
sound_manager.load_sounds()
sound_manager.set_global_sound_volume_to(volume=0.3)

# Global variables
screen = pygame.display.set_mode(WINDOW_SIZE)
display = pygame.Surface(DISPLAY_SIZE)
screen_veil = ScreenVeil(display)
pygame.display.set_caption("Merlin's Dream")
# Plays the main menu theme
utils.play_music_theme(vol=0.3, type='maintheme')

# User Interface Managers
pause_menu_ui_manager = utils.create_ui_manager(DISPLAY_SIZE)
main_menu_manager = utils.create_ui_manager(DISPLAY_SIZE)
game_over_manager = utils.create_ui_manager(DISPLAY_SIZE)
gui_manager = utils.create_ui_manager(DISPLAY_SIZE)
overlay_manager = utils.create_ui_manager(DISPLAY_SIZE)
reading_earned_spell = False

# Main grass tiles
grass_block = pygame.image.load('./grass.png')
grass_rect = grass_block.get_rect()

# Player spritesheets
idle_spritesheet = utils.get_sprites(['player'], 'idle')
running_spritesheet = utils.get_sprites(['player'], 'walk')
backview_running_spritesheet = utils.get_sprites(['player', 'backview'], 'backview_walk')
backview_idle_spritesheet = utils.get_sprites(['player', 'backview'], 'backview_idle')

def load_fresh_game(
  map_data: list,
  gui_elements: dict = None,
  **player_stats
) -> tuple:
  
  fresh_player = Player(
    tile=map_data[0], 
    **player_stats
  )

  # Making sure the game over flag is toggled off
  global player_died_game_over
  player_died_game_over = False
  
  enemiesgroup = pygame.sprite.Group()

  # Adding five enemies to the map for wave 1
  utils.add_n_enemies(
    map_data=map_data, 
    n=random.randint(3, 6), 
    enemy_group=enemiesgroup, 
    enemy_name='orc',
    atk_range=20,
    display=display,
    sound_manager=sound_manager
  )

  enemies_list = enemiesgroup.sprites()

  # Update GUI
  if gui_elements:
    gui_elements['char_info']['level'].set_text(f'Level: {fresh_player.level}')
    gui_elements['char_info']['str'].set_text(f'Strength: {fresh_player.strength}')
    gui_elements['char_info']['int'].set_text(f'Int: {fresh_player.intelligence}')
    gui_elements['char_info']['haste'].set_text(f'Haste: {fresh_player.haste}')
    gui_elements['char_info']['xp'].set_text(f'XP: {fresh_player.xp}/{fresh_player.max_xp}')
    gui_elements['xp_bar'].set_current_progress(0)

  return fresh_player, enemies_list, enemiesgroup


def pause_game(show_pause_menu: bool = True) -> None:
  """Pauses or unpauses the game"""
  global game_paused
  game_paused = not game_paused

  # Toggle the opaque background
  screen_veil.toggle = not screen_veil.toggle

  if game_paused and show_pause_menu:
    pause_menu_elements['panel'].show()
    # Hidding the options from the option tab since showing the
    # main panel makes everything visible inside of it at once
    for option in pause_menu_elements['options'].values():
      option.hide()

  else:
    pause_menu_elements['panel'].hide()

def control_volume_sliders() -> None:
  menu_sound_slider = menu_elements['sound_slider']
  pause_sound_slider = pause_menu_elements['options']['sound_slider']

  menu_music_slider = menu_elements['music_slider']
  pause_music_slider = pause_menu_elements['options']['music_slider']

  sound_val_1 = menu_sound_slider.get_current_value()
  sound_val_2 = pause_sound_slider.get_current_value()

  music_val_1 = menu_music_slider.get_current_value()
  music_val_2 = pause_music_slider.get_current_value()

  if sound_val_1 != sound_val_2:
    
    if game_paused: 
      # It means user changed the slider in the paused menu
      menu_sound_slider.set_current_value(sound_val_2)
      sound_manager.set_global_sound_volume_to(round(sound_val_2 / 100, ndigits=2))

    else:
      pause_sound_slider.set_current_value(sound_val_1)
      sound_manager.set_global_sound_volume_to(round(sound_val_1 / 100, ndigits=2))

  if music_val_1 != music_val_2:
    
    if game_paused: 
      # It means user changed the slider in the paused menu
      menu_music_slider.set_current_value(music_val_2)
      pygame.mixer.music.set_volume(round(music_val_2 / 100, ndigits=2))

    else:
      pause_music_slider.set_current_value(music_val_1)
      pygame.mixer.music.set_volume(round(music_val_1 / 100, ndigits=2))

class Player(Entity):
  def __init__(
    self, 
    tile: dict,
    strength: int = 10,
    intelligence: int = 10,
    haste: int = 5,
    hp: int = 100,
    mana: int = 200,
    level: int = 1,
    xp: int = 0,
    max_xp:int = 100,
  ):
    Entity.__init__(
      self, 
      tile, 
      list(idle_spritesheet.values()),
      strength,
      intelligence,
      haste,
      hp,
      mana,
      level,
      xp,
      max_xp
    )

    # Keeps coherence with the enemy class and prevent errors
    # when calling shared funtions dependent on the entity name
    self.name = 'Merlin'

    # ======== COOLDOWN FONT ========
    self.cd_font = pygame.font.Font('./font/Avqest-eeel.ttf', 20)

    self.disabled_spells = [] # Assists the cooldown timer re-enable the disabled spell on cd

    self.spell_to_be_cast = None # Identifies what spell should be cast 
    self.cursor_state = 'normal' # Helps identify if the user is using a target-spell
    self.spell_caster = SpellCaster(entity=self, display=display, sound_manager=sound_manager)
    self.distance_from_enemy = 0
    self.atk_range = 90
    self.projectiles = []
    self.speed = 0.8
    self.regen_hp_timer = 300
    self.regen_mana_timer = 240
    self.kills = 0
    self.being_targeted_by = [] # Helps with passive regeneration

    # Potions
    self.potions = {
      'mana': 5,
      'health': 5,
      'health_cd': 300,
      'mana_cd': 300,
      'heal_amount': 50,
      'mana_amount': 100
    }

    # ========== PLAYER SPELLS DATA ==========
    self.spells = {
      'magic_bolt': {
        'cooldown': 120, # Placeholder cooldown value
        'cost': 16,
        'dmg': random.randint(self.intelligence - 3, self.intelligence + 3)
      },
      'fire_bolt': {
        'cooldown': 180, # Placeholder cooldown value
        'cost': 30,
        'dmg': 80
      },
      'teletransport': {
        'cooldown': 300, # Placeholder cooldown value
        'cost': 100
      },
      'radial_blast': {
        'cooldown': 600,
        'cost': 200
      },
      'firestorm': {
        'cooldown': 1200,
        'cost': 500
      }
    }

    # ========== PLAYER ACTIVE SPELL COOLDOWNS ==========
    self.active_cooldowns = {
      'magic_bolt': 0, # Defaults to 120
      'fire_bolt': 0, # Defaults to 180
      'teletransport': 0, # Defaults to 300
      'health_potion': 0, # Defaults to 300
      'mana_potion': 0 # Defaults to 300
    }

    # ========== PLAYER CACHE ==========
    self.cache = {
      'hp': self.hp,
      'mana': self.mana,
      'cursor': 'normal'
    }

    # ========== HP BAR GUI ==========
    self.bar_img = pygame.image.load('./assets/ui/player_bar.png')
    self.bar_img.convert_alpha()
    self.bar_img.set_alpha(128)
    self.bar_rect1 = self.bar_img.get_rect(midbottom=(70, 360))
    self.bar_rect2 = self.bar_img.get_rect(midbottom=(570, 360))

    self.hp_bar_filler = pygame.Rect(0,0,HPBAR_WIDTH,27)
    self.hp_bar_filler.midbottom = self.bar_rect1.midbottom
    self.hp_bar_filler.y -= 3

    self.mana_bar_filler = pygame.Rect(0,0,HPBAR_WIDTH,27)
    self.mana_bar_filler.midbottom = self.bar_rect2.midbottom
    self.mana_bar_filler.y -= 3

  def reset_ui_properties(self) -> None:
    # Reseting the health potions count
    hp_potion_count = gui_elements['health_potion_count']
    hp_potion_count.set_text(str(self.potions['health']))

    # Reseting the mana potions count
    mana_potion_count = gui_elements['mana_potion_count']
    mana_potion_count.set_text(str(self.potions['mana']))

    # Hides away spells learned in the previous gameplay
    for spell_name, element in gui_elements['portraits'].items():
      if spell_name != 'magic_bolt' and 'potion' not in spell_name:
        element.hide()

  def consume_potion(self, type: str) -> None:
    if self.potions[type] and self.active_cooldowns[f'{type}_potion'] <= 0:

      # Updating the UI
      potion_name = type + '_potion_count'
      ui_potion_count = gui_elements[potion_name]

      if self.potions[type] - 1 > 0:
        self.potions[type] -= 1
      else:
        self.potions[type] = 0

      # Update the player health or mana accordingly
      if type == 'health':
        amount = self.potions['heal_amount']
        bb_color = '#21ff29'
        points_gained = self.heal(amount)

      else:
        amount = self.potions['mana_amount']
        bb_color = "#397eff"
        points_gained = self.gain_mana(amount)

      # Points gained is the actual amount of HP/Mana restored,
      # which may be lower than the potion's value if the player
      # is close to their maximum HP/Mana.
      regen_bb = RegenBubble(
        value=f'+{points_gained}',
        color=bb_color,
        size=14,
        pos=self.rect.center
      )

      # Manager to render all events
      utils.event_manager.append(regen_bb)

      # Play sound effect
      sound_manager.sounds['potion'].play()

      # Setting the new text to the count label
      ui_potion_count.set_text(str(self.potions[type]))

      # Start a new cooldown
      self.active_cooldowns[f'{type}_potion'] = self.potions[f'{type}_cd']

  def calculate_current_bar_width(self, type: str) -> None:
    if type == 'hp':
      curr_width = (self.hp * HPBAR_WIDTH) / self.max_hp # Regra de 3
      self.hp_bar_filler.width = curr_width
    elif type == 'mana':
      curr_width = (self.mana * HPBAR_WIDTH) / self.max_mana # Regra de 3
      self.mana_bar_filler.width = curr_width

  def update_cooldown_data(self, display: pygame.Surface) -> None:
    for spell, cd in self.active_cooldowns.items():

      # Making sure this cooldown data update runs only when on gameplay
      if cd > 0 and not reading_earned_spell and not game_paused:
        # Updating the backend spell cooldown
        self.active_cooldowns[spell] -= 1
        cd_in_seconds = int(self.active_cooldowns[spell] / 60)

        timer_text = self.cd_font.render(str(cd_in_seconds), True, '#f2bd29')
        timer_rect = gui_elements['cooldown_timer'][spell]

        bg_surf = pygame.Surface((18,22))
        bg_surf.fill(color="#272f35")
        bg_surf.set_alpha(200)

        bg_timer_rect = gui_elements['cooldown_timer'][spell].copy()
        bg_timer_rect.x -= 1
        bg_timer_rect.y += 1
        
        # Disable the spell button
        gui_elements['portraits'][spell].disable()

        # Helps the code knows when to enable the button back again
        if spell not in self.disabled_spells and self.active_cooldowns[spell] > 0:
          self.disabled_spells.append(spell)

        display.blit(bg_surf, bg_timer_rect)
        display.blit(timer_text, timer_rect)

      if spell in self.disabled_spells and self.active_cooldowns[spell] <= 0:
        gui_elements['portraits'][spell].enable()
        self.disabled_spells.remove(spell)
    
  def run_animation(self, display: pygame.Surface) -> None:
    if self.destination_tile:
      if self.facing == 'backview':
        self.animation_frames = list(backview_running_spritesheet.values())

      else:
        self.animation_frames = list(running_spritesheet.values())

    else:
      if self.facing == 'backview':
        self.animation_frames = list(backview_idle_spritesheet.values())
      else:
        self.animation_frames = list(idle_spritesheet.values())

    self.animation_index += 0.1
    if self.animation_index > len(self.animation_frames):
      self.animation_index = 0

    # ================ RENDERING THE CORRECT IMAGE IF THE PLAYER IS DEAD OR ALIVE ================
    if self.alive:
      self.image = self.animation_frames[int(self.animation_index)]
    else:
      blood_indicator = pygame.image.load('./assets/cursor/blood_indicator.png')
      display.blit(blood_indicator, (self.rect.x - 5, self.rect.y + 12))
      self.image = pygame.image.load('./assets/player/dead.png')

    self.image = pygame.transform.flip(self.image, self.flip, False)

  def cast_spell(self, name: str) -> None:
    if name == 'fire_bolt':
      self.spell_caster.cast_firebolt(spell_data=self.spells['fire_bolt'])
    elif name == 'teletransport':
      self.spell_caster.cast_teletransport(
        to=mouse_click_area,
        spell_data=self.spells['teletransport']
      )
    elif name == 'magic_bolt':
      self.spell_caster.cast_magicbolt(spell_data=self.spells['magic_bolt'])


  def regenerate(self, type: str) -> None:
    if type == 'hp':
      if self.hp < self.max_hp:
        if self.regen_hp_timer == 0:
          amount = random.randint(self.strength - 6, self.strength)
          self.heal(amount)
          self.regen_hp_timer = 300
        else:
          self.regen_hp_timer -= 1

    elif type == 'mana':
      if self.mana < self.max_mana:
        if self.regen_mana_timer == 0:
          amount = random.randint(self.intelligence, self.intelligence + 6)
          self.gain_mana(amount)
          self.regen_mana_timer = 240
        else:
          self.regen_mana_timer -= 1

  def heal(self, amount: int) -> int:

    if self.hp + amount > self.max_hp:
      final_healed_amount = self.max_hp - self.hp
      self.hp = self.max_hp
    else:
      self.hp += amount
      final_healed_amount = amount

    self.calculate_current_bar_width('hp')
    return final_healed_amount

  def gain_mana(self, amount: int) -> int:
    if self.mana + amount > self.max_mana:
      final_mana_gained = self.max_mana - self.mana
      self.mana = self.max_mana
    else:
      self.mana += amount
      final_mana_gained = amount

    self.calculate_current_bar_width('mana')
    return final_mana_gained

  def use_mana(self, amount: int) -> None:
    if self.mana - amount < 0:
      self.mana = 0
    else:
      self.mana -= amount

    self.calculate_current_bar_width('mana')

  def auto_attack(self) -> None:
    self.cast_spell(name='magic_bolt')

  def update_spell_cooldowns(self) -> None:
    # Decrease the cooldown of spells as the user levels up
    for spell in self.spells.values():
      spell['cooldown'] -= self.level * 2
  
  def populate_earned_spell_screen(self, spell: dict) -> None:
    # Populate the reading spell panel dynamically
    overlay_elements['img_container'].set_background_images([spell['img_surf']])
    overlay_elements['label'].set_text(spell['title'])
    overlay_elements['text'].set_text(html_text=spell['info_text'])
    overlay_elements['text'].set_active_effect( # Typing effect
      effect_type=pygame_gui.TEXT_EFFECT_TYPING_APPEAR,
      params={'time_per_letter': 0.03}
    )
    gui_elements['portraits'][spell['name']].show() # Reveal spell portrait

  def update_stats_upon_lvlup(self) -> None:
    # Update backend values
    self.level += 1
    self.max_xp = self.max_xp * 2
    self.strength = self.strength + self.level * 3
    self.intelligence = self.intelligence + self.level * 3
    self.haste = self.haste + self.level
    self.max_hp = self.max_hp + self.level * 2
    self.hp = self.max_hp
    self.max_mana = self.max_mana + self.level * 2 + self.intelligence
    self.mana = self.max_mana

    # Update the spell cooldowns and the number displayed on the spell infos
    self.update_spell_cooldowns()

    # Update the mana and hp bar upon lvl up
    self.calculate_current_bar_width(type='hp')
    self.calculate_current_bar_width(type='mana')

    # Update GUI
    gui_elements['char_info']['level'].set_text(f'Level: {self.level}')
    gui_elements['char_info']['str'].set_text(f'Strength: {self.strength}')
    gui_elements['char_info']['int'].set_text(f'Int: {self.intelligence}')
    gui_elements['char_info']['haste'].set_text(f'Haste: {self.haste}')
    gui_elements['char_info']['xp'].set_text(f'XP: {self.xp}/{self.max_xp}')

  def update_points(self, type: str, amount: int) -> int:
    if type == 'xp':
      if self.xp + amount >= self.max_xp:
        # Level up condition
        carry_over = (self.xp + amount) - self.max_xp
        self.xp = carry_over
        self.update_stats_upon_lvlup()
        pygame.event.post(pygame.event.Event(LEVEL_UP))
        return 1
      else:
        self.xp += amount
        return 0

  def check_distance_from_enemy(self):
    # Finding the Euclidean distance between player and enemy
    dt_x = player.rect.x - player.target[1].rect.x
    dt_y = player.rect.y - player.target[1].rect.y
    player.distance_from_enemy = math.sqrt((dt_x) ** 2 + (dt_y) ** 2)

  def update(self, display: pygame.Surface, game_paused: bool) -> None:
    if not game_paused:
      self.run_animation(display)

      # If there are projectiles to load, render and handle them
      self.handle_projectiles(display, self.projectiles)

      if self.alive:
        if self.target:
          self.check_distance_from_enemy()
          self.auto_attack()
          t = self.target[1].rect
          display.blit(target_indicator_img, (t.x - 5, t.y + 11))

        if not self.target and not self.being_targeted_by:
          self.regenerate('hp')
          self.regenerate('mana')

        if self.destination_tile:
          self.move()      

        xp_earned = utils.check_dead_enemy_for_xp(enemies_list)
        if xp_earned:
          # Update kill count
          self.kills += 1
          gui_elements['char_info']['kills'].set_text(f'Kills: {self.kills}')

          # Update xp based on xp earned
          leveled_up = self.update_points(type='xp', amount=xp_earned)

          # Create a experience bubble
          xp_bb = XPBubble(
            value=f'+{xp_earned}XP' if not leveled_up else f'LEVEL UP',
            color="#a600ff",
            size=14,
            pos=self.rect.center
          )
          utils.event_manager.append(xp_bb)

          if leveled_up:
            sound_manager.sounds['level_up'].play()

          # Update the xp progress bar
          xp_percentage = self.xp / self.max_xp
          gui_elements['xp_bar'].set_current_progress(xp_percentage)

          # Update the xp numbers from the character info panel
          gui_elements['char_info']['xp'].set_text(f'XP: {player.xp}/{player.max_xp}')

      
      else:
        if self.vanish_timer > 0:
          self.vanish_timer -= 1
          if self.vanish_timer == 1:
            # Making sure the program posts this event only once
            pygame.event.post(pygame.event.Event(PLAYER_DIED))

  def draw(self, display: pygame.Surface) -> None:
    display.blit(self.image, self.rect)
    self.run_hit_animation(display)
    
# Rendering measurements
HALF_TILE = grass_rect.width / 2
TILE_SURFACE_OFFSET = 8

class BackgroundFragment:
  def __init__(self):
    n1 = random.randint(2, 4)
    n2 = n1

    self.speed = 0.1
    self.rect = pygame.Rect(0, 0, n1, n2)
    self.rect.x = random.randint(0, DISPLAY_SIZE[0])
    self.rect.y = DISPLAY_SIZE[1]
    self.color = random.choice(['#c9c9c9', "#130c4752", "#5a87b7"])
    self.x_movement = random.choice([0.1, -0.1, 0.5, -0.5, 0])  
    self.spawn_timer = random.randint(15, 500)

fragment_map = []

for i in range(100):
  fragment = BackgroundFragment()
  fragment_map.append(fragment)

map_data = []

for x in range(16):
  for y in range(16):
    tile_data = {}

    tile_rect = grass_rect.copy()
    tile_rect.x = 320 + (x - y) * HALF_TILE # Grows left-down
    tile_rect.y = 30 + (x + y) * TILE_SURFACE_OFFSET # Grows right-down

    hover_area = pygame.Rect(0, 0, 13, 10)
    hover_area.center = (
      tile_rect.x + (tile_rect.width / 2), 
      tile_rect.y + ((tile_rect.height / 2) - 9)
    )

    tile_data['tile'] = tile_rect
    tile_data['hover_area'] = hover_area
    tile_data['index'] = [x, y]

    map_data.append(tile_data)

player, enemies_list, enemiesgroup = load_fresh_game(map_data=map_data, intelligence=200)



# ================ GAME USER INTERFACE ================
# load_gui function creates and isolates all GUI elements
# used in the game in a single file to provide a more readable 
# code and a organized programming environment
gui_elements = user_interface.load_gui(gui_manager, player)
info_screen_elements = user_interface.load_info_screen(pause_menu_ui_manager)
pause_menu_elements = user_interface.load_pause_menu(pause_menu_ui_manager)
menu_elements = user_interface.load_menu_elements(main_menu_manager)
game_over_elements = user_interface.load_game_over_elements(game_over_manager)
overlay_elements = user_interface.load_overlay_elements(overlay_manager)

# Cursor related surfaces
mouse_img = pygame.image.load('./assets/cursor/cursor_white.png')
mouse_rect = mouse_img.get_rect()
mouse_click_area = pygame.Rect(mouse_rect.left, mouse_rect.top, 4, 4)
map_indicator_img = pygame.image.load('./assets/cursor/map_indicator_white.png')
attack_indicator_img = pygame.image.load('./assets/cursor/attack_indicator.png')
target_indicator_img = pygame.image.load('./assets/cursor/target_indicator.png')
pygame.mouse.set_visible(False)

# UI element hover visibility flags
show_hovered_window = None

# Update the player potion count 
gui_elements['health_potion_count'].set_text(str(player.potions['health']))
gui_elements['mana_potion_count'].set_text(str(player.potions['mana']))

# Wave manager
wave_manager = WaveManager(
  map_data=map_data, 
  enemies_list=enemies_list,
  gui_elements=gui_elements,
  pause_menu_elements=pause_menu_elements,
  screen_veil=screen_veil,
  sound_manager=sound_manager
)
    
while True:
  dt = clock.tick(60) / 1000
  mouse_b1, _, mouse_b3 = pygame.mouse.get_pressed()
  mousex, mousey = pygame.mouse.get_pos()
  mouse_rect.topleft = pygame.mouse.get_pos()

  display.fill("#080025")

  control_volume_sliders()
  
  if in_main_menu:
    # Loads the main menu screen and returns a boolean value to 
    # control if the player is in the main menu or otherwise 
    in_main_menu = main_menu.load(
      menu_manager=main_menu_manager, 
      delta=dt,
      display=display,
      fragment_list=fragment_map,
      menu_elements=menu_elements,
      sound_manager=sound_manager
    )

    if not in_main_menu:
      in_transition = True
      pygame.event.post(pygame.event.Event(FADE_IN))

  elif in_transition:      
    bleep_index = random.randint(0,2)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == FADE_IN:
        screen_veil.fade = 'in'
        info_screen_elements['main_panel'].show()

        # Play text bleep sound in a loop
        # Index randoms through three different options of bleep sounds
        sound_manager.sounds['text_bleep'][str(bleep_index)].play(-1)

        info_screen_elements['main_text'].set_active_effect(
          effect_type=pygame_gui.TEXT_EFFECT_TYPING_APPEAR,
          params={'time_per_letter': 0.03}
        )

      if event.type == FADE_OUT:
        screen_veil.fade = 'out'
        in_transition = False
        info_screen_elements['main_panel'].hide()
        info_screen_elements['main_text'].clear_all_active_effects()

      if event.type == pygame_gui.UI_TEXT_EFFECT_FINISHED:
        # Stop the text bleep sound loop
        sound_manager.play_bleep_sound(play=0)

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          sound_manager.sounds['button_click_2'].play()

          # Change page to read more about the game
          if info_screen_page >= 1 and info_screen_page < 3:
            info_screen_page += 1 # Turn the page

            # Applying different text to different pages
            if info_screen_page == 2:
              info_screen_elements['main_text'].set_text("""<font color='#f2bd29'>Instructions:</font><br><br>- Right-click with the mouse to <font color='#f2bd29'>guide</font> Merlin across the dreamscape. <br><br>- <font color='#ff0000'>Attack</font> enemies by right-clicking upon your chosen target.""")

            elif info_screen_page == 3:
              info_screen_elements['main_text'].set_text("""<font color='#f2bd29'>Instructions:</font><br>- <font color='#f2bd29'>Merlin's</font> basic attack is an enchanted <font color='#f2bd29'>Magic Bolt</font>, cast automatically against foes within range. <br><br>- Gain levels to recover <font color='#f2bd29'>forgotten spells</font>, fragments of magic once mastered by the ancient wizard. <br><br>""")

            # Run typing effect
            info_screen_elements['main_text'].set_active_effect(
              effect_type=pygame_gui.TEXT_EFFECT_TYPING_APPEAR,
              params={'time_per_letter': 0.03}
            )
            # Stop all bleeping sounds if any
            sound_manager.play_bleep_sound(play=0)
            # Play text bleep sound in a loop
            # Index randoms through three different options of bleep sounds
            sound_manager.sounds['text_bleep'][str(bleep_index)].play(-1)

          else:
            sound_manager.play_bleep_sound(play=0)
            pygame.event.post(pygame.event.Event(FADE_OUT))

      pause_menu_ui_manager.process_events(event)

    pause_menu_ui_manager.update(dt)
    screen_veil.update()
    # Pause and Game Over menu UI manager is drawed one layer above the screen veil
    pause_menu_ui_manager.draw_ui(display)
  
  else:

    # ================ UPDATING ENEMIES LIST PER WAVE ================

    if not enemies_list:
      enemies_list = wave_manager.enemies_list

    # ================ HOVERING PANELS ================
  
    if not game_paused:
      if show_hovered_window == 'char_info':
        gui_elements['char_info_panel'].show()

      elif show_hovered_window == 'magic_bolt_info':
        gui_elements['spells_info']['magic_bolt'].show()
        gui_elements['cooldown_text']['magic_bolt'].show()

      elif show_hovered_window == 'fire_bolt_info':
        gui_elements['spells_info']['fire_bolt'].show()
        gui_elements['cooldown_text']['fire_bolt'].show()

      elif show_hovered_window == 'tp_info':
        gui_elements['spells_info']['teletransport'].show()
        gui_elements['cooldown_text']['teletransport'].show()

      elif show_hovered_window == 'radial_blast_info':
        gui_elements['spells_info']['radial_blast'].show()
        gui_elements['cooldown_text']['radial_blast'].show()

      elif show_hovered_window == 'firestorm_info':
        gui_elements['spells_info']['firestorm'].show()
        gui_elements['cooldown_text']['firestorm'].show()

      else:
        for info in gui_elements['spells_info'].values():
          info.hide()

        for cd in gui_elements['cooldown_text'].values():
          cd.hide()

        gui_elements['char_info_panel'].hide()

    char_info_panel_hovered = gui_elements['char_info_panel'].get_abs_rect().collidepoint(mouse_click_area.center)
    char_info_button_hovered = gui_elements['char_info_button'].hover_point(mouse_click_area.x, mouse_click_area.y)

    magic_bolt_hovered = gui_elements['portraits']['magic_bolt'].hover_point(
      mouse_click_area.x, 
      mouse_click_area.y
    )
    magic_bolt_info_hovered = gui_elements['spells_info']['magic_bolt'].get_abs_rect().collidepoint(
      mouse_click_area.center
    )

    fire_bolt_hovered = gui_elements['portraits']['fire_bolt'].hover_point(
      mouse_click_area.x, 
      mouse_click_area.y
    )
    fire_bolt_info_hovered = gui_elements['spells_info']['fire_bolt'].get_abs_rect().collidepoint(
      mouse_click_area.center
    )

    tp_hovered = gui_elements['portraits']['teletransport'].hover_point(
      mouse_click_area.x, 
      mouse_click_area.y
    )
    tp_info_hovered = gui_elements['spells_info']['teletransport'].get_abs_rect().collidepoint(
      mouse_click_area.center
    )

    radial_blast_hovered = gui_elements['portraits']['radial_blast'].hover_point(
      mouse_click_area.x, 
      mouse_click_area.y
    )
    radial_blast_info_hovered = gui_elements['spells_info']['radial_blast'].get_abs_rect().collidepoint(
      mouse_click_area.center
    )

    firestorm_hovered = gui_elements['portraits']['firestorm'].hover_point(
      mouse_click_area.x, 
      mouse_click_area.y
    )
    firestorm_info_hovered = gui_elements['spells_info']['firestorm'].get_abs_rect().collidepoint(
      mouse_click_area.center
    )

    if char_info_button_hovered or (char_info_panel_hovered and gui_elements['char_info_panel'].visible):
      show_hovered_window = 'char_info'

    elif magic_bolt_hovered or (magic_bolt_info_hovered and gui_elements['spells_info']['magic_bolt'].visible):
      show_hovered_window = 'magic_bolt_info'

    elif (
      (fire_bolt_hovered and gui_elements['portraits']['fire_bolt'].visible)
      or 
      (fire_bolt_info_hovered and gui_elements['spells_info']['fire_bolt'].visible)
    ):
      show_hovered_window = 'fire_bolt_info'

    elif (
      (tp_hovered and gui_elements['portraits']['teletransport'].visible)
      or 
      (tp_info_hovered and gui_elements['spells_info']['teletransport'].visible)
    ):
      show_hovered_window = 'tp_info'
      
    elif (
      (radial_blast_hovered and gui_elements['portraits']['radial_blast'].visible)
      or 
      (radial_blast_info_hovered and gui_elements['spells_info']['radial_blast'].visible)
    ):
      show_hovered_window = 'radial_blast_info'

    elif (
      (firestorm_hovered and gui_elements['portraits']['firestorm'].visible)
      or 
      (firestorm_info_hovered and gui_elements['spells_info']['firestorm'].visible)
    ):
      show_hovered_window = 'firestorm_info'

    else:
      show_hovered_window = None
    
    
    # ================ CACHE HANDLING LOOP ================

    if player.cache['hp'] != player.hp:
      gui_elements['player_hp_label'].set_text(text=f'Health: {player.hp}/{player.max_hp}')
      player.cache['hp'] = player.hp
      player.calculate_current_bar_width(type='hp')

    if player.cache['mana'] != player.mana:
      gui_elements['player_mana_label'].set_text(text=f'Mana: {player.mana}/{player.max_mana}')
      player.cache['mana'] = player.mana
      player.calculate_current_bar_width(type='mana')
    
    if player.cursor_state != player.cache['cursor']:
      mouse_img, mouse_rect, mouse_click_area = utils.change_cursor_to(player.cursor_state)
      player.cache['cursor'] = player.cursor_state
      
      # Avoids a subtle bug where the cursor image blinks at 
      # the (0,0) position of the screen before going back to 
      # where it was suppose to be
      mouse_rect.topleft = pygame.mouse.get_pos()

    # ================ BACKGROUND MOVING FRAGMENTS ================

    utils.run_fragment_map(fragment_map, display, DISPLAY_SIZE)

    # ================ MAP TILE RENDERING ================

    for data in map_data:
      tile = data['tile']
      hover_area = data['hover_area']

      display.blit(grass_block, (tile.x, tile.y))
      # Uncomment to visualize the tile hover area
      # pygame.draw.rect(display, '#ff0000', hover_area, 1)

      if hover_area.colliderect(mouse_click_area):

        if enemies_list:
          enemy_hovered = False

          for e in enemies_list:

              # If either the cursor hovers on top of the tile
              # that the enemy is standing on top of or if the enemy
              # itself gets hovered, toggle the enemy_hovered variable
              if (
                e.rect.midbottom == hover_area.center or
                mouse_click_area.colliderect(e.rect)
              ):
                  enemy_hovered = True
                  break

          if enemy_hovered:
              display.blit(attack_indicator_img, (tile.x, tile.y))

              if player.cursor_state != 'target': # Making sure the cursor is not in a target state
                  player.cursor_state = 'attack'
          else:
              display.blit(map_indicator_img, (tile.x, tile.y))

              if player.cursor_state != 'target': # Making sure the cursor is not in a target state
                  player.cursor_state = 'normal'

        else:
          display.blit(map_indicator_img, (tile.x, tile.y))

    # ================ KEYBOARD EVENT LOOP ================

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == PLAYER_DIED:
        game_over_elements['main_panel'].show()
        screen_veil.toggle = not screen_veil.toggle

      if event.type == GO_TO_MAIN_MENU:

        # Set the info screen pages to 1
        info_screen_page = 1

        # Reset the first page content to the default text
        info_screen_elements['main_text'].set_text("""<font color='#f2bd29'>Merlin</font> is ensnared within his own dream, forced to battle the creatures that haunted his past adventures. Your task is to keep the old mage alive for as long as possible, lest he perish within the realm of sleep itself. Face endless waves of foes from distant lands and dark domains.""")
        
        # When player goes from the gameplay screen to the main menu
        if game_over_elements['main_panel'].visible:
          game_over_elements['main_panel'].hide()
          
        wave_manager.current_wave = 1

        # If the player goes to the main menu manually from the pause menu screen
        if game_paused:
          pause_game()
        else:
          screen_veil.toggle = not screen_veil.toggle

        player, enemies_list, enemiesgroup = load_fresh_game(map_data, gui_elements)

        # Clear learned spells from previous gameplay
        # Reset used potions
        player.reset_ui_properties()

        # Update the player hp and mana bar label values
        gui_elements['player_hp_label'].set_text(text=f'Health: {player.hp}/{player.max_hp}')
        gui_elements['player_mana_label'].set_text(text=f'Mana: {player.mana}/{player.max_mana}')
        
        utils.play_music_theme(vol=0.3, type='maintheme') # Plays the main menu music theme

        # Flag that makes the main menu render
        in_main_menu = True

      if event.type == LEVEL_UP:
        bleep_index = random.randint(0,2)
        spells = utils.get_merlins_spells_library()
        # Show the reading spell panel

        if player.level == 2:
          overlay_elements['panel'].show()

          pause_game(show_pause_menu=False) # Pauses the game

          # Prevents faulty pause menu behaviors when reading the new spell
          reading_earned_spell = True 
          sound_manager.sounds['text_bleep'][str(bleep_index)].play(-1)

          # Learn the new spell on the backend
          player.learned_spells.append('firestorm')

          # Load the earned spell screen
          player.populate_earned_spell_screen(spells['firestorm'])

        elif player.level == 3:
          overlay_elements['panel'].show()

          pause_game(show_pause_menu=False) # Pauses the game

          # Prevents faulty pause menu behaviors when reading the new spell
          reading_earned_spell = True 
          sound_manager.sounds['text_bleep'][str(bleep_index)].play(-1)

          # Learn the new spell on the backend
          player.learned_spells.append('radial_blast')

          # Load the earned spell screen
          player.populate_earned_spell_screen(spells['radial_blast'])


        elif player.level == 4:
          overlay_elements['panel'].show()

          pause_game(show_pause_menu=False) # Pauses the game

          # Prevents faulty pause menu behaviors when reading the new spell
          reading_earned_spell = True 
          sound_manager.sounds['text_bleep'][str(bleep_index)].play(-1)

          # Learn the new spell on the backend
          player.learned_spells.append('fire_bolt')

          # Load the earned spell screen
          player.populate_earned_spell_screen(spells['fire_bolt'])

        elif player.level == 5:
          overlay_elements['panel'].show()

          pause_game(show_pause_menu=False) # Pauses the game

          # Prevents faulty pause menu behaviors when reading the new spell
          reading_earned_spell = True 
          sound_manager.sounds['text_bleep'][str(bleep_index)].play(-1)

          # Learn the new spell on the backend 
          player.learned_spells.append('teletransport')

          # Load the earned spell screen
          player.populate_earned_spell_screen(spells['teletransport'])

        

      if event.type == pygame_gui.UI_TEXT_EFFECT_FINISHED:
        # Stop the text bleep sound loop
        sound_manager.play_bleep_sound(play=0)

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE and player.alive:
          pause_game(show_pause_menu=False if reading_earned_spell else True)
          
          # If player is in the new spell learned screen while
          # clicking ESC, then hide the spell screen, unpause the
          # game and toggle the reading_earned_spell variable to False
          if reading_earned_spell:
            # Play button sound
            sound_manager.sounds['button_click_2'].play()
            # Stop text bleeping
            sound_manager.play_bleep_sound(play=0)
            overlay_elements['panel'].hide()
            reading_earned_spell = False

          sound_manager.sounds['button_click'].play()

        if event.key == pygame.K_q:
          player.consume_potion('health')
          gui_elements['keys']['Q'].select()

        if event.key == pygame.K_e:
          player.consume_potion('mana')
          gui_elements['keys']['E'].select()

        if event.key == pygame.K_1:
          if 'fire_bolt' in player.learned_spells:
            player.cast_spell('fire_bolt')
            gui_elements['keys']['1'].select() # Run click animation
            gui_elements['portraits']['fire_bolt'].select() # Run click animation

        if event.key == pygame.K_2:
          if 'teletransport' in player.learned_spells:
            gui_elements['keys']['2'].select() # Run click animation
            gui_elements['portraits']['teletransport'].select() # Run click animation
            tp_cost = player.spells['teletransport']['cost']

            # Telling the program to execute the teletransport 
            # spell when player.spell_cast() is called
            player.spell_to_be_cast = 'teletransport'

            # Switching the cursor image to target
            player.cursor_state = 'target'

        if event.key == pygame.K_3:
          if 'radial_blast' in player.learned_spells:
            player.cast_spell('radial_blast')
            gui_elements['keys']['3'].select() # Run click animation
            gui_elements['portraits']['radial_blast'].select() # Run click animation

        if event.key == pygame.K_4:
          if 'firestorm' in player.learned_spells:
            player.cast_spell('firestorm')
            gui_elements['keys']['4'].select() # Run click animation
            gui_elements['portraits']['firestorm'].select() # Run click animation

      if event.type == pygame.KEYUP:
          if event.key == pygame.K_1:
            if 'fire_bolt' in player.learned_spells:
              gui_elements['keys']['1'].unselect() # Run click animation
              gui_elements['portraits']['fire_bolt'].unselect() # Run click animation

          if event.key == pygame.K_2:
            if 'teletransport' in player.learned_spells:
              gui_elements['keys']['2'].unselect() # Run click animation
              gui_elements['portraits']['teletransport'].unselect() # Run click animation

          if event.key == pygame.K_3:
            if 'radial_blast' in player.learned_spells:
              gui_elements['keys']['3'].unselect() # Run click animation
              gui_elements['portraits']['radial_blast'].unselect() # Run click animation

          if event.key == pygame.K_4:
            if 'firestorm' in player.learned_spells:
              gui_elements['keys']['4'].unselect() # Run click animation
              gui_elements['portraits']['firestorm'].unselect() # Run click animation
          
          if event.key == pygame.K_q:
            gui_elements['keys']['Q'].unselect()

          if event.key == pygame.K_e:
            gui_elements['keys']['E'].unselect()


      if event.type == pygame.MOUSEBUTTONDOWN:
        for data in map_data:
          tile = data['tile']
          hover_area = data['hover_area']
  
          # Checking if the tile clicked was a target to attack
          if event.button == 3:
            
            # If the player is trying to move while with the
            # target cursor, change it
            if player.cursor_state == 'target':
              player.cursor_state = 'normal'

            # Variable to prevent moving to the targeted tile
            enemy_found = False

            if hover_area.colliderect(mouse_click_area):
              for e in enemies_list:
                if e.alive: # Only alive creatures are targetable
                  if e.rect.midbottom == hover_area.center or e.rect.colliderect(mouse_click_area):
                    player.target = [data, e]
                    enemy_found = True
                    sound_manager.sounds['click_3_sound'].play() # Play sound
                    break

              if not enemy_found:
                player.destination_tile = data

              # Change character facing direction based on destination
              if player.rect.y > data['hover_area'].y:
                player.facing = 'backview'
              else:
                player.facing = 'front'

              # Flip the character horizontally accordingly
              player.flip = True if player.rect.x > data['hover_area'].x else False

          # Unselect targeted enemy
          if event.button == 1:
            # Play clicking sound
            sound_manager.sounds['click_1_sound'].play()

            # It can be any target spell chosen from the spell panel
            if (player.spell_to_be_cast):
              player.cast_spell(name=player.spell_to_be_cast)
              player.spell_to_be_cast = None

            if player.cursor_state == 'target':
              player.cursor_state = 'normal'

            for e in enemies_list:
              if e.rect.midbottom != hover_area.center:
                player.target = []

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == gui_elements['settings_button'] and player.alive:
          pause_game()
          sound_manager.sounds['button_click'].play()

        if (
          event.ui_element == pause_menu_elements['main_menu_button'] or
          event.ui_element == game_over_elements['main_menu_button']
        ):
          pygame.event.post(pygame.event.Event(GO_TO_MAIN_MENU))
          sound_manager.sounds['button_click'].play()

        if event.ui_element == pause_menu_elements['options_button']:
          sound_manager.sounds['button_click'].play() # Play button sound

          # Hide main tab buttons
          pause_menu_elements['main_menu_button'].hide()
          pause_menu_elements['quit_button'].hide()
          pause_menu_elements['options_button'].hide()

          # Show options tab buttons
          for option in pause_menu_elements['options'].values():
            option.rebuild()
            option.show()

        if event.ui_element == pause_menu_elements['options']['back_button']:
          sound_manager.sounds['button_click'].play() # Play button sound

          # Show main tab buttons
          pause_menu_elements['main_menu_button'].show()
          pause_menu_elements['quit_button'].show()
          pause_menu_elements['options_button'].show()

          # Hide options tab buttons
          for option in pause_menu_elements['options'].values():
            option.hide()

        if event.ui_element == overlay_elements['close_btn']:
          pause_game(show_pause_menu=False if reading_earned_spell else True)

          # If player is in the new spell learned screen while
          # clicking ESC, then hide the spell screen, unpause the
          # game and toggle the reading_earned_spell variable to False
          if reading_earned_spell:
            # Play button sound
            sound_manager.sounds['button_click_2'].play()
            # Stoping all bleeping sounds
            sound_manager.play_bleep_sound(play=0)
            overlay_elements['panel'].hide()
            reading_earned_spell = False

          sound_manager.sounds['button_click'].play()

        if (
          event.ui_element == gui_elements['portraits']['fire_bolt'] or
          event.ui_element == gui_elements['keys']['1']
        ):
          player.cast_spell('fire_bolt')

        if (
          event.ui_element == pause_menu_elements['quit_button'] or
          event.ui_element == game_over_elements['quit_button']
        ):
          sound_manager.sounds['button_click'].play()
          pygame.quit()
          sys.exit()

      gui_manager.process_events(event)
      overlay_manager.process_events(event)
      pause_menu_ui_manager.process_events(event)
      game_over_manager.process_events(event)
  
    # UI manager update function calls
    gui_manager.update(dt)
    overlay_manager.update(dt)
    pause_menu_ui_manager.update(dt)
    game_over_manager.update(dt)

    # Player essentials
    player.update(display, game_paused)
    player_died_game_over = player.is_dead()

    # Triggers the vanish_timer inside player.update()
    if player_died_game_over and player.alive:
      player.alive = False # Avoids re-loop


    # =================== LAYERING ===================
    # Here you can see run_hit_animation(), player.draw(), show_eney_hpbar_onhover()
    # and multiple other rendering functions because here I try to solve the render
    # layering issue where I rearrange stuff to be layered properly on top of themselves.
    # Some GUI managers are spread around here as well to solve the same issue (specially with the screen veil).

    # Draw dead player behind the enemy layers
    if not player.alive:
      player.draw(display)

    # Enemy essentials
    enemiesgroup.update(map_data, player, game_paused)

    # Drawing player on top of every enemy graphical layer if it is alive
    if player.alive:
      player.draw(display)

    utils.filter_dead_from(enemies_list)
    utils.show_enemy_hpbar_onhover(
      map_data,
      mouse_click_area,
      enemies_list,
      player
    )

    player.run_hit_animation(display)

    for e in enemies_list:
      e.run_hit_animation(display)

    # Wave manager essentials
    wave_manager.update(enemies_group=enemiesgroup, display=display)

    # If the player has a target, show its health bar
    if player.target and player.target[1].hp > 0:
      player.target[1].show_hp_bar()

    # ================ BUBBLE EVENTS MANAGER LOOP ================
    utils.run_events(display) # Bubbles like damage and xp feedback

    # ================ DRAWING MAIN ELEMENTS LIKE THE SPELL PANEL ================
    gui_manager.draw_ui(display)

    # ================ DRAWING THE SPELL COOLDOWNS ON TOP OF THE SPELL PANEL LAYER ================
    player.update_cooldown_data(display)

    mouse_click_area.x = mousex
    mouse_click_area.y = mousey

    display.blit(player.bar_img, player.bar_rect1)
    display.blit(player.bar_img, player.bar_rect2)
    pygame.draw.rect(display, '#870505', player.hp_bar_filler)
    pygame.draw.rect(display, "#2424ab", player.mana_bar_filler)

    screen_veil.update()

    # Pause and Game Over menu UI manager is drawed one layer above the screen veil
    overlay_manager.draw_ui(display)
    pause_menu_ui_manager.draw_ui(display)
    game_over_manager.draw_ui(display)

  # Mouse is above all graphical layers
  display.blit(mouse_img, mouse_rect)
  # Make display 2x bigger
  screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0,0))

  # c = pygame.

  pygame.display.update()