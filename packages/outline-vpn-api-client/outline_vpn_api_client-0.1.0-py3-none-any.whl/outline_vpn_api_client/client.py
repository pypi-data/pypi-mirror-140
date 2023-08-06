from typing import List, Optional

from outline_vpn_api_client.http import ABCHTTPClient, SingleAiohttpClient
from outline_vpn_api_client.types import OutlineKey


class OutlineVPNAPIClient:
    def __init__(
        self, api_url: str, http_client: Optional["ABCHTTPClient"] = None
    ) -> None:
        self.api_url = api_url
        self.http_client = http_client or SingleAiohttpClient()

    async def request(
        self, method: str, endpoint: str, data: Optional[dict] = None
    ) -> dict:
        response = await self.http_client.request_json(endpoint, method, data=data)
        return response

    async def get_keys(self) -> List[OutlineKey]:
        """Get all keys in the server"""
        response = await self.request("get", f"{self.api_url}/access-keys/", {})

        keys = response.get("accessKeys", [])
        return [OutlineKey(**key) for key in keys]

    async def create_key(self) -> OutlineKey:
        """Create a new key"""
        response = await self.request("post", f"{self.api_url}/access-keys/", {})
        return OutlineKey(**response)

    async def delete_key(self, key_id: int) -> bool:
        """Delete a key"""
        response = await self.request("delete", f"{self.api_url}/access-keys/{key_id}")
        return bool(response)

    async def rename_key(self, key_id: int, name: str):
        response = await self.request(
            "put",
            f"{self.api_url}/access-keys/{key_id}/name",
            data={"name": name},
        )
        return bool(response)

    async def add_data_limit(self, key_id: int, limit_bytes: int) -> bool:
        """Set data limit for a key (in bytes)"""
        data = {"limit": {"bytes": limit_bytes}}

        response = await self.request(
            "put", f"{self.api_url}/access-keys/{key_id}/data-limit", data
        )
        return bool(response)

    async def delete_data_limit(self, key_id: int) -> bool:
        """Removes data limit for a key"""
        response = await self.request(
            "delete", f"{self.api_url}/access-keys/{key_id}/data-limit"
        )
        return bool(response)

    async def get_transferred_data(self):
        """Gets how much data all keys have used"""
        response = await self.request("get", f"{self.api_url}/metrics/transfer")
        data = await response.json()
        return data
