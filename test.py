from payu.payu_client import init_payu, PayUError
import time, asyncio
import uuid
from config import UPAY_CALL_URL, MINIAPP_URL

async def test_order():
    client = init_payu()
    try:
        resp = await client.get_order("T4LF5NRB8V251104GUEST000P01")
        print(resp)
    except PayUError as e:
        print("HTTP:", e.status)
        print("HEADERS:", getattr(e, "headers", None))
        print("PAYU JSON:", e.payload)
        print("PAYU TEXT:", e.text)


asyncio.run(test_order())