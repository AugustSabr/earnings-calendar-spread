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


class IBKRClient(EWrapper, EClient):
  """
  Felles IBKR-klient for broker-operasjoner.
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
    Callback når contract details-responsen er ferdig.
    """
    self.contract_details_event.set()

  def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
    """
    Ignorerer vanlige IBKR-info-meldinger og printer ekte feil/warnings.
    """
    if errorCode in INFO_ERROR_CODES:
      return

    print(f"IBKR error {errorCode}: {errorString} (reqId={reqId})")

  def connect_and_start(
    self,
    host: str,
    port: int,
    client_id: int,
    timeout: int = 10,
  ) -> None:
    """
    Kobler til IBKR og starter reader-thread.
    """
    self.connect(
      host,
      port,
      clientId=client_id,
    )

    thread = threading.Thread(
      target=self.run,
      daemon=True,
    )
    thread.start()

    if not self.connected_event.wait(timeout):
      raise TimeoutError("Timed out waiting for IBKR nextValidId callback.")

  def disconnect_and_wait(self) -> None:
    """
    Kobler fra IBKR.
    """
    self.disconnect()
    time.sleep(1)

  def get_stock_contract_details(
    self,
    symbol: str,
    primary_exchange: str | None = None,
    timeout: int = 10,
  ):
    """
    Henter contract details for én aksje.
    """
    self.contract_details = []
    self.contract_details_event.clear()

    contract = make_stock_contract(
      symbol=symbol,
      primary_exchange=primary_exchange,
    )

    self.reqContractDetails(
      1,
      contract,
    )

    if not self.contract_details_event.wait(timeout):
      raise TimeoutError("Timed out waiting for IBKR contract details.")

    return self.contract_details


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