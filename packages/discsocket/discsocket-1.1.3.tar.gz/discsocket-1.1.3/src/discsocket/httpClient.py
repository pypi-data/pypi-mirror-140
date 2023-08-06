import aiohttp

class HttpRequestError(Exception):
    def __init__(self, request_path, error_message):
        super().__init__(f"HTTP request to {request_path} failed. Displaying attached error message: \n{error_message}")


class HTTPClient:
    def __init__(self, client_session: aiohttp.BaseConnector, client_headers, api_gateway_version=8):
        self.base = f'https://discord.com/api/v{api_gateway_version}/'
        self.session = client_session
        self.headers = client_headers

    async def make_request(self, request_type, request_path, json=None):
        full_request_path = self.base + request_path
        # Why
        match request_type:
            case 'GET':
                maybe_response = await self.session.get(full_request_path, headers=self.headers)
            case 'POST':
                maybe_response = await self.session.post(full_request_path, headers=self.headers, json=json)
            case 'PATCH':
                maybe_response = await self.session.patch(full_request_path, headers=self.headers, json=json)
            case 'DELETE':
                maybe_response = await self.session.delete(full_request_path, headers=self.headers)
            case 'PUT':
                maybe_response = await self.session.put(full_request_path, headers=self.headers)

        if not str(maybe_response.status).startswith('20'):
            raise HttpRequestError(full_request_path, (await maybe_response.json())['message'])

        try:
            return await maybe_response.json()
        except Exception:
            pass

    def build_url(self, path):
        return self.base + path 