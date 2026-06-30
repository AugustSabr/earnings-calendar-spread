import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

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

    self.bid_ask_by_req_id = {}
    self.market_data_events = {}

    self.order_status_by_id = {}
    self.order_events = {}

    self.option_chain_parameters_event = threading.Event()
    self.option_chain_parameters = []

    self.next_request_id = 1
    self.active_contract_details_req_id = None
    self.contract_details_error = None

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
    if reqId != self.active_contract_details_req_id:
      return

    self.contract_details.append(contractDetails)

  def get_contract_details(
    self,
    contract: Contract,
    timeout: int = 10,
  ):
    """
    Henter contract details for en IBKR Contract.
    """
    request_id = self.get_next_request_id()

    self.contract_details = []
    self.contract_details_error = None
    self.contract_details_event.clear()
    self.active_contract_details_req_id = request_id

    self.reqContractDetails(
      request_id,
      contract,
    )

    try:
      if not self.contract_details_event.wait(timeout):
        raise TimeoutError("Timed out waiting for IBKR contract details.")

      if self.contract_details_error:
        raise ValueError(self.contract_details_error)

      return self.contract_details

    finally:
      self.active_contract_details_req_id = None

  def contractDetailsEnd(self, reqId):
    """
    Callback når contract details-responsen er ferdig.
    """
    if reqId != self.active_contract_details_req_id:
      return

    self.contract_details_event.set()

  def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
    """
    Ignorerer vanlige IBKR-info-meldinger og printer ekte feil/warnings.
    """
    if errorCode in INFO_ERROR_CODES:
      return
    
    if reqId == self.active_contract_details_req_id:
      self.contract_details_error = f"IBKR error {errorCode}: {errorString}"
      self.contract_details_event.set()
      return

    print(f"IBKR error {errorCode}: {errorString} (reqId={reqId})")

  def error(self, reqId, *args):
    """
    Callback for IBKR errors/warnings.
    - Støtter både gammel og ny IBKR API-signatur
    - Ignorerer vanlige IBKR-info-meldinger og printer ekte feil/warnings.
    """
    if len(args) == 2:
      errorCode, errorString = args
      advancedOrderRejectJson = ""

    elif len(args) == 3:
      errorCode, errorString, advancedOrderRejectJson = args

    elif len(args) == 4:
      _errorTime, errorCode, errorString, advancedOrderRejectJson = args

    else:
      print(f"Unknown IBKR error callback format: reqId={reqId}, args={args}")
      return

    if errorCode in INFO_ERROR_CODES:
      return

    if reqId == self.active_contract_details_req_id:
      self.contract_details_error = f"IBKR error {errorCode}: {errorString}"
      self.contract_details_event.set()
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

  def get_next_request_id(self) -> int:
    """
    Returnerer neste lokale request id.
    """
    request_id = self.next_request_id
    self.next_request_id += 1
    return request_id

  def orderStatus(
    self,
    orderId,
    status,
    filled,
    remaining,
    avgFillPrice,
    permId,
    parentId,
    lastFillPrice,
    clientId,
    whyHeld,
    mktCapPrice,
  ):
    self.order_status_by_id[orderId] = {
      "status": status,
      "filled": filled,
      "remaining": remaining,
      "avg_fill_price": avgFillPrice,
      "last_fill_price": lastFillPrice,
    }

    event = self.order_events.get(orderId)
    if event:
      event.set()

  def place_order(
    self,
    contract: Contract,
    order: Order,
    wait_for_status: bool = True,
    timeout: int = 10,
  ) -> int:
    """
    Sender en ordre til TWS/IBKR.
    - order.transmit styrer om ordren faktisk transmitteres.
    - transmit=False kan brukes for staged/untransmitted ordre.
    """
    if self.next_order_id is None:
      raise ValueError("next_order_id is not available.")

    order_id = self.next_order_id
    self.next_order_id += 1

    event = threading.Event()
    self.order_events[order_id] = event

    self.placeOrder(
      order_id,
      contract,
      order,
    )

    if wait_for_status:
      event.wait(timeout)

    return order_id