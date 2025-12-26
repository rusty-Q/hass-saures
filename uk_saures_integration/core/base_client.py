import requests
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAPIClient(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @abstractmethod
    def authenticate(self, login: str, password: str) -> bool:
        pass
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Базовый метод для выполнения HTTP запросов"""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.RequestException as e:
            raise Exception(f"Ошибка запроса: {e}")
