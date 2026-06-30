import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

from earnings_calendar_spreads.brokers.ibkr_contracts import make_stock_contract
from earnings_calendar_spreads.brokers.ibkr_option_chain import (
  IBKROptionChainParameters,
)

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

    self.market_data_events = {}
    self.bid_ask_by_req_id = {}

    self.option_chain_parameters_event = threading.Event()
    self.option_chain_parameters = []

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

  def get_contract_details(
    self,
    contract: Contract,
    timeout: int = 10,
  ):
    """
    Henter contract details for en IBKR Contract.
    """
    self.contract_details = []
    self.contract_details_event.clear()

    self.reqContractDetails(
      1,
      contract,
    )

    if not self.contract_details_event.wait(timeout):
      raise TimeoutError("Timed out waiting for IBKR contract details.")

    return self.contract_details

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

  def securityDefinitionOptionParameter(
    self,
    reqId,
    exchange,
    underlyingConId,
    tradingClass,
    multiplier,
    expirations,
    strikes,
  ):
    self.option_chain_parameters.append(
      IBKROptionChainParameters(
        exchange=exchange,
        underlying_con_id=underlyingConId,
        trading_class=tradingClass,
        multiplier=multiplier,
        expirations=sorted(expirations),
        strikes=sorted(float(strike) for strike in strikes),
      )
    )


  def securityDefinitionOptionParameterEnd(self, reqId):
    self.option_chain_parameters_event.set()

  def get_option_chain_parameters(
    self,
    underlying_symbol: str,
    underlying_con_id: int,
    timeout: int = 10,
  ):
    """
    Henter option chain metadata fra IBKR for en underliggende aksje.
    """
    self.option_chain_parameters = []
    self.option_chain_parameters_event.clear()
  
    self.reqSecDefOptParams(
      200,
      underlying_symbol.strip().upper(),
      "",
      "STK",
      underlying_con_id,
    )
  
    if not self.option_chain_parameters_event.wait(timeout):
      raise TimeoutError("Timed out waiting for IBKR option chain parameters.")
  
    return self.option_chain_parameters

  def get_stock_contract_details(
    self,
    symbol: str,
    primary_exchange: str | None = None,
    timeout: int = 10,
  ):
    """
    Henter contract details for én aksje.
    """
    contract = make_stock_contract(
      symbol=symbol,
      primary_exchange=primary_exchange,
    )

    return self.get_contract_details(
      contract=contract,
      timeout=timeout,
    )

  def tickPrice(self, reqId, tickType, price, attrib):
    """
    Callback for market data-priser.
    """

    if price < 0:
      return

    bid, ask = self.bid_ask_by_req_id.get(reqId, (None, None))

    if tickType == 1:
      bid = price

    if tickType == 2:
      ask = price

    self.bid_ask_by_req_id[reqId] = (bid, ask)

    if bid is not None and ask is not None:
      event = self.market_data_events.get(reqId)
      if event:
        event.set()

  def get_bid_ask(
    self,
    contract,
    req_id: int = 100,
    timeout: int = 10,
  ) -> tuple[float, float]:
    """
    Henter bid/ask for en IBKR Contract.
    """
    self.bid_ask_by_req_id[req_id] = (None, None)

    event = threading.Event()
    self.market_data_events[req_id] = event

    self.reqMktData(
      req_id,
      contract,
      "",
      False,
      False,
      [],
    )

    try:
      if not event.wait(timeout):
        bid, ask = self.bid_ask_by_req_id.get(req_id, (None, None))
        raise TimeoutError(f"Timed out waiting for bid/ask. bid={bid}, ask={ask}")

      bid, ask = self.bid_ask_by_req_id[req_id]
      return bid, ask

    finally:
      self.cancelMktData(req_id)
      self.market_data_events.pop(req_id, None)