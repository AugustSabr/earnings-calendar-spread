import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

INFO_ERROR_CODES = {
  2104,
  2106,
  2158,
}

class IBKRConnectionApp(EWrapper, EClient):
  """
  Minimal IBKR-app for å teste at vi kan koble til TWS/IB Gateway.
  """
  def __init__(self):
    EClient.__init__(self, self)
    self.connected_event = threading.Event()
    self.next_order_id = None

  def nextValidId(self, orderId):
    """
    Callback fra IBKR når API-tilkoblingen er klar.
    """
    self.next_order_id = orderId
    self.connected_event.set()

def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
  """
  Printer IBKR-feil/warnings for debugging.
  """
  if errorCode in INFO_ERROR_CODES:
    print(f"IBKR info {errorCode}: {errorString}")
    return

  print(f"IBKR error {errorCode}: {errorString} (reqId={reqId})")


def check_ibkr_connection(
  host: str,
  port: int,
  client_id: int,
  timeout: int = 10,
) -> int:
  """
  Kobler til IBKR og returnerer next_order_id hvis tilkoblingen fungerer.
  """
  app = IBKRConnectionApp()

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

    return app.next_order_id
  finally:
    app.disconnect()
    time.sleep(1)