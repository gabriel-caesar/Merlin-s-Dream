from __future__ import annotations
import pygame
import utils
import random
from events.damage_bubble import DamageBubble

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from projectile import Projectile
  from sound_manager import SoundManager

class Entity(pygame.sprite.Sprite):
  def __init__(
    self, 
    tile: dict, 
    idle: list[pygame.Surface],
    strength: int,
    intelligence: int,
    haste: int,
    hp: int,
    mana: int,
    level: int,
    xp: int,
    max_xp: int
  ):
    pygame.sprite.Sprite.__init__(self)
    self.image = idle[0]
    self.on_tile = tile # Where the character is on top of
    self.rect = self.image.get_rect(midbottom=self.on_tile['hover_area'].center)
    self.animation_state = 'idle'
    self.animation_frames = idle
    self.animation_index = 0
    self.vanish_timer = 180

    self.destination_tile = {}
    self.facing = 'front'
    self.pos = pygame.Vector2(self.rect.midbottom)
    self.flip = False
    self.target = []
    self.direction = pygame.Vector2()
    self.alive = True
    self.hit_effects_list = []
    self.learned_spells = []

    self.level = level
    self.strength = strength + self.level * 3
    self.intelligence = intelligence + self.level * 3
    self.haste = haste + self.level
    self.max_hp = hp + self.level * 2
    self.hp = hp + self.level * 2
    self.max_mana = mana + self.level * 2 + self.intelligence
    self.mana = mana + self.level * 2 + self.intelligence
    self.xp = xp
    self.max_xp = max_xp

  def move(self) -> None:
    destination = self.destination_tile['hover_area'].center
    origin = self.rect.midbottom

    # Stop moving
    if destination == origin:
      self.on_tile = self.destination_tile
      self.destination_tile = {}
      return
    
    self.direction = pygame.math.Vector2(destination) - pygame.math.Vector2(origin)
    if self.direction.length() > 0:
      self.direction = self.direction.normalize()
    self.pos[0] += self.direction.x * self.speed
    self.pos[1] += self.direction.y * self.speed

    self.rect.midbottom = (int(self.pos[0]), int(self.pos[1]))

  def combat(self, ranged: str) -> None:
    if ranged:
      pass
    pass

  def is_dead(self, enemies_list: list = []) -> bool:
    if self.hp <= 0:

      if enemies_list:
        enemies_list = list(filter(lambda e: e.hp > 0, enemies_list))

      return True
    
  def take_damage(
    self, 
    dmg: int, 
    sound_manager: SoundManager,
    bb_color: str = '#ffffff', 
    is_enemy: bool = False
  ) -> None:
    
    # Caping the damage received
    if self.hp - dmg <= 0:
      self.hp = 0
    else:
      self.hp -= dmg

    new_damage_bb = DamageBubble(dmg, bb_color, 14, self.rect.midtop)
    utils.event_manager.append(new_damage_bb)

    # If it is an enemy entity
    if is_enemy:
      # Recalculate its hp points info
      creature_info_font = pygame.font.Font('./font/Avqest-eeel.ttf', 11)
      self.hp_points_surf = creature_info_font.render(f'{self.hp}/{self.max_hp}', True, '#ffffff')

  def run_hit_animation(self, display: pygame.Surface) -> None:
    if self.hit_effects_list:
      for effect in self.hit_effects_list:
        decision = effect.update(display)
        if decision == 'destroy':
          self.hit_effects_list.remove(effect)

  def handle_projectiles(self, display: pygame.Surface, projectiles: list[Projectile]) -> None:
    if projectiles:
      for p in projectiles:
        pygame.draw.rect(display, p.color, p.rect)
        kill = p.cast()
        if kill:
          projectiles.remove(p)