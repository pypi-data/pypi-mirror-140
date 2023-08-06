from typing import List
from senkalib.caaj_journal_amount import CaajJournalAmount

class CaajJournalSide:
  def __init__(self, side_from:str = None, side_to:str = None, 
    title:str = None, amounts:List[CaajJournalAmount] = None):
    self.side_from = side_from
    self.side_to = side_to
    self.title = title
    self.amounts = amounts