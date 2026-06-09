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

HPBAR_WIDTH = 110

class Enemy(Entity):
  def __init__(
    self, 
    tile: dict, 
    name: str,
    atk_range: int,
    display: pygame.Surface,
    wave: int = 1,
    strength: int = 10,
    intelligence: int = 10,
    haste: int = 5,
    hp: int = 100,
    mana: int = 100,
    level: int = 1,
    xp: int = 0,
    max_xp:int = 100,
  ):
    self.idle_spritesheet = list(utils.get_sprites(['enemies', name], 'idle').values())
    self.running_spritesheet = list(utils.get_sprites(['enemies', name], 'walk').values())
    self.backview_idle_spritesheet = list(utils.get_sprites(['enemies', name, 'backview'], 'backview_idle').values())
    self.backview_running_spritesheet = list(utils.get_sprites(['enemies', name, 'backview'], 'backview_walk').values())
    self.attack_spritesheet = list(utils.get_sprites(['enemies', name, 'attack'], 'attack').values())
    self.backview_attack_spritesheet = list(utils.get_sprites(['enemies', name, 'attack', 'backview'], 'attack').values())

    self.level = level + int(wave * 0.8)

    Entity.__init__(
      self, 
      tile, 
      self.idle_spritesheet,
      strength,
      intelligence,
      haste,
      hp,
      mana,
      self.level,
      xp,
      max_xp
    )

    self.display = display
    self.name = name
    self.patrol_timer = random.randint(90, 240)
    self.patrol_tile = self.on_tile # Never changes after arriving at the destination tile
    self.aggro = False
    self.speed = 0.5
    self.chase_cooldown = 0
    self.xp_value = int(self.level + (wave * 50))

    self.attacking = False
    self.atk_type = None
    self.atk_range = atk_range
    self.atk_cooldown = 0
    self.damage = random.randint(self.strength - 3, self.strength + 3)
    self.projectile_list = []

    # ========== HP BAR GUI ==========
    self.hp_bar_img = pygame.image.load('./assets/ui/enemy_hp_bar.png')
    self.hp_bar_rect = self.hp_bar_img.get_rect(center=(320, 20))
    self.hp_bar_filler = pygame.Rect(
      self.hp_bar_rect.left + 15,
      self.hp_bar_rect.top + 3,
      HPBAR_WIDTH,
      20
    )

    # Filtering any underscore inside name
    if '_' in self.name:
      self.name = self.name.split('_')
      self.name = ' '.join(self.name)

    # Making sure the text is small for longer names
    if len(self.name) > 8:
      self.font = pygame.font.Font('./font/Avqest-eeel.ttf', 14)
    else:
      self.font = pygame.font.Font('./font/Avqest-eeel.ttf', 16)

    self.hpbar_text = self.font.render(self.name.upper(), True, '#ffffff')
    self.hpbar_text_rect = self.hpbar_text.get_rect()

    # ========== LEVEL/HP INFO GUI ==========

    # Panel image
    self.level_container_img = pygame.image.load('./assets/ui/button_image.png')
    self.level_container_img = pygame.transform.scale(self.level_container_img, (100, 15))
    self.level_container_rect = self.level_container_img.get_rect(
      center=(
        self.hp_bar_rect.center[0],
        self.hp_bar_rect.center[1] + 20

      )
    )

    # Level text in the panel image
    creature_info_font = pygame.font.Font('./font/Avqest-eeel.ttf', 11)
    self.level_text_surf = creature_info_font.render(f'Level {self.level}', True, '#ff0000')
    self.level_text_rect = self.level_text_surf.get_rect(
      center=(
        self.level_container_rect.center[0] - 25,
        self.level_container_rect.center[1]
      )
    )

    # HP text in the panel image
    self.hp_points_surf = creature_info_font.render(f'{self.hp}/{self.max_hp}', True, '#ffffff')
    self.hp_points_rect = self.hp_points_surf.get_rect(
      center=(
        self.level_container_rect.center[0] + 25,
        self.level_container_rect.center[1]
      )
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
        if self.facing == 'backview':
          self.animation_frames = self.backview_idle_spritesheet
        else:
          self.animation_frames = self.idle_spritesheet

      # ============== ANIMATION LOOP ==============
      self.animation_index += 0.1
      if self.animation_index > len(self.animation_frames):
        self.animation_index = 0
        if self.attacking: # Finish the enemy attack animation at this point
          self.attacking = False

      self.image = self.animation_frames[int(self.animation_index)]
      
    self.image = pygame.transform.flip(self.image, self.flip, False)

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
        self.atk_type = 'slash' if self.atk_range <= 20 else 'ranged_hit'
        self.attack(player, type=self.atk_type)
        self.chase_cooldown = 120

  def attack(self, player: Player, type: Literal['slash', 'ranged_hit']) -> None:
    # Change the facing direction if the entity is currently attacking and not moving
    self.get_facing_direction(real_target=player)

    if self.atk_cooldown > 0:
      self.atk_cooldown -= 1

    else: 
      if type == 'slash':
        global slash_imgs_list
        player.take_damage(self.damage, bb_color="#ff0000")
        player.calculate_current_bar_width('hp')
        hit_effect = HitEffect(target=player, type=type) # type == slash
        self.hit_effects_list.append(hit_effect)

      elif type == 'ranged_hit':
        self.projectile = Projectile(
          caster=self,
          name=type, 
          origin=self.rect.center, 
          dmg_value=self.damage,
          target=player,
          display=self.display
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
          if self in player.being_targeted_by:
            player.being_targeted_by.remove(self)
          self.alive = False

        self.animation_frames = []
        this_name = self.name.split(' ')
        this_name = '_'.join(this_name)
        self.image = pygame.image.load(f'./assets/enemies/{this_name}/dead.png')

        blood_indicator = pygame.image.load('./assets/cursor/blood_indicator.png')
        self.display.blit(blood_indicator, (self.rect.x - 5, self.rect.y + 12))
        self.vanish_timer -= 1

        if self.vanish_timer == 0:
          self.kill()
          return
        
      else:
        if self.destination_tile:
          self.move() 

        if not self.aggro:
          if self.patrol_timer > 0:
            self.patrol_timer -= 1
          self.patrol(map_data)

          if self.hp < self.max_hp:
            self.aggro = True

        else:
          self.chase(player)

          # ============== PROJECTILES FOR RANGED ENEMIES ==============
          self.handle_projectiles(self.display, self.projectile_list)

        if self.destination_tile:
          self.move()


    self.display.blit(self.image, self.rect)
