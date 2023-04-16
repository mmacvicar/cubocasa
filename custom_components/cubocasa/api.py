"""Cubo Casa API Client."""
import asyncio
import aiohttp
import json

class CuboClient:
    def __init__(self, session, token=None, url=None):
        if url is None:
            url = "https://iot.cubo.casa"
        if token is None:
            raise ValueError("token is required")
        self.session = session
        self.base_url = url
        self.headers = {"Bearer": token }

    async def _request_with_retry(self, method, url, headers, max_retries, backoff_factor, **kwargs):
        retry = 0

        while retry <= max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(method, url, headers={**self.headers,**headers}, timeout=5, **kwargs) as resp:
                        return resp.status, await resp.json()
            except aiohttp.ClientError as e:
                if retry == max_retries:
                    print(f"Error: {e}")
                    return None

                await asyncio.sleep(backoff_factor ** retry)
                retry += 1

    async def get_device_status(self, device_id, max_retries=3, backoff_factor=2):
        if not isinstance(device_id, int):
            raise ValueError("device_id must be an integer")

        return await self._request_with_retry("GET", f"{self.base_url}/api/device/{device_id}/status/", {}, max_retries, backoff_factor)

    async def list_devices(self, max_retries=3, backoff_factor=2):
        return await self._request_with_retry("GET", f"{self.base_url}/api/device/", {}, max_retries, backoff_factor)

    async def set_device_status(self, device_id, status, max_retries=3, backoff_factor=2):
        if not isinstance(device_id, int):
            raise ValueError("device_id must be an integer")

        if status not in ["open", "close"]:
            raise ValueError("status must be 'open' or 'close'")
        headers = {"Content-Type": "application/json"}
        return await self._request_with_retry("POST", f"{self.base_url}/api/device/{device_id}/", headers, max_retries, backoff_factor, json={"status": status})
