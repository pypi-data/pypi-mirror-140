import unittest
from senkalib.caaj_journal import CaajJournal
from decimal import Decimal
from senkalib.caaj_journal_amount import CaajJournalAmount
from senkalib.caaj_journal_meta import CaajJournalMeta
from senkalib.caaj_journal_side import CaajJournalSide

class TestCaajJounal(unittest.TestCase):
  def test_init(self):
    meta = CaajJournalMeta('2022-01-12 11:11:11', 'platform', 
      '0x36512c7e09e3570dfc53176252678ee9617660550d36f4da797afba6fc55bba6', 'hello world')
    amounts = [CaajJournalAmount('juno', 'ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED', 
      '3a2570c5-15c4-2860-52a8-bff14f27a236', Decimal('0.005147'))]
    caaj_debit = CaajJournalSide('0x111111111111111111111', '0x222222222222222222222', 'LEND', amounts)
    caaj_credit = CaajJournalSide('0x222222222222222222222', '0x111111111111111111111', 'LEND', amounts)
    cj = CaajJournal(meta, caaj_debit, caaj_credit)
    assert cj.meta.time == '2022-01-12 11:11:11'
    assert cj.meta.platform == 'platform'
    assert cj.meta.transaction_id == '0x36512c7e09e3570dfc53176252678ee9617660550d36f4da797afba6fc55bba6'
    assert cj.meta.comment == 'hello world'
    assert cj.debit.side_from == '0x111111111111111111111'
    assert cj.debit.side_to == '0x222222222222222222222'
    assert cj.credit.side_from == '0x222222222222222222222'
    assert cj.credit.side_to == '0x111111111111111111111'
    assert cj.credit.amounts[0].symbol== 'juno'
    assert cj.credit.amounts[0].original_id == 'ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED'
    assert cj.credit.amounts[0].symbol_uuid == '3a2570c5-15c4-2860-52a8-bff14f27a236'
    assert cj.credit.amounts[0].amount == Decimal('0.005147')

if __name__ == '__main__':
  unittest.main()