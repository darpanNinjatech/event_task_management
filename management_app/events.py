from .httpx_client import HTTPXClientModel
from dotenv import load_dotenv
import os

load_dotenv()

EVENTS_API_URL = os.getenv('EVENTS_API_URL')
RESPONSE_API_URL = os.getenv('RESPONSE_API_URL')

class EventClientModel(HTTPXClientModel):
    def __init__(self, events_api_url: str = EVENTS_API_URL, timeout: int = 10):
        super().__init__(events_api_url, timeout)

    def get_events(self):
        return self.parse_xml(self.get('/'))

class ClientModel(HTTPXClientModel):
    def __init__(self, response_api_url: str = RESPONSE_API_URL, timeout: int = 10):
        super().__init__(response_api_url, timeout)

    def get_events(self):
        return self.get('/api/events/').json()

    def add_event(self, payload: dict):
        return self.post('/api/events/', json=payload)

    def get_processed_event_ids(self):
        return self.get('/api/events/ids').json()
