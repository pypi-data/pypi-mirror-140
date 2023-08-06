from typing import List
from senkalib.caaj_journal_amount import CaajJournalAmount
from senkalib.caaj_journal_meta import CaajJournalMeta
from senkalib.caaj_journal_side import CaajJournalSide

class CaajJournal:
  def __init__(self, meta:CaajJournalMeta = None, debit:CaajJournalSide = None, credit:CaajJournalSide = None):
    self.meta = meta
    self.debit = debit
    self.credit = credit