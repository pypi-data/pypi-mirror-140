import json
import aiohttp
import tornado.options


async def post(path, data=None,
               base_url=tornado.options.options.cube_server,
               result_type="json", **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(base_url + path, json=data, **kwargs) as resp:
            result = await resp.text()
            if result_type == "json":
                result = json.loads(result)
            return result


async def get(path, params=None, base_url=tornado.options.options.cube_server, result_type="json", **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + path, params=params, **kwargs) as resp:
            result = await resp.text()
            if result_type == "json":
                result = json.loads(result)
            return result
