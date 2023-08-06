import re
import unittest
from unittest.mock import *
from senkalib.chain.bsc.bsc_transaction_generator import BscTransactionGenerator
from senkalib.chain.osmosis.osmosis_transaction_generator import OsmosisTransactionGenerator
from senkalib.senka_lib import SenkaLib
from senkalib.caaj_journal import CaajJournal
from senkalib.caaj_journal_meta import CaajJournalMeta
from senkalib.caaj_journal_side import CaajJournalSide
from senkalib.caaj_journal_amount import CaajJournalAmount
import os
from decimal import Decimal

class TestSenkaLib(unittest.TestCase):
  def test_get_available_chain(self):
    with patch.object(os, 'listdir', new=TestSenkaLib.mock_listdir):
      chains = SenkaLib.get_available_chain()

      self.assertEqual(chains[0], BscTransactionGenerator)
      self.assertEqual(chains[1], OsmosisTransactionGenerator)

  def test_get_token_original_ids(self):
    token_original_ids_df = SenkaLib.get_token_original_ids()
    result = token_original_ids_df\
      .query('chain == "osmosis" and original_id == "ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2"')
    self.assertEqual(token_original_ids_df['symbol_uuid'][0], 'e7816a15-ce91-0aa8-0508-21d0d19f3aa8')


  def test_get_caaj_jounal_dicts(self):
    meta = CaajJournalMeta('2022-01-12 11:11:11', 'platform', 
      '0x36512c7e09e3570dfc53176252678ee9617660550d36f4da797afba6fc55bba6', 'hello world')
    amounts = [CaajJournalAmount('juno', 'ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED', 
      '3a2570c5-15c4-2860-52a8-bff14f27a236', Decimal('0.005147'))]
    caaj_debit = CaajJournalSide('0x111111111111111111111', '0x222222222222222222222', 'LEND', amounts)
    caaj_credit = CaajJournalSide('0x222222222222222222222', '0x111111111111111111111', 'LEND', amounts)
    caaj_journal = CaajJournal(meta, caaj_debit, caaj_credit)
    caaj_journals = [caaj_journal, caaj_journal]
    caaj_journal_dicts = SenkaLib.get_caaj_jounal_dicts(caaj_journals)
    assert len(caaj_journal_dicts) == 2
    assert caaj_journal_dicts[0]['time'] == '2022-01-12 11:11:11'
    assert caaj_journal_dicts[0]['platform'] == 'platform'
    assert caaj_journal_dicts[0]['transaction_id'] == '0x36512c7e09e3570dfc53176252678ee9617660550d36f4da797afba6fc55bba6'
    assert caaj_journal_dicts[0]['comment'] == 'hello world'
    assert caaj_journal_dicts[0]['debit_from'] == '0x111111111111111111111'
    assert caaj_journal_dicts[0]['debit_to'] == '0x222222222222222222222'
    assert caaj_journal_dicts[0]['credit_from'] == '0x222222222222222222222'
    assert caaj_journal_dicts[0]['credit_to'] == '0x111111111111111111111'
    assert caaj_journal_dicts[0]['credit_amounts'][0]['amount'] == Decimal('0.005147')
    assert caaj_journal_dicts[0]['credit_amounts'][0]['token'] == {
      'symbol':'juno', 
      'original_id':'ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED', 
      'symbol_uuid':'3a2570c5-15c4-2860-52a8-bff14f27a236'
    }
    assert caaj_journal_dicts[0]['debit_amounts'][0]['amount'] == Decimal('0.005147')
    assert caaj_journal_dicts[0]['debit_amounts'][0]['token'] == {
      'symbol':'juno', 
      'original_id':'ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED', 
      'symbol_uuid':'3a2570c5-15c4-2860-52a8-bff14f27a236'
    }

  @classmethod
  def mock_listdir(cls, transaction_hash):
    return ['osmosis', 'bsc']

if __name__ == '__main__':
  unittest.main()
