from __future__ import annotations

import pygame
import utils

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from entity import Entity
  from enemy import Enemy

class HitEffect():
  """Graphical animation for meele and ranged attacks"""
  def __init__(self, target: Entity | Enemy, type: str):

    if type == 'slash':
      slash_imgs = utils.get_sprites(['effects', 'slash_effect'], 'meele_slash')
      slash_imgs_list = list(slash_imgs.values())
      self.animation_frames = slash_imgs_list

    elif type == 'ranged_hit':
      ranged_hit = utils.get_sprites(['effects', 'ranged_hit_effect'], 'hit')
      ranged_hit_list = list(ranged_hit.values())
      self.animation_frames = ranged_hit_list

    elif type == 'magic_bolt':
      magic_bolt_effect = utils.get_sprites(['effects', 'magic_bolt_effect'], 'magic_vortex')
      effect_list = list(magic_bolt_effect.values())
      self.animation_frames = effect_list

    elif type == 'fire_bolt' or type == 'firestorm':
      magic_bolt_effect = utils.get_sprites(['effects', 'fire_bolt_effect'], 'effect')
      effect_list = list(magic_bolt_effect.values())
      self.animation_frames = effect_list

    elif type == 'teletransport':
      tp_effect = utils.get_sprites(['effects', 'tp_effect'], 'spark')
      effect_list = list(tp_effect.values())
      self.animation_frames = effect_list

    self.animation_index = 0
    self.image = self.animation_frames[0]

    if type == 'teletransport':
      target_pos = (target.center[0], target.center[1] - 5)
    elif type == 'firestorm':
      target_pos = (target[0], target[1])
    else:
      target_pos = target.rect.center

    self.rect = self.image.get_rect(center=target_pos)

  def run_animation(self, display: pygame.Surface) -> str:
    if self.animation_frames:
      self.animation_index += 0.2

      if self.animation_index > len(self.animation_frames):
        self.animation_frames = []
        self.image = None
        return 'destroy'
      
      else:
        self.image = self.animation_frames[int(self.animation_index)]
        display.blit(self.image, self.rect)
        return 'animate'

  def update(self, display: pygame.Surface) -> str:
    return self.run_animation(display)
    