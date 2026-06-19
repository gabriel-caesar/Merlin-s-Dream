from __future__ import annotations

import pygame
from typing import TYPE_CHECKING
from projectile import Projectile
from hit_effect import HitEffect

if TYPE_CHECKING:
  from entity import Entity
  from sound_manager import SoundManager

class SpellCaster():
  def __init__(self, entity: Entity, display: pygame.Surface, sound_manager: SoundManager):
    self.entity = entity
    self.display = display
    self.sound_manager = sound_manager  

  def cast_magicbolt(self, spell_data: dict) -> None:
    damage = spell_data['dmg']
    spell_cooldown = spell_data['cooldown']
    target = self.entity.target[1]
    auto_attack_cost = spell_data['cost']
    
    if self.entity.mana >= auto_attack_cost and self.entity.distance_from_enemy <= self.entity.atk_range:
      if self.entity.active_cooldowns['magic_bolt'] == 0 and self.entity.target:

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
        self.entity.use_mana(auto_attack_cost)
        self.entity.active_cooldowns['magic_bolt'] = spell_cooldown

  def cast_firebolt(self, spell_data: dict) -> None:
    if self.entity.target:
      damage = spell_data['dmg']
      target = self.entity.target[1]
      spell_cooldown = spell_data['cooldown']
      mana_cost = spell_data['cost']

      if self.entity.mana >= mana_cost and self.entity.distance_from_enemy <= self.entity.atk_range + 120:
        if self.entity.active_cooldowns['fire_bolt'] == 0 and target:

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

  def cast_teletransport(self, to: pygame.Rect, spell_data: dict) -> None:    
    mana_cost = spell_data['cost']
    spell_cooldown = spell_data['cooldown'] # Cooldown to be set

    if self.entity.mana >= mana_cost and self.entity.active_cooldowns['teletransport'] <= 0:
      self.sound_manager.sounds['teletransport']['cast'].play()

      tp_effect = HitEffect(target=to, type='teletransport')
      self.entity.hit_effects_list.append(tp_effect)

      self.entity.rect.midbottom = to.center
      self.entity.pos = list(to.center) # Transforming a tuple to list so it becomes mutable
      self.entity.destination_tile = None 
      self.entity.use_mana(mana_cost)
      self.entity.active_cooldowns['teletransport'] = spell_cooldown

  def cast_radial_blast(self) -> None:
    pass

  def cast_firestorm(self) -> None:
    pass