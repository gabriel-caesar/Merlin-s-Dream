from __future__ import annotations
from typing import TYPE_CHECKING
from pygame_gui.core import ObjectID

import pygame_gui
import pygame

if TYPE_CHECKING:
  from main import Player

DISPLAY_SIZE = (640, 360)

def load_gui(
  gui_manager: pygame_gui.UIManager,
  player: Player
) -> dict:
  
  # ======== FONT ========
  cd_font = pygame.font.Font('./font/Avqest-eeel.ttf', 20)

  # ======== MAIN GAMEPLAY INTERFACE COMPONENTS ========

  cinfo_button_surf = pygame.image.load('./assets/ui/character_info_button.png')
  char_info_button = pygame_gui.elements.UIButton(
    relative_rect=cinfo_button_surf.get_rect(topleft=(8, 8)),
    manager=gui_manager,
    text='',
    object_id=ObjectID(object_id='#char_info_button', class_id='@img_button')
  )

  settings_button_surf = pygame.image.load('assets/ui/settings_button.png')
  settings_button = pygame_gui.elements.UIButton(
    relative_rect=settings_button_surf.get_rect(topleft=(48, 10)),
    manager=gui_manager,
    text='',
    object_id=(ObjectID(object_id='#settings_button', class_id='@img_button'))
  )

  player_hp_label = pygame_gui.elements.UILabel(
    text=f'Health: {player.hp}/{player.max_hp}',
    manager=gui_manager,
    relative_rect=player.bar_rect1,
  )
  player_hp_label.rect.y -= 25

  player_mana_label = pygame_gui.elements.UILabel(
    text=f'Mana: {player.mana}/{player.max_mana}',
    manager=gui_manager,
    relative_rect=player.bar_rect2,
  )
  player_mana_label.rect.y -= 25

  # ======== WAVE INDICATOR ELEMENTS ========

  wave_panel = pygame_gui.elements.UIPanel(
    relative_rect=(540,10,80,30),
    manager=gui_manager,
  )

  wave_label = pygame_gui.elements.UILabel(
    relative_rect=(0,0,-1,-1),
    anchors={
      'centerx': 'centerx',
      'centery': 'centery',
    },
    text='Wave: 1',
    manager=gui_manager,
    container=wave_panel
  )

  # ======== CHARACTER EXPERIENCE PROGRESS BAR ELEMENTS ========

  # This progress bar subclass instance makes the default
  # progress text numbers disappear
  class XPBar(pygame_gui.elements.UIProgressBar):
    def status_text(self):
        return "experience"
  xp_bar = XPBar(
    relative_rect=(0, 342, 275, 20),
    manager=gui_manager,
    anchors={
      'centerx':'centerx',
    },
    object_id=ObjectID(object_id='#xp_bar')
  )


  # ======== CHARACTER SPELLS PANEL ========

  spell_panel_surf = pygame.image.load('./assets/ui/spell_panel.png')
  spell_panel = pygame_gui.elements.UIPanel(
    relative_rect=spell_panel_surf.get_rect(
      midbottom=(
        DISPLAY_SIZE[0] // 2, 
        DISPLAY_SIZE[1] - 17
      )
    ),
    manager=gui_manager,
    object_id=ObjectID(object_id='#spell_panel')
  )

  # ======== MAGIC BOLT UI ELEMENTS ========

  magic_bolt_portrait = pygame_gui.elements.UIButton(
    text='',
    relative_rect=(-1,-1,23,23),
    manager=gui_manager,
    object_id=ObjectID(object_id='#magic_bolt_button', class_id='@spell_buttons'),
    container=spell_panel,
  )

  magic_bolt_info = pygame_gui.elements.UIPanel(
    relative_rect=(magic_bolt_portrait.rect.x - 175, magic_bolt_portrait.rect.y - 75, 200, 80),
    manager=gui_manager,
    visible=0
  )

  magic_bolt_cd_text = pygame_gui.elements.UITextBox(
    html_text="<font color='#f2bd29'>Cooldown: 2s</font>",
    relative_rect=(magic_bolt_portrait.rect.x - 175, magic_bolt_portrait.rect.y - 102,-1,-1),
    manager=gui_manager,
    object_id=ObjectID(class_id='@cooldown_text'),
    visible=0
  )

  magicbolt_cd_timer = cd_font.render('2', True, '#f2bd29')
  magicbolt_cd_timer_rect = magicbolt_cd_timer.get_rect(center =(
    magic_bolt_portrait.rect.center[0],
    magic_bolt_portrait.rect.center[1],
  ))

  # ======== FIRE BOLT UI ELEMENTS ========

  fire_bolt_portrait = pygame_gui.elements.UIButton(
    text='',
    relative_rect=(23,-1,23,23),
    manager=gui_manager,
    object_id=ObjectID(object_id='#fire_bolt_button', class_id='@spell_buttons'),
    container=spell_panel,
    visible=0
  )

  fire_bolt_info = pygame_gui.elements.UIPanel(
    relative_rect=(fire_bolt_portrait.rect.x, fire_bolt_portrait.rect.y - 75, 200, 80),
    manager=gui_manager,
    visible=0
  )

  fire_bolt_key = pygame_gui.elements.UIButton(
    text='1',
    manager=gui_manager,
    relative_rect=(
      fire_bolt_portrait.rect.x + 3, 
      fire_bolt_portrait.rect.y - 14,
      18, 18
    ),
    object_id=ObjectID(class_id='@spell_keys')
  )

  fire_bolt_cd_text = pygame_gui.elements.UITextBox(
    html_text="<font color='#f2bd29'>Cooldown: 3s</font>",
    relative_rect=(fire_bolt_portrait.rect.x, fire_bolt_portrait.rect.y - 102,-1,-1),
    manager=gui_manager,
    object_id=ObjectID(class_id='@cooldown_text'),
    visible=0
  )

  firebolt_cd_timer = cd_font.render('3', True, '#f2bd29')
  firebolt_cd_timer_rect = firebolt_cd_timer.get_rect(center =(
    fire_bolt_portrait.rect.center[0],
    fire_bolt_portrait.rect.center[1],
  ))

  # ======== TELETRANSPORT UI ELEMENTS ========

  tp_portrait = pygame_gui.elements.UIButton(
    text='',
    relative_rect=(47,-1,25,25),
    manager=gui_manager,
    object_id=ObjectID(object_id='#tp_button', class_id='@spell_buttons'),
    container=spell_panel,
    visible=0
  )

  tp_info = pygame_gui.elements.UIPanel(
    relative_rect=(tp_portrait.rect.x + 10, tp_portrait.rect.y - 75, 200, 80),
    manager=gui_manager,
    visible=0
  )

  tp_key = pygame_gui.elements.UIButton(
    text='2',
    manager=gui_manager,
    relative_rect=(
      tp_portrait.rect.x + 3, 
      tp_portrait.rect.y - 14,
      18, 18
    ),
    object_id=ObjectID(class_id='@spell_keys')
  )

  tp_cd_text = pygame_gui.elements.UITextBox(
    html_text="<font color='#f2bd29'>Cooldown: 5s</font>",
    relative_rect=(tp_portrait.rect.x + 10,tp_portrait.rect.y - 102,-1,-1),
    manager=gui_manager,
    object_id=ObjectID(class_id='@cooldown_text'),
    visible=0
  )

  tp_cd_timer = cd_font.render('5', True, '#f2bd29')
  tp_cd_timer_rect = tp_cd_timer.get_rect(center =(
    tp_portrait.rect.center[0],
    tp_portrait.rect.center[1],
  ))

  # ======== SPELLS INFO BOXES WHEN PLAYER HOVER ON TOP OF IT ========

  pygame_gui.elements.UITextBox(
    relative_rect=(0, 0, 200, 80),
    starting_height=0,
    manager=gui_manager,
    container=magic_bolt_info,
    html_text=("<font color='#f2bd29'><b>Magic Bolt</b></font><br>"
      "This is Merlin's <font color='#daf0ff'>magic bolt</font>, "
      "it will be casted as an auto-attack. Damage scales based on "
      "current <font color='#4169E1'>intelligence</font> levels."),
    object_id=ObjectID(class_id='@spell_labels')
  )

  pygame_gui.elements.UITextBox(
    relative_rect=(0, 0, 200, 80),
    starting_height=0,
    manager=gui_manager,
    container=fire_bolt_info,
    html_text=("<font color='#f2bd29'><b>Fire Bolt</b><br></font>"
      "This is Merlin's <font color='#FF0000'>fire bolt</font>, "
      "it will be casted by the press of a button. Damage scales based on "
      "current <font color='#4169E1'>intelligence</font> levels."),
    object_id=ObjectID(class_id='@spell_labels')
  )

  pygame_gui.elements.UITextBox(
    relative_rect=(0, 0, 200, 80),
    starting_height=0,
    manager=gui_manager,
    container=tp_info,
    html_text=("<font color='#f2bd29'><b>Teletransport</b><br></font>"
      "This is Merlin's <font color='#FF0000'>teletransport</font>, "
      "it will be casted by the press of a button. In a blink of an eye will teletransport "
      "the caster to whatever destination within range."),
    object_id=ObjectID(class_id='@spell_labels')
  )

  # ======== CHARACTER INFO PANEL ========

  char_info_panel = pygame_gui.elements.UIPanel(
    relative_rect=(char_info_button.rect.x + 10, char_info_button.rect.y + 26, 105, 150),
    manager=gui_manager,
    visible=0
  )
  pygame_gui.elements.UILabel(
    relative_rect=(0,0,-1,-1),
    manager=gui_manager,
    text='Archmage Merlin',
    container=char_info_panel,
    object_id=ObjectID(object_id='#panel_char_name_title'),
    anchors={
      'centerx': 'centerx'
    }
  )
  char_level_label = pygame_gui.elements.UILabel(
    relative_rect=(0,30,-1,-1),
    manager=gui_manager,
    text=f'Level: {player.level}',
    parent_element=char_info_panel,
    container=char_info_panel,
    anchors={
      'centerx': 'centerx'
    }
  )
  char_str_label = pygame_gui.elements.UILabel(
    relative_rect=(0,45,-1,-1),
    manager=gui_manager,
    text=f'Strength: {player.strength}',
    parent_element=char_info_panel,
    container=char_info_panel,
    anchors={
      'centerx': 'centerx'
    }
  )
  char_int_label = pygame_gui.elements.UILabel(
    relative_rect=(0,60,-1,-1),
    manager=gui_manager,
    text=f'Int: {player.intelligence}',
    parent_element=char_info_panel,
    container=char_info_panel,
    anchors={
      'centerx': 'centerx'
    }
  )
  char_haste_label = pygame_gui.elements.UILabel(
    relative_rect=(0,75,-1,-1),
    manager=gui_manager,
    text=f'Haste: {player.haste}',
    parent_element=char_info_panel,
    container=char_info_panel,
    anchors={
      'centerx': 'centerx'
    }
  )
  char_kill_count_label = pygame_gui.elements.UILabel(
    relative_rect=(0,90,-1,-1),
    manager=gui_manager,
    text=f'Kills: {player.kills}',
    parent_element=char_info_panel,
    container=char_info_panel,
    anchors={
      'centerx': 'centerx'
    }
  )
  char_xp_label = pygame_gui.elements.UILabel(
    relative_rect=(0,120,-1,-1),
    manager=gui_manager,
    text=f'XP: {player.xp}/{player.max_xp}',
    parent_element=char_info_panel,
    container=char_info_panel,
    anchors={
      'centerx': 'centerx'
    }
  )

  # ======== POTIONS ========
  
  health_potion = pygame_gui.elements.UIButton(
    relative_rect=(132, 330, 30, 30),
    manager=gui_manager,
    object_id=ObjectID(object_id='#health_potion', class_id='@potion_buttons'),
    text=''
  )

  hp_potion_count = pygame_gui.elements.UILabel(
    relative_rect=health_potion.rect,
    text='5',
    object_id=ObjectID(class_id='@cooldown_text'),
    manager=gui_manager
  )
  hp_potion_count.rect.x += 8
  hp_potion_count.rect.y += 8

  mana_potion = pygame_gui.elements.UIButton(
    relative_rect=(479, 330, 30, 30),
    manager=gui_manager,
    object_id=ObjectID(object_id='#mana_potion', class_id='@potion_buttons'),
    text=''
  )

  mana_potion_count = pygame_gui.elements.UILabel(
    relative_rect=mana_potion.rect,
    text='5',
    object_id=ObjectID(class_id='@cooldown_text'),
    manager=gui_manager
  )
  mana_potion_count.rect.x -= 8
  mana_potion_count.rect.y += 8

  gui_elements = {
    'char_info_button': char_info_button,
    'char_info_panel': char_info_panel,
    'player_hp_label': player_hp_label,
    'player_mana_label': player_mana_label,
    'spell_panel': spell_panel,
    'settings_button': settings_button,
    'portraits': {
      'magic_bolt': magic_bolt_portrait,
      'fire_bolt': fire_bolt_portrait,
      'teletransport': tp_portrait,
    },
    'keys': {
      '1': fire_bolt_key,
      '2': tp_key,
    },
    'char_info': {
      'level': char_level_label,
      'str': char_str_label,
      'int': char_int_label,
      'haste': char_haste_label,
      'xp': char_xp_label,
      'kills': char_kill_count_label
    },
    'spells_info': {
      'magic_bolt': magic_bolt_info,
      'fire_bolt': fire_bolt_info,
      'teletransport': tp_info,
    },
    'cooldown_text': {
      'teletransport': tp_cd_text,
      'fire_bolt': fire_bolt_cd_text,
      'magic_bolt': magic_bolt_cd_text
    },
    'cooldown_timer': {
      'teletransport': tp_cd_timer_rect,
      'fire_bolt': firebolt_cd_timer_rect,
      'magic_bolt': magicbolt_cd_timer_rect
    },
    'health_potion_count': hp_potion_count,
    'mana_potion_count': mana_potion_count,
    'health_potion_btn': health_potion,
    'mana_potion_btn': mana_potion,
    'wave_panel': wave_panel,
    'wave_label': wave_label,
    'xp_bar': xp_bar
  }

  return gui_elements

def load_pause_menu(gui_manager: pygame_gui.UIManager) -> dict:
  
  # ======== PAUSE PANEL ========

  main_pause_panel = pygame_gui.elements.UIPanel(
    relative_rect=(220, 50, 200, 250),
    manager=gui_manager,
    visible=0
  )

  pygame_gui.elements.UILabel(
    text='GAME PAUSED',
    manager=gui_manager,
    relative_rect=(0, 10, -1, -1),
    container=main_pause_panel,
    object_id=ObjectID(object_id='#game_paused_title'),
    anchors={
      'centerx': 'centerx'
    }
  )

  main_menu_button = pygame_gui.elements.UIButton(
    relative_rect=(0,70,91,-1),
    manager=gui_manager,
    container=main_pause_panel,
    text='MAIN MENU',
    object_id=ObjectID(class_id='@menu_buttons', object_id='#main_text_label'),
    anchors={
      'centerx': 'centerx'
    },
  )
  options_button = pygame_gui.elements.UIButton(
    relative_rect=(0,110,91,-1),
    manager=gui_manager,
    container=main_pause_panel,
    text='OPTIONS',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={
      'centerx': 'centerx'
    },
  )
  quit_button = pygame_gui.elements.UIButton(
    relative_rect=(0,150,91,-1),
    manager=gui_manager,
    container=main_pause_panel,
    text='QUIT',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={
      'centerx': 'centerx'
    },
  )

  music_label = pygame_gui.elements.UILabel(
    text='MUSIC VOLUME',
    relative_rect=(0,60,-1,-1),
    container=main_pause_panel,
    manager=gui_manager,
    visible=0,
    anchors={'centerx':'centerx'},
  )
  
  music_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=(0,75,150,20),
    start_value=50,
    value_range=(0, 100),
    manager=gui_manager,
    container=main_pause_panel,
    anchors={'centerx':'centerx'},
    visible=0
  )

  sound_label = pygame_gui.elements.UILabel(
    text='SOUND VOLUME',
    relative_rect=(0,120,-1,-1),
    container=main_pause_panel,
    manager=gui_manager,
    visible=0,
    anchors={'centerx':'centerx'},
  )
  
  sound_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=(0,135,150,20),
    start_value=50,
    value_range=(0, 100),
    manager=gui_manager,
    container=main_pause_panel,
    anchors={'centerx':'centerx'},
    visible=0
  )

  back_button = pygame_gui.elements.UIButton(
    relative_rect=(0,180,91,-1),
    manager=gui_manager,
    container=main_pause_panel,
    text='BACK',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={'centerx':'centerx'},
    visible=0
  )

  wave_display = pygame_gui.elements.UILabel(
    relative_rect=(0,0,-1,-1),
    anchors={
      'centerx': 'centerx',
      'centery': 'centery',
    },
    text='Wave 1',
    manager=gui_manager,
    object_id=ObjectID(object_id='#wave_display'),
    visible=0
  )
  
  pause_menu_elements = {
    'main_menu_button': main_menu_button,
    'options_button': options_button,
    'panel': main_pause_panel,
    'quit_button': quit_button,
    'wave_display': wave_display,
    'options': {
      'sound_label': sound_label,
      'sound_slider': sound_slider,
      'music_label': music_label,
      'music_slider': music_slider,
      'back_button': back_button,
    }
  }

  return pause_menu_elements

def load_menu_elements(gui_manager: pygame_gui.UIManager) -> dict:

  main_panel = pygame_gui.elements.UIPanel(
    relative_rect=(0,50,200,250),
    manager=gui_manager,
    anchors={'centerx':'centerx'}
  )

  menu_title = pygame.image.load('./assets/ui/main_menu_title.png')
  pygame_gui.elements.UIImage(
    relative_rect=(0,10,menu_title.get_width() // 4, menu_title.get_height() // 4),
    image_surface=menu_title,
    manager=gui_manager,
    container=main_panel,
    object_id=ObjectID(),
    anchors={'centerx':'centerx'},
  )

  play_button = pygame_gui.elements.UIButton(
    relative_rect=(0,120,91,-1),
    manager=gui_manager,
    container=main_panel,
    text='PLAY',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={'centerx':'centerx'},
  )

  options_button = pygame_gui.elements.UIButton(
    relative_rect=(0,160,91,-1),
    manager=gui_manager,
    container=main_panel,
    text='OPTIONS',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={'centerx':'centerx'},
  )

  quit_button = pygame_gui.elements.UIButton(
    relative_rect=(0,200,91,-1),
    manager=gui_manager,
    container=main_panel,
    text='QUIT',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={'centerx':'centerx'},
  )

  music_label = pygame_gui.elements.UILabel(
    text='MUSIC VOLUME',
    relative_rect=(0,110,-1,-1),
    container=main_panel,
    manager=gui_manager,
    visible=0,
    anchors={'centerx':'centerx'},
  )
  
  music_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=(0,125,150,20),
    start_value=50,
    value_range=(0, 100),
    manager=gui_manager,
    container=main_panel,
    anchors={'centerx':'centerx'},
    visible=0
  )

  sound_label = pygame_gui.elements.UILabel(
    text='SOUND VOLUME',
    relative_rect=(0,160,-1,-1),
    container=main_panel,
    manager=gui_manager,
    visible=0,
    anchors={'centerx':'centerx'},
  )
  
  sound_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=(0,175,150,20),
    start_value=50,
    value_range=(0, 100),
    manager=gui_manager,
    container=main_panel,
    anchors={'centerx':'centerx'},
    visible=0
  )

  back_button = pygame_gui.elements.UIButton(
    relative_rect=(0,210,91,-1),
    manager=gui_manager,
    container=main_panel,
    text='BACK',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={'centerx':'centerx'},
    visible=0
  )

  main_menu_elements = {
    'main_panel': main_panel,
    'play_button': play_button,
    'options_button': options_button,
    'quit_button': quit_button,
    'sound_label': sound_label,
    'sound_slider': sound_slider,
    'music_label': music_label,
    'music_slider': music_slider,
    'back_button': back_button,
  }

  return main_menu_elements

def load_game_over_elements(gui_manager: pygame_gui.UIManager) -> dict:
  # ======== GAME OVER PANEL ========

  main_panel = pygame_gui.elements.UIPanel(
    relative_rect=(220, 50, 200, 250),
    manager=gui_manager,
    visible=0
  )

  pygame_gui.elements.UILabel(
    text='GAME OVER',
    manager=gui_manager,
    relative_rect=(0, 10, -1, -1),
    container=main_panel,
    object_id=ObjectID(object_id='#game_paused_title'),
    anchors={
      'centerx': 'centerx'
    }
  )

  main_menu_button = pygame_gui.elements.UIButton(
    relative_rect=(0,70,91,-1),
    manager=gui_manager,
    container=main_panel,
    text='MAIN MENU',
    object_id=ObjectID(class_id='@menu_buttons', object_id='#main_text_label'),
    anchors={
      'centerx': 'centerx'
    },
  )

  quit_button = pygame_gui.elements.UIButton(
    relative_rect=(0,100,91,-1),
    manager=gui_manager,
    container=main_panel,
    text='QUIT',
    object_id=ObjectID(class_id='@menu_buttons'),
    anchors={
      'centerx': 'centerx'
    },
  )

  game_over_elements = {
    'main_panel': main_panel,
    'main_menu_button': main_menu_button,
    'quit_button': quit_button
  }

  return game_over_elements

def load_info_screen(gui_manager) -> dict:

  main_panel = pygame_gui.elements.UIPanel(
    relative_rect=(0,0, 200, 300),
    manager=gui_manager,
    anchors={
      'centerx':'centerx',
      'centery':'centery',
    },
    visible=0
  )

  pygame_gui.elements.UILabel(
    text="Welcome to Merlin's Dream",
    relative_rect=(0,0,-1,-1),
    container=main_panel,
    manager=gui_manager,
    object_id=ObjectID(object_id='#info_text_title')
  )

  main_text = pygame_gui.elements.UITextBox(
    html_text=(
      "<font color='#f2bd29'>Merlin</font> is ensnared within his own dream, forced to battle the creatures that haunted his past adventures. Your task is to keep the old mage alive for as long as possible, lest he perish within the realm of sleep itself. Face endless waves of foes from distant lands and dark domains, including orcs, undead horrors, and many other fearsome beings."

      "<br><br>"

      "- Right-click with the mouse to <font color='#f2bd29'>guide</font> Merlin across the dreamscape. <br><br>"

      "- <font color='#ff0000'>Attack</font> enemies by right-clicking upon your chosen target. <br><br>"

      "- <font color='#f2bd29'>Merlin's</font> basic attack is an enchanted <font color='#f2bd29'>Magic Bolt</font>, cast automatically against foes within range. <br><br>"

      "- Gain levels to recover <font color='#f2bd29'>forgotten spells</font>, fragments of magic once mastered by the ancient wizard. <br><br>"
    ),
    manager=gui_manager,
    container=main_panel,
    relative_rect=(0, 20, 188, 250),
    starting_height=0,
    object_id=ObjectID(object_id='#info_text')
  )

  pygame_gui.elements.UILabel(
    container=main_panel,
    relative_rect=(0,270,-1,-1),
    manager=gui_manager,
    anchors={
      'centerx':'centerx',
    },
    text='Press space to continue',
    object_id=ObjectID(object_id='#info_press_spacebar')
  )

  info_screen_elements = {
    'main_panel': main_panel,
    'main_text': main_text
  }

  return info_screen_elements

def load_overlay_elements(gui_manager: pygame_gui.UIManager) -> dict:

  # ======== LEARNING A SPELL INTERFACE ========
  earn_spell_panel = pygame_gui.elements.UIPanel(
    relative_rect=(0,0,300,200),
    anchors={
      'centerx': 'centerx',
      'centery': 'centery'
    },
    manager=gui_manager,
    object_id=ObjectID(object_id='#earn_spell_panel'),
    visible=0
  )

  pygame_gui.elements.UILabel(
    relative_rect=(60, 30, -1, -1),
    text='Level up bonus',
    object_id=(ObjectID(object_id='#label_lvl_up_label')),
    manager=gui_manager,
    container=earn_spell_panel
  )

  earn_spell_label = pygame_gui.elements.UILabel(
    relative_rect=(60,10,-1,-1),
    text='',
    object_id=ObjectID(object_id="#earn_spell_label"),
    manager=gui_manager,
    container=earn_spell_panel
  )

  spell_img_container = pygame_gui.elements.UIPanel(
    relative_rect=(10,10,46,46),
    manager=gui_manager,
    object_id=ObjectID(object_id="#earn_spell_img_container"),
    container=earn_spell_panel
  )

  earn_spell_text = pygame_gui.elements.UITextBox(
    html_text='',
    relative_rect=(10,60,270,120),
    container=earn_spell_panel,
    object_id=ObjectID(object_id='#earn_spell_text')
  )

  close_spell_panel_button = pygame_gui.elements.UIButton(
    text='X',
    relative_rect=(-24,-2,22,24),
    container=earn_spell_panel,
    object_id=ObjectID(object_id='#close_spell_panel_button'),
    anchors={'top':'top','right':'right'}
  )

  overlay_elements = {
    'panel': earn_spell_panel,
    'text': earn_spell_text,
    'close_btn': close_spell_panel_button,
    'label': earn_spell_label,
    'img_container': spell_img_container
  }

  return overlay_elements