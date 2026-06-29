from __future__ import annotations
from entity import Entity
from hit_effect import HitEffect
from projectile import Projectile
import utils
import pygame
import random
import math
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
  from main import Player
  from sound_manager import SoundManager

HPBAR_WIDTH = 145

class Enemy(Entity):
  def __init__(
    self, 
    tile: dict, 
    name: str,
    atk_range: int,
    display: pygame.Surface,
    sound_manager: SoundManager,
    wave: int = 1,
    strength: int = 10,
    intelligence: int = 10,
    hp: int = 100,
    mana: int = 100,
    level: int = 1,
    xp: int = 0,
    max_xp:int = 100,
    is_boss: bool = False
  ):
    self.idle_spritesheet = list(utils.get_sprites(['enemies', name], 'idle').values())
    self.running_spritesheet = list(utils.get_sprites(['enemies', name], 'walk').values())
    self.backview_idle_spritesheet = list(utils.get_sprites(['enemies', name, 'backview'], 'backview_idle').values())
    self.backview_running_spritesheet = list(utils.get_sprites(['enemies', name, 'backview'], 'backview_walk').values())
    self.attack_spritesheet = list(utils.get_sprites(['enemies', name, 'attack'], 'attack').values())
    self.backview_attack_spritesheet = list(utils.get_sprites(['enemies', name, 'attack', 'backview'], 'attack').values())

    self.level = level + random.randint(0, 1)

    Entity.__init__(
      self, 
      tile, 
      self.idle_spritesheet,
      strength,
      intelligence,
      hp,
      mana,
      self.level,
      xp,
      max_xp,
      attribute_multiplier=utils.get_wave_multiplier(wave),
      is_boss=is_boss
    )

    self.sound_manager = sound_manager
    self.display = display
    self.name = name
    self.patrol_timer = random.randint(90, 240)
    self.patrol_tile = self.on_tile # Never changes after arriving at the destination tile
    self.speed = 0.5
    self.chase_cooldown = 0
    self.xp_value = int(self.level + (wave * 50))
    self.is_boss = is_boss
    self.chase_cooldown_placeholder = 120
    self.got_frenzy = False

    self.attacking = False
    self.atk_type = None
    self.atk_range = atk_range
    self.atk_cooldown = 0
    self.damage = self.strength
    self.projectile_list = []

    if self.atk_range <= 20 or self.atk_range == 40:
      self.atk_type = 'slash'
    else: 
      self.atk_type = 'ranged_hit'


    # ========== AGGRO RELATED LOGIC ==========
    self.aggro = False
    self.aggro_range = 60
    self.aggro_pointer = pygame.image.load('./assets/ui/aggro_pointer.png')
    self.frenzy_pointer = pygame.image.load('./assets/ui/frenzy_pointer.png')
    self.aggro_pointer_rect = self.aggro_pointer.get_rect()
    self.aggro_pointer_timer = 0

    # ========== HP BAR GUI ==========
    self.hp_bar_img = pygame.image.load('./assets/ui/enemy_hp_bar.png')
    self.hp_bar_rect = self.hp_bar_img.get_rect(center=(320, 20))
    self.hp_bar_filler = pygame.Rect(
      self.hp_bar_rect.left + 22,
      self.hp_bar_rect.top + 3,
      HPBAR_WIDTH,
      20
    )

    # Filtering any underscore inside name
    if '_' in self.name:
      self.name = self.name.split('_')
      self.name = ' '.join(self.name)

    if self.is_boss:
      if 'orc' in self.name:
        display_name = 'OGRE LORD'
      elif 'shadow' in self.name:
        display_name = 'SHADOW LICH'
    else:
      display_name = self.name.upper()

    # Making sure the text is small for longer names
    if len(self.name) > 8:
      self.font = pygame.font.Font('./font/Avqest-eeel.ttf', 14)
    else:
      self.font = pygame.font.Font('./font/Avqest-eeel.ttf', 16)

    self.hpbar_text = self.font.render(display_name, True, '#ffffff')
    self.hpbar_text_rect = self.hpbar_text.get_rect()

    # ========== LEVEL/HP INFO GUI ==========

    # Panel image
    self.level_container_img = pygame.image.load('./assets/ui/enemy_info_bar.png')
    self.level_container_img = pygame.transform.scale(
      self.level_container_img,
      (self.level_container_img.get_width(), 15)
    )
    self.level_container_rect = self.level_container_img.get_rect(
      center=(
        self.hp_bar_rect.center[0],
        self.hp_bar_rect.center[1] + 19
      )
    )

    # Level text in the panel image
    creature_info_font = pygame.font.Font('./font/Avqest-eeel.ttf', 11)
    self.level_text_surf = creature_info_font.render(f'Level {self.level}', True, '#ff0000')
    self.level_text_rect = self.level_text_surf.get_rect(
      center=(
        self.level_container_rect.center[0] - 45,
        self.level_container_rect.center[1]
      )
    )

    # HP text in the panel image
    self.hp_points_surf = creature_info_font.render(f'{self.hp}/{self.max_hp}', True, '#ffffff')
    self.hp_points_rect = self.hp_points_surf.get_rect(
      center=(
        self.level_container_rect.center[0] + 40,
        self.level_container_rect.center[1]
      )
    )

  def handle_aggro_pointer(self) -> None:
    if self.aggro_pointer_timer > 0 and self.alive:
      self.aggro_pointer_timer -= 1
      
      self.aggro_pointer_rect = self.aggro_pointer.get_rect(
        midbottom = (
          self.rect.midtop[0],
          self.rect.midtop[1] - 5 # Slightly to the top of the enemy's head
        )
      )      

      self.display.blit(
        self.aggro_pointer,
        self.aggro_pointer_rect
      )

  def run_animation(self) -> None:
    if len(self.animation_frames) > 1:

      # ============== RUNNING ANIMATION ==============
      if self.destination_tile:
        if self.facing == 'backview':
          self.animation_frames = self.backview_running_spritesheet

        else:
          self.animation_frames = self.running_spritesheet

      # ============== ATTACKING ANIMATION ==============
      elif self.attacking:
        if self.facing == 'backview':
          self.animation_frames = self.backview_attack_spritesheet

        else:
          self.animation_frames = self.attack_spritesheet

      # ============== IDLE ANIMATION ==============
      else:
        # Making sure the attack animation doesn't get ran over by the idle one
        if not self.attacking: 
          if self.facing == 'backview':
            self.animation_frames = self.backview_idle_spritesheet
          else:
            self.animation_frames = self.idle_spritesheet

      # ============== ANIMATION LOOP ==============
      self.animation_index += 0.1
      if self.animation_index >= len(self.animation_frames):
        self.animation_index = 0
        if self.attacking: # Finish the enemy attack animation at this point
          self.attacking = False

      self.image = self.animation_frames[int(self.animation_index)]
      
    self.image = pygame.transform.flip(self.image, self.flip, False)
    if self.is_boss: 
      self.image = pygame.transform.scale(self.image, (self.image.get_width() * 2, self.image.get_height() * 2))

  def patrol(self, map_data: list) -> None:

    if self.patrol_timer == 0:
      ix = self.patrol_tile['index'][0]
      iy = self.patrol_tile['index'][1]

      x_val = random.randint(ix - 2, ix + 2)
      y_val = random.randint(iy - 2, iy + 2)

      new_index = [x_val, y_val]

      for data in map_data:
        if (
          data['index'][0] == new_index[0] and
          data['index'][1] == new_index[1]
        ):
          self.destination_tile = data
          self.patrol_timer = 240
          self.get_facing_direction()
    
  def get_facing_direction(self, real_target: Player | None = None) -> None:
    if self.destination_tile:
      destination = self.destination_tile['hover_area'].center
    if real_target:
      destination = real_target.rect.center

    origin = self.rect.midbottom
    if destination[1] < origin[1]:
      self.facing = 'backview'
    else:
      self.facing = 'front'

    if destination[0] > self.rect.midbottom[0]:
      self.flip = False
    else:
      self.flip = True
    return

  def show_hp_bar(self) -> None:
    self.display.blit(self.hp_bar_img, self.hp_bar_rect)
    pygame.draw.rect(self.display, "#870505", self.hp_bar_filler)
    self.hpbar_text_rect.center = self.hp_bar_rect.center # Center the text in the hp bar
    self.hpbar_text_rect.top += 2 # Offset to center the text due to font size
    self.display.blit(self.hpbar_text, self.hpbar_text_rect)

    # Displaying the level info
    self.display.blit(self.level_container_img, self.level_container_rect)
    self.display.blit(self.level_text_surf, self.level_text_rect)
    self.display.blit(self.hp_points_surf, self.hp_points_rect)

  def calculate_current_bar_width(self, type: str) -> None:
    if type == 'hp':
      curr_width = (self.hp * HPBAR_WIDTH) / self.max_hp # Regra de 3
      self.hp_bar_filler.width = curr_width

  def chase(self, player: Player) -> None:

    # Attack range 20 is for melee enemies, anything bigger is ranged
    
    # Making sure player is alive so enemy can chase and attack it
    if player.alive:
      # Updating the player targeted list with this entity
      if self not in player.being_targeted_by:
        player.being_targeted_by.append(self)

      if self.chase_cooldown > 0:
        self.chase_cooldown -= 1
        self.destination_tile = {}
      else:
        self.destination_tile = {'hover_area': player.rect}
        self.get_facing_direction()

      # Finding the Euclidean distance between player and enemy
      dt_x = self.rect.x - player.rect.x
      dt_y = self.rect.y - player.rect.y
      distance = math.sqrt((dt_x) ** 2 + (dt_y) ** 2)

      if int(distance) <= self.atk_range:
        # Stop moving and attack
        self.destination_tile = {}
        self.atk_type = self.atk_type
        self.attack(player, type=self.atk_type)

        # Determines an interval before chasing the player again
        self.chase_cooldown = self.chase_cooldown_placeholder 

  def attack(self, player: Player, type: Literal['slash', 'ranged_hit']) -> None:
    # Change the facing direction if the entity is currently attacking and not moving
    self.get_facing_direction(real_target=player)

    if self.atk_cooldown > 0:
      self.atk_cooldown -= 1

    else: 
      if type == 'slash':
        global slash_imgs_list
        given_damage = random.randint(self.damage - 3, self.damage + 3)
        player.take_damage(given_damage, bb_color="#ff0000", sound_manager=self.sound_manager)
        player.calculate_current_bar_width('hp')
        hit_effect = HitEffect(target=player, type=type) # Attention: type == slash
        self.hit_effects_list.append(hit_effect)
        self.sound_manager.sounds['swing'].play() # Play the weapon swing sound()

        if self.is_boss:
          # Screen shake
          pygame.event.post(pygame.event.Event(pygame.USEREVENT + 12, duration=120))

      elif type == 'ranged_hit':
        
        if self.name == 'shadow caster':
          self.sound_manager.sounds['fire_bolt']['cast'].play()
          d1 = self.intelligence - 3
          d2 = self.intelligence + 3
          self.damage = random.randint(d1, d2)
        else:
          self.sound_manager.sounds['arrow']['cast'].play() # Play the shooting arrow sound

        self.projectile = Projectile(
          caster=self,
          # Attention: type can be slash or ranged_hit, but for 
          # fire_bolt matching shadow caster means that they share
          # the same impact sound
          name='fire_bolt' if self.name == 'shadow caster' else type,
          origin=self.rect.center, 
          dmg_value=self.damage,
          target=player,
          display=self.display,
          sound_manager=self.sound_manager,
          has_particles=True if self.name == 'shadow caster' else False
        )
        self.projectile_list.append(self.projectile)

      
      self.attacking = True
      self.atk_cooldown = 120

  def update(
    self, 
    map_data: list, 
    player: Player,
    game_paused: bool
  ) -> None:

    if not game_paused:
      self.run_animation()  
      
      if self.is_dead():

        # self.alive tells the code to clear the player target only once while this
        # loop runs until the dead enemy corpse vanishes through self.vanish_timer
        if self.alive:
          player.target = []

          # Play orc death sound once
          if 'orc' in self.name:
            index = random.randint(0,2)
            self.sound_manager.sounds['orc_death_sounds'][str(index)].play()
          elif 'shadow' in self.name:
            index = random.randint(0,2)
            self.sound_manager.sounds['shadow_death_sounds'][str(index)].play()


          # Used for regeneration purposes
          if self in player.being_targeted_by:
            player.being_targeted_by.remove(self)

          self.alive = False

        self.animation_frames = []
        this_name = self.name.split(' ')
        this_name = '_'.join(this_name)

        dead_img = pygame.image.load(f'./assets/enemies/{this_name}/dead.png')
        self.image = dead_img
        if self.is_boss:
          # Scaling the death assets if necessary
          self.image = pygame.transform.scale(dead_img, (dead_img.get_width() * 2, dead_img.get_height() * 2))

        blood_indicator = pygame.image.load('./assets/cursor/blood_indicator.png')

        # Scaling the death assets if necessary
        if self.is_boss:
          blood_indicator = pygame.transform.scale(blood_indicator, (blood_indicator.get_width() * 2, blood_indicator.get_height() * 2))
          self.display.blit(blood_indicator, (self.rect.x - 5, self.rect.y + 23))
        else:
          self.display.blit(blood_indicator, (self.rect.x - 5, self.rect.y + 12))


        self.vanish_timer -= 1

        if self.vanish_timer == 0:
          self.kill()
          return
        
      else:


        # Getting the distance between the enemy and the player for aggro
        self.distance_from_enemy = self.check_distance_from_enemy(enemy=player)

        if self.destination_tile:
          self.move() 

        if not self.aggro:
          if self.patrol_timer > 0:
            self.patrol_timer -= 1
          self.patrol(map_data=map_data)

          if (
            self.hp < self.max_hp or # If enemy gets  hit
            self.distance_from_enemy <= self.aggro_range and
            self.distance_from_enemy > 0 
          ):
            self.aggro = True
            self.aggro_pointer_timer = 180

        else:

          # Boss becomes frenzy
          if self.is_boss and self.hp < self.max_hp // 2:
            self.chase_cooldown_placeholder = 60

            # Frenzy icon
            frenzy_pointer_rect = self.frenzy_pointer.get_rect(
              midbottom = (
                self.rect.midtop[0],
                self.rect.midtop[1] - 5 # Slightly to the top of the enemy's head
              )
            )    
            self.display.blit(self.frenzy_pointer, frenzy_pointer_rect)


            if not self.got_frenzy: # Prevents re-looping
              self.strength += 100 # Damage boost
              self.damage = random.randint(self.strength - 3, self.strength + 3) # Reassign updated damage value
              self.got_frenzy = True

          self.chase(player)

          # ============== PROJECTILES FOR RANGED ENEMIES ==============
          self.handle_projectiles(self.display, self.projectile_list)

        if self.destination_tile:
          self.move()


    self.display.blit(self.image, self.rect)
    self.handle_aggro_pointer() # Rendering the aggro pointer on top of the enemy's own image
