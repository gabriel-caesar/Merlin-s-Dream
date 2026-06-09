from __future__ import annotations

import pygame
from typing import TYPE_CHECKING
from projectile import Projectile
from hit_effect import HitEffect

if TYPE_CHECKING:
  from entity import Entity

class SpellCaster():
  def __init__(self, entity: Entity, display: pygame.Surface):
    self.entity = entity
    self.display = display

  def cast_firebolt(self):
    if self.entity.target:
      target = self.entity.target[1]
      fire_bolt_cost = 30

      if self.entity.mana >= fire_bolt_cost and self.entity.distance_from_enemy <= self.entity.atk_range + 120:
        if self.entity.cooldowns['fire_bolt'] == 0 and target:
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
            has_particles=True
          )

          self.entity.projectiles.append(fire_bolt)
          self.entity.use_mana(fire_bolt_cost)
          self.entity.cooldowns['fire_bolt'] = 60