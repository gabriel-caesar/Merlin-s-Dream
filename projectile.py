from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
from hit_effect import HitEffect
if TYPE_CHECKING:
  from entity import Entity
  from sound_manager import SoundManager

MAGIC_BOLT_COLOR = "#daf0ff"
ARROW_COLOR = "#8EA7AE"
ENEMY_BB_COLOR = "#FF0000"
FIRE_BOLT_COLOR = "#FF8400"

class Particle():
  def __init__(self, rect, origin):
    self.timer = 60
    self.rect = rect
    self.pos = pygame.Vector2(origin)
    self.minifier = [self.rect.width, self.rect.height]
    self.speed = 0.3

class Projectile():
  def __init__(
    self, 
    caster: Entity,
    name: str, 
    origin: list, 
    dmg_value: int, 
    target: dict, 
    sound_manager: SoundManager,
    display: pygame.Surface,
    is_enemy: bool = False,
    has_particles: bool = False
  ):
    
    self.sound_manager = sound_manager
    self.caster = caster
    self.name = name
    if name == 'magic_bolt':
      self.color = MAGIC_BOLT_COLOR
      self.bb_color = MAGIC_BOLT_COLOR
      self.rect = pygame.Rect(origin[0], origin[1], 4, 4) 
      self.speed = 6

    if name == 'fire_bolt':
      self.color = FIRE_BOLT_COLOR
      self.bb_color = ENEMY_BB_COLOR
      self.rect = pygame.Rect(origin[0], origin[1], 6, 6) 
      self.speed = 2

    if name == 'ranged_hit':
      self.color = ARROW_COLOR
      self.bb_color = ENEMY_BB_COLOR
      self.rect = pygame.Rect(origin[0], origin[1], 8, 8)
      self.speed = 6

    self.origin = origin
    self.dmg = dmg_value
    self.pos = pygame.Vector2(origin)
    self.target = target
    self.display = display
    self.took_damage = False
    self.is_enemy = is_enemy
    self.particles = [Particle(pygame.Rect(0,0,0,0), self.rect.center)] if has_particles else []
    self.create_particle_by = 5 

    self.direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)

  def project_particles(self) -> None:

    if self.create_particle_by > 0:
      self.create_particle_by -= 1
    else:
      particle = Particle(
        rect=pygame.Rect(
          self.rect.left,
          self.rect.top,
          self.rect.width,
          self.rect.height,
        ),
        origin=self.rect.center
      )

      self.particles.append(particle)
      self.create_particle_by = 5


  def run_particles(self) -> None:
    for p in self.particles:
      p.pos[0] += self.direction.x * p.speed
      p.pos[1] += self.direction.y * p.speed

      p.rect.center = (int(p.pos[0]), int(p.pos[1]))
      pygame.draw.rect(self.display, self.color, p.rect)

      # Fire particles get smaller as they fly
      p.minifier[0] -= 0.3
      p.minifier[1] -= 0.3
      p.rect.width = int(p.minifier[0])
      p.rect.height = int(p.minifier[1])

      if p.timer > 0:
        p.timer -= 1
      else:
        self.particles.remove(p)

  def cast(self) -> int:
    if self.particles:
      self.run_particles()
      self.project_particles()

    self.direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
    if self.direction.length() > 0:
      self.direction = self.direction.normalize()
    self.pos[0] += self.direction.x * self.speed
    self.pos[1] += self.direction.y * self.speed

    self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    if self.rect.colliderect(self.target.rect):
      self.target.take_damage(
        self.dmg, 
        is_enemy=self.is_enemy, 
        bb_color=self.bb_color,
        sound_manager=self.sound_manager
      )
      self.target.calculate_current_bar_width(type='hp')

      # Populate the hit effect list:
      hit_effect = HitEffect(target=self.target, type=self.name)
      self.caster.hit_effects_list.append(hit_effect)

      # Projectile impact sound
      match self.name:
        case 'fire_bolt':
          self.sound_manager.sounds['fire_bolt']['impact'].play()
        case 'magic_bolt':
          self.sound_manager.sounds['magic_bolt']['impact'].play()          

      return 1
        
    return 0
