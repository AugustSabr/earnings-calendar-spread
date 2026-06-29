import threading
import time

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper

INFO_ERROR_CODES = {
  2104,
  2106,
  2158,
}

class IBKRContractDetailsApp(EWrapper, EClient):
  """
  Minimal IBKR-app for å hente contract details.
  """
  def __init__(self):
    EClient.__init__(self, self)
    self.connected_event = threading.Event()
    self.contract_details_event = threading.Event()
    self.next_order_id = None
    self.contract_details = []

  def nextValidId(self, orderId):
    """
    Callback fra IBKR når API-tilkoblingen er klar.
    """
    self.next_order_id = orderId
    self.connected_event.set()

  def contractDetails(self, reqId, contractDetails):
    """
    Callback med contract details fra IBKR.
    """
    self.contract_details.append(contractDetails)

  def contractDetailsEnd(self, reqId):
    """
    Callback når IBKR er ferdig med contract details-responsen.
    """
    self.contract_details_event.set()

def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
  """
  Printer IBKR-feil/warnings for debugging.
  """
  if errorCode in INFO_ERROR_CODES:
    print(f"IBKR info {errorCode}: {errorString}")
    return

  print(f"IBKR error {errorCode}: {errorString} (reqId={reqId})")


def make_stock_contract(
  symbol: str,
  primary_exchange: str | None = None,
) -> Contract:
  """
  Lager en enkel STK-kontrakt for amerikansk aksje.
  """
  contract = Contract()
  contract.symbol = symbol.strip().upper()
  contract.secType = "STK"
  contract.exchange = "SMART"
  contract.currency = "USD"

  if primary_exchange:
    contract.primaryExchange = primary_exchange

  return contract


def get_stock_contract_details(
  symbol: str,
  host: str,
  port: int,
  client_id: int,
  primary_exchange: str | None = None,
  timeout: int = 10,
):
  """
  Henter contract details for én aksje fra IBKR.
  """
  app = IBKRContractDetailsApp()

  app.connect(
    host,
    port,
    clientId=client_id,
  )

  thread = threading.Thread(
    target=app.run,
    daemon=True,
  )
  thread.start()

  try:
    if not app.connected_event.wait(timeout):
      raise TimeoutError("Timed out waiting for IBKR nextValidId callback.")

    contract = make_stock_contract(
      symbol=symbol,
      primary_exchange=primary_exchange,
    )

    app.reqContractDetails(
      1,
      contract,
    )

    if not app.contract_details_event.wait(timeout):
      raise TimeoutError("Timed out waiting for IBKR contract details.")

    return app.contract_details
  finally:
    app.disconnect()
    time.sleep(1)