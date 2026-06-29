import os
import threading
import time

from dotenv import load_dotenv
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

INFO_ERROR_CODES = {
  2104,
  2106,
  2158,
}

class IBKRConnectionCheckApp(EWrapper, EClient):
  """
  Minimal IBKR-app kun for manuell connection check.
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
    Ignorerer vanlige IBKR-info-meldinger og printer ekte warnings/errors.
    """
    if errorCode in INFO_ERROR_CODES:
      return

    print(f"IBKR error {errorCode}: {errorString} (reqId={reqId})")


def main():
  load_dotenv()

  host = os.getenv("IBKR_HOST", "127.0.0.1")
  port = int(os.getenv("IBKR_PORT", "7497"))
  client_id = int(os.getenv("IBKR_CLIENT_ID", "180"))

  app = IBKRConnectionCheckApp()

  print(f"Connecting to IBKR at {host}:{port} with client_id={client_id}")

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
    if not app.connected_event.wait(10):
      raise TimeoutError("Timed out waiting for IBKR nextValidId callback.")

    print("Connected successfully.")
    print(f"Next valid order id: {app.next_order_id}")

  finally:
    app.disconnect()
    time.sleep(1)


if __name__ == "__main__":
  main()