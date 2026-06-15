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

  def cast_firebolt(self, spell_data: dict) -> None:
    if self.entity.target:
      target = self.entity.target[1]
      spell_cooldown = spell_data['cooldown']
      mana_cost = spell_data['cost']

      if self.entity.mana >= mana_cost and self.entity.distance_from_enemy <= self.entity.atk_range + 120:
        if self.entity.active_cooldowns['fire_bolt'] == 0 and target:
          self.sound_manager.sounds['fire_bolt']['cast'].play()
          fire_bolt = Projectile(
            caster=self.entity,
            name='fire_bolt',
            origin=(
              self.entity.rect.center[0],
              self.entity.rect.center[1] - 4,
            ),
            dmg_value=300,
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
    if self.entity.active_cooldowns['teletransport'] <= 0:
      mana_cost = spell_data['cost']
      spell_cooldown = spell_data['cooldown'] # Cooldown to be set

      tp_effect = HitEffect(target=to, type='teletransport')
      self.entity.hit_effects_list.append(tp_effect)

      self.entity.rect.midbottom = to.center
      self.entity.pos = list(to.center) # Transforming a tuple to list so it becomes mutable
      self.entity.destination_tile = None 
      self.entity.use_mana(mana_cost)
      self.entity.active_cooldowns['teletransport'] = spell_cooldown