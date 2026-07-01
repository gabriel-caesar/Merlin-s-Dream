from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
  pass

class WarningElement(TypedDict):
    title: str
    content: str
    raw_text: str

class WarningManager():
  def __init__(self):
    self.timer = 240
    self.warning_elements: list[WarningElement] = []

  def update(self) -> None:     
        
    if self.timer > 0 and self.warning_elements:
      self.timer -= 1
    
    else:
      for el in self.warning_elements:
        el['content'].hide()
        el['title'].hide()
      self.warning_elements.clear()

    