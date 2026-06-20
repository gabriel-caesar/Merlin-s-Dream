import pygame

class Warning():
  def __init__(self, gui_elements: dict):
    self.timer = 360
    self.elements = gui_elements

  def update(self):
    if self.timer > 0:
      self.timer -= 1