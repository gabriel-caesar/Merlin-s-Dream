import pygame

class ScreenVeil():
  def __init__(self, display: pygame.Surface):
    self.image = pygame.Surface((640, 360))
    self.rect = self.image.get_rect()
    self.toggle = False
    self.alpha_value = 0
    self.fade = None
    self.display = display
  
  def update(self):

    if self.toggle:
      self.image.set_alpha(128)        
      self.image.fill("#000000")
      self.display.blit(self.image, self.rect)

    if self.fade == 'in':
      if self.alpha_value <= 255:
        self.alpha_value += 4

      self.image.set_alpha(self.alpha_value)
      self.image.fill("#000000")
      self.display.blit(self.image, self.rect)

    if self.fade == 'out':
      if self.alpha_value > 0:
        self.alpha_value -= 4

      self.image.set_alpha(self.alpha_value)
      self.image.fill("#000000")
      self.display.blit(self.image, self.rect)