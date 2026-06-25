import pygame_gui

class Warning():
  def __init__(self, gui_elements: dict, name: str):
    self.timer = 120  
    self.elements = gui_elements
    self.name = name
    self.chosen_element = None

    if name == 'OUT OF MANA':
      self.chosen_element = gui_elements['warnings']['1']
    elif name == 'COOLDOWN':
      self.chosen_element = gui_elements['warnings']['1']
    elif name == 'OUT OF RANGE':
      self.chosen_element = gui_elements['warnings']['2']
    elif name == 'NO TARGET':
      self.chosen_element = gui_elements['warnings']['2']

  def update(self) -> int:
    if not self.chosen_element:
      print('\nNo element was found inside Warning().\n')
      return
    
    self.chosen_element['title'].show()
    self.chosen_element['text'].show()

    print(self.timer)

    if self.timer > 0:
      self.timer -= 1
      return 1
    
    else:
      self.chosen_element['title'].hide()
      self.chosen_element['text'].hide()
      return 0

    