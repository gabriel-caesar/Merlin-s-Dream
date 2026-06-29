from __future__ import annotations

import pygame
import random
from typing import TYPE_CHECKING
from projectile import Projectile, RadialBlast
from hit_effect import HitEffect

if TYPE_CHECKING:
  from entity import Entity
  from sound_manager import SoundManager
  from enemy import Enemy

class SpellCaster():
  def __init__(self, entity: Entity, display: pygame.Surface, sound_manager: SoundManager):
    self.entity = entity
    self.display = display
    self.sound_manager = sound_manager  
    self.firestorm_casting_timer = 0
    self.meteor_timer = 0

  def cast_magicbolt(self, spell_data: dict) -> None | str:
    mana_cost = spell_data['cost']
    
    # If at least of the conditions fail, return a warning
    if (
      self.entity.mana <= mana_cost or
      self.entity.distance_from_enemy > self.entity.atk_range or
      self.entity.active_cooldowns['magic_bolt'] > 0 or
      not self.entity.target
    ):
      return
      # return self.handle_warnings(mana_cost, target='Not existent' if not self.entity.target else self.entity.target)

    # Getting a random damage value based on the caster's intelligence
    d1 = self.entity.intelligence - 3
    d2 = self.entity.intelligence + 3
    damage = random.randint(d1, d2)
    spell_cooldown = spell_data['cooldown']
    target = self.entity.target[1]
    
    magic_bolt = Projectile(
      caster=self.entity,
      name='magic_bolt', 
      origin=self.entity.rect.center, 
      dmg_value=damage,
      target=target,
      display=self.display,
      is_enemy=True,
      sound_manager=self.sound_manager
    )

    self.entity.projectiles.append(magic_bolt)
    self.entity.use_mana(mana_cost)
    self.entity.active_cooldowns['magic_bolt'] = spell_cooldown

  def cast_firebolt(self, spell_data: dict) -> str | None:
    if not self.entity.target: # If there's no target, return
      return
    
    # Calculating the fire bolt damage
    d1 = self.entity.intelligence - 10
    d2 = self.entity.intelligence + 40
    fire_bolt_damage = random.randint(d1, d2)

    damage = fire_bolt_damage
    target = self.entity.target[1]
    spell_cooldown = spell_data['cooldown']
    mana_cost = spell_data['cost']

    # Don't execute if any of these conditions are met
    if (
      self.entity.mana < mana_cost or 
      self.entity.distance_from_enemy > self.entity.atk_range + 120 or
      self.entity.active_cooldowns['fire_bolt'] > 0 
    ):
        return

    self.sound_manager.sounds['fire_bolt']['cast'].play() # Play spell cast sound

    fire_bolt = Projectile(
      caster=self.entity,
      name='fire_bolt',
      origin=(
        self.entity.rect.center[0],
        self.entity.rect.center[1] - 4,
      ),
      dmg_value=damage,
      target=target,
      display=self.display,
      is_enemy=True,
      has_particles=True,
      sound_manager=self.sound_manager
    )

    self.entity.projectiles.append(fire_bolt)
    self.entity.use_mana(mana_cost)
    self.entity.active_cooldowns['fire_bolt'] = spell_cooldown

  def cast_teletransport(self, to: pygame.Rect, spell_data: dict) -> None | str:    
    mana_cost = spell_data['cost']
    spell_cooldown = spell_data['cooldown'] # Cooldown to be set

    if self.entity.mana < mana_cost or self.entity.active_cooldowns['teletransport'] > 0:
      return

    self.sound_manager.sounds['teletransport']['cast'].play()

    tp_effect = HitEffect(target=to, type='teletransport')
    self.entity.hit_effects_list.append(tp_effect)

    self.entity.rect.midbottom = to.center
    self.entity.pos = list(to.center) # Transforming a tuple to list so it becomes mutable
    self.entity.destination_tile = None 
    self.entity.use_mana(mana_cost)
    self.entity.active_cooldowns['teletransport'] = spell_cooldown

  def cast_radial_blast(self, spell_data: dict) -> RadialBlast | None | str:
    mana_cost = spell_data['cost']
    spell_cooldown = spell_data['cooldown'] # Cooldown to be set

    if self.entity.mana < mana_cost or self.entity.active_cooldowns['radial_blast'] > 0:
      return

    radial_blast = RadialBlast(
      entity=self.entity,
      origin=(
        self.entity.rect.center[0] + 2,
        self.entity.rect.center[1] - 5,
      ),
      sound_manager=self.sound_manager,
      display=self.display
    )

    # Play cast sound
    self.sound_manager.sounds['fire_bolt']['cast'].play()

    # Using mana
    self.entity.use_mana(mana_cost)

    # Setting the radial blast cooldown
    self.entity.active_cooldowns['radial_blast'] = spell_cooldown
    
    return radial_blast
    
  def check_if_firestorm_is_available(self, spell_data: dict) -> bool:
    mana_cost = spell_data['cost']
    spell_cooldown = spell_data['cooldown'] # Cooldown to be set

    if self.entity.mana < mana_cost or self.entity.active_cooldowns['firestorm'] > 0:
      return False
    else:
      # Play spell channeling sound effect
      self.sound_manager.sounds['spell_channeling'].play(-1)

      # Using mana
      self.entity.use_mana(mana_cost)

      # Setting the radial blast cooldown
      self.entity.active_cooldowns['firestorm'] = spell_cooldown
      return True
    
  def cast_firestorm(self, to: pygame.Rect, enemies_list: list[Enemy]) -> None:
    self.entity.destination_tile = [] # Stop moving

    # Calculating the meteor damage
    d1 = self.entity.intelligence - 10
    d2 = self.entity.intelligence + 10
    meteor_damage = random.randint(d1, d2)

    if self.firestorm_casting_timer > 0:
      self.firestorm_casting_timer -= 1

      # Making the landing point more sparse
      random_x = random.randint(to.center[0] - 30, to.center[0] + 30)
      random_y = random.randint(to.center[1] - 30, to.center[1] + 30)

      # Adding an interval between each meteor
      if self.meteor_timer > 0:
        self.meteor_timer -= 1

      else:

        # Create a meteor projectile
        meteor = Projectile(
          caster=self.entity,
          name='meteor',
          origin=(
            # Randoming the meteor landing point
            random.randint(0, 640), # Screen Size
            -50, # Off screen
          ),
          dmg_value=meteor_damage,
          target=(random_x, random_y),
          display=self.display,
          is_enemy=True,
          has_particles=True,
          sound_manager=self.sound_manager,
          enemies_list=enemies_list
        )

        # What actually makes the projectiles be rendered
        self.entity.projectiles.append(meteor)

        # Reseting the meteor timer so it has an interval between casts
        self.meteor_timer = 5

    else:
      self.sound_manager.sounds['spell_channeling'].stop()
      self.entity.casting_firestorm = False

  def handle_warnings(self, mana_cost: int, target: Entity | int = 'Not existent') -> None | str:
    # Handling warnings
    if self.entity.distance_from_enemy > self.entity.atk_range + 120:
      return 'OUT OF RANGE'
    elif self.entity.mana < mana_cost:
      return 'OUT OF MANA'
    elif self.entity.active_cooldowns['fire_bolt'] > 0:
      return 'SPELL ON COOLDOWN'
    
    # Not existent for no-target spells (like tp and radial_blast)
    elif not target and target != 'Not existent':
      return 'NO TARGET'
    else:
      return None