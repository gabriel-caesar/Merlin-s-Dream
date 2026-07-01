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
  from warning_manager import WarningManager

class SpellCaster():
  def __init__(
    self, 
    entity: Entity, 
    display: pygame.Surface, 
    sound_manager: SoundManager,
    warning_manager: WarningManager | None
  ):
    self.entity = entity
    self.display = display
    self.sound_manager = sound_manager  
    self.warning_manager = warning_manager
    self.firestorm_casting_timer = 0
    self.meteor_timer = 0

  def cast_magicbolt(self, spell_data: dict) -> None | str:
    mana_cost = spell_data['cost']

    # Handles edge case warnings to provide better gameplay
    self.handle_warnings(mana_cost=mana_cost, spell_name='magic_bolt')
    
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
    # Calculating the fire bolt damage
    d1 = self.entity.intelligence - 10
    d2 = self.entity.intelligence + 40
    fire_bolt_damage = random.randint(d1, d2)

    mana_cost = spell_data['cost']
    damage = fire_bolt_damage
    spell_cooldown = spell_data['cooldown']

    # Handles edge case warnings to provide better gameplay
    self.handle_warnings(mana_cost=mana_cost, spell_name='fire_bolt')

    # If there's no target, return
    if not self.entity.target:
      return
    
    # If there is a target, it will be created after the check
    target = self.entity.target[1]
    
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

    # Handles edge case warnings to provide better gameplay
    self.handle_warnings(mana_cost=mana_cost, spell_name='teletransport')

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

  def cast_radial_blast(
    self, 
    spell_data: dict, 
    spell_to_be_cast: RadialBlast | None | str
  ) -> RadialBlast | None | str:
    
    mana_cost = spell_data['cost']
    spell_cooldown = spell_data['cooldown'] # Cooldown to be set

    # Handles edge case warnings to provide better gameplay
    self.handle_warnings(mana_cost=mana_cost, spell_name='radial_blast')

    if self.entity.mana < mana_cost or self.entity.active_cooldowns['radial_blast'] > 0:
      return spell_to_be_cast

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

    # Handles edge case warnings to provide better gameplay
    self.handle_warnings(mana_cost=mana_cost, spell_name='firestorm')

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

  def handle_warnings(self, mana_cost: int, spell_name: str) -> None:
    '''
      Provides feedback to the player as warnings, such as "out of mana",
      "cooldown", etc. It will prevent spam warnings for Merlin's magic bolt
      since this spell is cast as an auto attack and not triggered by a key press.
    '''

    # "warnings" will hold all raw texts from warnings
    # that already exist in warning_manager, preventing warning spams
    warnings = []
    for el in self.warning_manager.warning_elements:
      warnings.append(el['raw_text'])

    if self.entity.mana <= mana_cost:
      warning_text = 'OUT OF MANA'

      # Prevent warning spams if spell is magic bolt
      if spell_name == 'magic_bolt':
        if warning_text not in warnings:
          pygame.event.post(pygame.event.Event(
            pygame.USEREVENT + 14,
            warning=warning_text,
            index='1'
          ))

      else:
        # For clickable spells, don't constraint it
        pygame.event.post(pygame.event.Event(
          pygame.USEREVENT + 14,
          warning=warning_text,
          index='1'
        ))

    if self.entity.distance_from_enemy > self.entity.atk_range:
      warning_text = 'OUT OF RANGE'
      if spell_name == 'magic_bolt':
        if warning_text not in warnings:
          pygame.event.post(pygame.event.Event(
            pygame.USEREVENT + 14,
            warning=warning_text,
            index='2'
          ))

      else:
        pygame.event.post(pygame.event.Event(
          pygame.USEREVENT + 14,
          warning=warning_text,
          index='2'
        ))

    if spell_name != 'magic_bolt':
      warning_text = 'ON COOLDOWN'
      if self.entity.active_cooldowns[spell_name] > 0:
        pygame.event.post(pygame.event.Event(
          pygame.USEREVENT + 14,
          warning=warning_text,
          index='1'
        ))

    if not self.entity.target:
      warning_text = 'NO TARGET'
      if spell_name == 'fire_bolt':
        pygame.event.post(pygame.event.Event(
          pygame.USEREVENT + 14,
          warning=warning_text,
          index='2'
        ))
