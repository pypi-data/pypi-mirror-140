import httpx
from httpx import ConnectError
from httpx import ConnectTimeout
from fake_useragent import UserAgent
from scan.response import Response
from scan.common import logger


class Downloader(object):
    def __init__(self):
        self.client = None
        self.ua = UserAgent()

    async def gen_headers(self):
        try:
            ua = self.ua.random
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                          'q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en;q=0.9',
                'user-agent': ua
            }
            return headers
        except Exception as e:
            await logger.error(f'gen ua error: {e}')

    async def close(self):
        try:
            await self.client.aclose()
        except:
            pass

    @staticmethod
    async def log_request(request):
        pass

    @staticmethod
    async def log_response(response):
        """
        日志钩子
        """
        request = response.request
        if response.status_code not in [200, 301, 302]:
            await logger.error(f'{response.status_code}  {request.url}')
        else:
            await logger.info(f'{response.status_code}  {request.url}')

    async def request(self, url, params=None, headers=None, cookies=None, auth=None, proxies=None, allow_redirects=True,
                      content=None, data=None, files=None, json=None, timeout=30, cycle=3):
        if data or json or content:
            method = 'POST'
        else:
            method = 'GET'
        if not headers:
            headers = await self.gen_headers()
        for _ in range(cycle):
            try:
                if not proxies:
                    if not self.client:
                        self.client = httpx.AsyncClient(event_hooks={'response': [self.log_response]})
                    resp = await self.client.request(
                        method=method, url=url, content=content, data=data, files=files, json=json, params=params,
                        headers=headers, cookies=cookies, auth=auth, allow_redirects=allow_redirects, timeout=timeout
                    )
                    response = Response(resp)
                    return response
                else:
                    async with httpx.AsyncClient(proxies=proxies, event_hooks={'response': [self.log_response]}) as client:
                        resp = await client.request(
                            method=method, url=url, content=content, data=data, files=files, json=json, params=params,
                            headers=headers, cookies=cookies, auth=auth, allow_redirects=allow_redirects,
                            timeout=timeout
                        )
                        response = Response(resp)
                        return response
            except ConnectError as e:
                await logger.error(f'Failed to request {url}  ConnectError:{e}')
            except ConnectTimeout as e:
                await logger.error(f'Failed to request {url}  ConnectTimeout:{e}')
            except Exception as e:
                await logger.error(f'Failed to request {url}  {e}')




