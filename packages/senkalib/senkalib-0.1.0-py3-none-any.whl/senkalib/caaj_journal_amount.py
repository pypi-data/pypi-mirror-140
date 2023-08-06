from typing import List
from decimal import Decimal

class CaajJournalAmount:
  def __init__(self, symbol:str, original_id:str, symbol_uuid:str, amount:Decimal):
    self.symbol = symbol
    self.original_id = original_id
    self.symbol_uuid = symbol_uuid
    self.amount = amount