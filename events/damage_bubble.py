import pygame
from pathlib import Path
from os import path

# Getting the font path
parent_folder = Path(__file__).parent.parent
font_path = path.join(parent_folder, 'font', 'Avqest-eeel.ttf')

class DamageBubble():
  def __init__(self, value: int, color: str, size: int, pos: tuple):
    self.value = value
    self.timer = 60
    self.speed = 0.5
    self.pos = [pos[0], pos[1]]
    self.color = color
    self.size = size
    self.font = pygame.font.Font(font_path, self.size)
    self.text_surf = self.font.render(str(self.value), True, self.color)
    self.rect = self.text_surf.get_rect(center=(pos[0], pos[1]))

class XPBubble(DamageBubble):
  def __init__(
    self,
    value: str,
    color: str,
    size: int,
    pos: tuple
  ):
    DamageBubble.__init__(
      self,
      value=0,
      color=color,
      size=size,
      pos=pos
    )

    self.text_surf = self.font.render(value, True, self.color)
    self.rect = self.text_surf.get_rect(center=(pos))
    self.timer = 120
    self.speed = 0.3

class RegenBubble(DamageBubble):
  def __init__(
    self,
    value: str,
    color: str,
    size: int,
    pos: tuple
  ):
    DamageBubble.__init__(
      self,
      value=0,
      color=color,
      size=size,
      pos=pos
    )

    self.text_surf = self.font.render(value, True, self.color)
    self.rect = self.text_surf.get_rect(center=(pos))
    self.timer = 120
    self.speed = 0.3