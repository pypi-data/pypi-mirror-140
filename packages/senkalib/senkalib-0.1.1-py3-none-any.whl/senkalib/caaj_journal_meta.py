from typing import List
from decimal import Decimal

class CaajJournalMeta:
  def __init__(self, time:str, platform:str, transaction_id:str, comment:str):
    self.time = time
    self.platform = platform
    self.transaction_id = transaction_id
    self.comment = comment