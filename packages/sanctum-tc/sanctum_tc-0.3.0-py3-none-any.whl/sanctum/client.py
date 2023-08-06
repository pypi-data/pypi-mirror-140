import aiohttp

from .utils import _to_json
from .exceptions import HTTPException, NotFound

__all__ = ("HTTPClient", )


class HTTPClient:
    def __init__(self, api_url: str, token: str) -> None:
        self.api_url = api_url
        self.session = aiohttp.ClientSession(headers={"User-Agent": "Sanctum-TC (https://gitlab.com/lightning-bot/sanctum-tc.git)",
                                                      "Authorization": f"Bearer {token}"})

    async def close(self):
        """Closes the client session"""
        await self.session.close()

    async def request(self, method: str, path: str, **kwargs) -> dict:
        """Makes a request to the api.

        Parameters
        ----------
        method : str
            The method to use to send a request to the route. GET, PUT, POST, DELETE
        path : str
            The path to send the request to.
        """
        url = self.api_url + path

        if data := kwargs.pop("data", None):
            kwargs['headers'] = {'Content-Type': 'application/json'}
            kwargs['data'] = _to_json(data)

        async with self.session.request(method, url, **kwargs) as resp:
            data = await resp.json()
            if 300 > resp.status >= 200:
                return data
            
            if resp.status == 404:
                raise NotFound(resp.status, data)

            raise HTTPException(resp.status, data)

    # Guild state management

    async def get_guild(self, guild_id: int):
        return await self.request("GET", f"/guilds/{guild_id}")

    async def create_guild(self, guild_id: int, payload: dict):
        return await self.request("PUT", f"/guilds/{guild_id}", data=payload)

    async def update_guild(self, guild_id: int, payload: dict):
        return await self.create_guild(guild_id, payload)

    async def leave_guild(self, guild_id: int):
        return await self.request("DELETE", f"/guilds/{guild_id}/leave")

    # Timer management

    async def create_timer(self, payload: dict):
        return await self.request("PUT", "/timers", data=payload)

    async def delete_timer(self, id: int):
        return await self.request("DELETE", f"/timers/{id}")

    async def get_timer(self, id: int):
        return await self.request("GET", f"/timers/{id}")

    async def get_timers(self, *, limit: int = 1):
        return await self.request("GET", "/timers", params={"limit": str(limit)})

    async def get_user_reminders(self, user_id: int, *, limit: int = 10):
        return await self.request("GET", f"/users/{user_id}/reminders", params={"limit": str(limit)})

    async def delete_user_reminder(self, user_id: int, reminder_id: int):
        return await self.request("DELETE", f"/users/{user_id}/reminders/{reminder_id}")
