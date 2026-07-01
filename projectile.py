from __future__ import annotations
import pygame
import random
from typing import TYPE_CHECKING
from hit_effect import HitEffect
if TYPE_CHECKING:
  from entity import Entity
  from sound_manager import SoundManager
  from enemy import Enemy
  from main import Player

MAGIC_BOLT_COLOR = "#daf0ff"
ARROW_COLOR = "#8EA7AE"
ENEMY_BB_COLOR = "#FF0000"
FIRE_BOLT_COLOR = "#FF8400"
SHADOW_BOLT_COLOR = "#9A1FE7"

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
    has_particles: bool = False,
    absolute_direction: str | None = None, # Radial Blast
    enemies_list: list[Enemy] | None = None
  ):
    
    self.absolute_direction = absolute_direction
    self.sound_manager = sound_manager
    self.caster = caster
    self.name = name
    self.enemies_list = enemies_list

    if name == 'magic_bolt':
      self.color = MAGIC_BOLT_COLOR
      self.bb_color = MAGIC_BOLT_COLOR
      self.rect = pygame.Rect(origin[0], origin[1], 4, 4) 
      self.speed = 6

    if name == 'fire_bolt' or name == 'radial_blast':
      if 'shadow' in self.caster.name:
        self.color = SHADOW_BOLT_COLOR
      else:
        self.color = FIRE_BOLT_COLOR

      self.bb_color = ENEMY_BB_COLOR

      if self.caster.name == 'shadow caster boss':
        self.rect = pygame.Rect(origin[0], origin[1], 12, 12) # Making the shadow bolt bigger
      else:
        self.rect = pygame.Rect(origin[0], origin[1], 6, 6) 

      self.speed = 2

    if name == 'meteor':
      self.color = FIRE_BOLT_COLOR
      self.bb_color = ENEMY_BB_COLOR
      self.rect = pygame.Rect(origin[0], origin[1], 12, 12) 
      self.speed = 2

    if name == 'ranged_hit':
      self.bb_color = ENEMY_BB_COLOR
      self.rect = pygame.Rect(origin[0], origin[1], 8, 8)
      self.color = ARROW_COLOR
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

    if name != 'radial_blast':

      if name == 'meteor':
        self.direction = pygame.math.Vector2(self.target) - pygame.math.Vector2(self.rect.center)
      else:
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

      if not self.absolute_direction: # Regular bolt
        p.pos[0] += self.direction.x * p.speed
        p.pos[1] += self.direction.y * p.speed

      else: # Radial blast bolts
        p.pos[0] += p.speed
        p.pos[1] += p.speed

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

    # Target can be an entity or just a tuple position
    if self.name == 'meteor':
      target_center = self.target # If it is a pygame.Rect
    else:
      target_center = self.target.rect.center # If it is a Entity

    self.direction = pygame.math.Vector2(target_center) - pygame.math.Vector2(self.rect.center)
    if self.direction.length() > 0:
      self.direction = self.direction.normalize()
    self.pos[0] += self.direction.x * self.speed
    self.pos[1] += self.direction.y * self.speed

    self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    # =================== HANDLING THE METEOR PROJECTILES
    if self.name == 'meteor':
      if self.enemies_list:
        for e in self.enemies_list:

          # If the meteor lands on an enemy
          if self.rect.colliderect(e.rect):

            # Handle blast effect and impact sound
            hit_effect = HitEffect(target=e, type='fire_bolt')
            self.caster.hit_effects_list.append(hit_effect)
            self.sound_manager.sounds['fire_bolt']['impact'].play()

            # Handle enemy taking damage from the meteor impact
            e.take_damage(
              dmg=self.dmg, 
              is_enemy=self.is_enemy, 
              bb_color=self.bb_color,
              sound_manager=self.sound_manager
            )
            e.calculate_current_bar_width(type='hp') # Recalculates the new amount of hp after the hit

            # Post the screen shaker event
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 12, duration=3, shake_factor=4))

            return 1 # Tells the receiver to kill the projectile

      # If the meteor lands on the ground
      if self.rect.collidepoint(target_center): 
        hit_effect = HitEffect(target=target_center, type='firestorm')
        self.caster.hit_effects_list.append(hit_effect)
        self.sound_manager.sounds['fire_bolt']['impact'].play()

        # Post the screen shaker event
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 12, duration=3, shake_factor=4))

        return 1 # Tells the receiver to kill the projectile

    # =================== HANDLING REGULAR PROJECTILES LIKE FIRE BOLT ===================
    else:
      if self.rect.colliderect(self.target.rect):
        self.target.take_damage(
          self.dmg, 
          is_enemy=self.is_enemy, 
          bb_color=self.bb_color,
          sound_manager=self.sound_manager
        )
        self.target.calculate_current_bar_width(type='hp')

        # Populate the hit effect list:
        if self.caster.name == 'shadow caster':
          # Custom shadow bolt 
          hit_effect = HitEffect(target=self.target, type='magic_bolt')
          self.sound_manager.sounds['fire_bolt']['impact'].play()          

        else:
          hit_effect = HitEffect(target=self.target, type=self.name)

        self.caster.hit_effects_list.append(hit_effect)

        # Projectile impact sound
        match self.name:
          case 'fire_bolt':
            if self.caster.name == 'shadow caster':
              self.sound_manager.sounds['shadow_bolt']['impact'].play()
            else:
              self.sound_manager.sounds['fire_bolt']['impact'].play()
              
          case 'magic_bolt':
            self.sound_manager.sounds['magic_bolt']['impact'].play()          

          case 'ranged_hit':
            self.sound_manager.sounds['arrow']['impact'].play()          

        return 1 # Tells the receiver to kill the projectile
        
    return 0 # Do nothing with the projectile


class RadialBlast():
  def __init__(
      self, 
      entity: Entity,
      origin: list, 
      sound_manager: SoundManager,
      display: pygame.Surface,
  ):
    self.origin = origin
    self.sound_manager=sound_manager
    self.display=display
    self.entity = entity
    self.directions = ['s','n','e','w','ne','nw','sw','se']
    self.firebolts: list[Projectile] = []
    self.bolts_already_created = False
    self.stop = 0
    self.bolts_timer = 120


  def create_firebolts(self) -> None:
    # Create a firebolt for each direction
    for dir in self.directions:

      # This is the same logic used for the fire bolt damage calculation
      d1 = self.entity.intelligence - 10
      d2 = self.entity.intelligence + 40
      base_damage = random.randint(d1, d2)

      # Applying it to the code
      firebolt_dmg = base_damage

      firebolt = Projectile(
        caster=self.entity,
        name='radial_blast',
        origin=self.origin,
        dmg_value=firebolt_dmg,
        target={},
        sound_manager=self.sound_manager,
        display=self.display,
        absolute_direction=dir,
        has_particles=True
      )
      self.firebolts.append(firebolt)

  # Name cast_to comes from the idea 'cast to north, cast to east...'
  def cast_to(self, enemies_list: list[Enemy] | None, player_enemy: Player | None = None) -> int:

    if self.bolts_timer > 0:
      self.bolts_timer -= 1
    else:
      self.firebolts.clear()

    if self.firebolts:
      for bolt in self.firebolts:

        # Flame particles
        if bolt.particles:
          bolt.run_particles()
          bolt.project_particles()

        # Checking collision with an enemy
        if enemies_list:
          for e in enemies_list:
            if e.rect.colliderect(bolt.rect) and e.alive:

              # Prevents game crash if this bolt is not
              # in the firebolts array by any reason
              if bolt in self.firebolts:
                self.firebolts.remove(bolt)

              e.take_damage(
                dmg=bolt.dmg, 
                is_enemy=bolt.is_enemy, 
                bb_color=bolt.bb_color,
                sound_manager=bolt.sound_manager
              )
              e.calculate_current_bar_width(type='hp')

              # Populate the hit effect list:
              hit_effect = HitEffect(target=e, type='fire_bolt')
              self.entity.hit_effects_list.append(hit_effect)

              # Play fire bolt sound
              bolt.sound_manager.sounds['fire_bolt']['impact'].play()

        elif player_enemy: # If an enemy is casting this spell
          if player_enemy.rect.colliderect(bolt.rect) and player_enemy.alive:
              # Prevents game crash if this bolt is not
              # in the firebolts array by any reason
              if bolt in self.firebolts:
                self.firebolts.remove(bolt)

              player_enemy.take_damage(
                dmg=bolt.dmg, 
                is_enemy=bolt.is_enemy, 
                bb_color=bolt.bb_color,
                sound_manager=bolt.sound_manager
              )
              player_enemy.calculate_current_bar_width(type='hp')

              # Populate the hit effect list:
              hit_effect = HitEffect(target=player_enemy, type='magic_bolt')
              player_enemy.hit_effects_list.append(hit_effect)

              # Play fire bolt sound
              bolt.sound_manager.sounds['shadow_bolt']['impact'].play()

        match bolt.absolute_direction:
          case 'n':
            bolt.pos[0] = self.entity.rect.center[0]
            bolt.pos[1] -= bolt.speed

          case 's':
            bolt.pos[0] = self.entity.rect.center[0]
            bolt.pos[1] += bolt.speed

          case 'w':
            bolt.pos[0] -= bolt.speed
            bolt.pos[1] = self.entity.rect.center[1]
          
          case 'e':
            bolt.pos[0] += bolt.speed
            bolt.pos[1] = self.entity.rect.center[1]

          case 'ne':
            bolt.pos[0] += bolt.speed
            bolt.pos[1] -= bolt.speed

          case 'nw':
            bolt.pos[0] -= bolt.speed
            bolt.pos[1] -= bolt.speed

          case 'sw':
            bolt.pos[0] -= bolt.speed
            bolt.pos[1] += bolt.speed

          case 'se':
            bolt.pos[0] += bolt.speed
            bolt.pos[1] += bolt.speed


        bolt.rect.center = (int(bolt.pos[0]), int(bolt.pos[1]))
        pygame.draw.rect(
          surface=bolt.display, 
          color=bolt.color, 
          rect=bolt.rect
        )

      return 0
    else:
      return 1