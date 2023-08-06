from typing import List
import importlib
import os
import re
from senkalib.chain.transaction_generator import TransactionGenerator
from pandas import DataFrame, pandas
import requests
import io

from senkalib.caaj_journal import CaajJournal

class SenkaLib:
  TOKEN_OERIGINAK_IDS_URL = 'https://raw.githubusercontent.com/ca3-caaip/token_original_id/master/token_original_id.csv'

  @classmethod
  def get_available_chain(cls, blacklist = []) -> List[TransactionGenerator]:
    available_chains = []
    try:
      blacklist.append('__pycache__')
      path = '%s/chain' % os.path.dirname(__file__)
      files = os.listdir(path)
      dirs = sorted([f for f in files if os.path.isdir(os.path.join(path, f)) and f not in blacklist])
  
      for dir in dirs:
        module = importlib.import_module(f"senkalib.chain.{dir}.{dir}_transaction_generator", f"senkalib")
        transaction_generator = list(f"{dir}_transaction_generator")
        transaction_generator[0] = transaction_generator[0].upper()
        transaction_generator = "".join(transaction_generator)
        transaction_generator = re.sub("_(.)",lambda x:x.group(1).upper(), transaction_generator)
        transaction_generator = getattr(module, transaction_generator)
        available_chains.append(transaction_generator)
    except Exception as e:
      f"failed to load senkalib transaction generator: {e}"
      raise e


    return available_chains

  @classmethod
  def get_token_original_ids(cls) -> DataFrame:
    url = cls.TOKEN_OERIGINAK_IDS_URL
    res = requests.get(url).content
    df = pandas.read_csv(io.StringIO(res.decode('utf-8')))
    return df

  @classmethod
  def get_caaj_jounal_dicts(cls, caaj_journal_list:List[CaajJournal]) -> list:
    caaj = []
    for caaj_journal in caaj_journal_list:
      debit_amount = list(map(lambda x:  {'token':{'symbol':x.symbol, 'original_id':x.original_id, 'symbol_uuid':x.symbol_uuid}, 'amount': x.amount}, caaj_journal.debit.amounts))
      credit_amount = list(map(lambda x:  {'token':{'symbol':x.symbol, 'original_id':x.original_id, 'symbol_uuid':x.symbol_uuid}, 'amount': x.amount}, caaj_journal.credit.amounts))
      caaj_data = {
        "time": caaj_journal.meta.time,
        "platform": caaj_journal.meta.platform,
        "transaction_id": caaj_journal.meta.transaction_id,
        "debit_title": caaj_journal.debit.title,
        "debit_amounts": debit_amount,
        "debit_from": caaj_journal.debit.side_from,
        "debit_to": caaj_journal.debit.side_to,
        "credit_title": caaj_journal.credit.title,
        "credit_amounts": credit_amount,
        "credit_from": caaj_journal.credit.side_from,
        "credit_to": caaj_journal.credit.side_to,
        "comment": caaj_journal.meta.comment,
      }
      caaj.append(caaj_data)
    return caaj