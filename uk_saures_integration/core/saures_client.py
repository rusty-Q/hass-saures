from typing import Dict, List, Any, Optional
from .base_client import BaseAPIClient
from ..utils.serial_normalizer import normalize_serial_number

class SauresClient(BaseAPIClient):
    def __init__(self):
        super().__init__('https://api.saures.ru/1.0')
    
    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Аутентификация в Saures API"""
        try:
            login_url = f"{self.base_url}/login"
            login_data = {'email': email, 'password': password}
            
            response = self.session.post(login_url, data=login_data)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') != 'ok':
                raise Exception(f"Ошибка авторизации Saures: {data.get('errors')}")
            
            return data['data']
            
        except Exception as e:
            raise Exception(f"Ошибка аутентификации Saures: {e}")
    
    def get_user_objects(self, sid: str) -> List[Dict[str, Any]]:
        """Получение списка объектов пользователя"""
        try:
            objects_url = f"{self.base_url}/user/objects"
            params = {'sid': sid}
            
            response = self.session.get(objects_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') != 'ok':
                raise Exception(f"Ошибка получения объектов: {data.get('errors')}")
            
            return data['data']['objects']
            
        except Exception as e:
            raise Exception(f"Ошибка получения объектов: {e}")
    
    def get_object_meters(self, sid: str, object_id: int) -> Dict[str, Dict[str, Any]]:
        """Получение счетчиков для объекта"""
        try:
            meters_url = f"{self.base_url}/object/meters"
            params = {'sid': sid, 'id': object_id}
            
            response = self.session.get(meters_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') != 'ok':
                raise Exception(f"Ошибка получения счетчиков: {data.get('errors')}")
            
            # Собираем счетчики в словарь по нормализованному серийному номеру
            saures_meters = {}
            sensors = data['data']['sensors']
            
            for sensor in sensors:
                for meter in sensor.get('meters', []):
                    sn_raw = meter.get('sn', '').strip()
                    if sn_raw:
                        sn_normalized = normalize_serial_number(sn_raw)
                        
                        saures_meters[sn_normalized] = {
                            'original_sn': sn_raw,
                            'normalized_sn': sn_normalized,
                            'meter_id': meter['meter_id'],
                            'serial_number': sn_raw,
                            'meter_name': meter.get('meter_name', ''),
                            'type': meter['type'],
                            'unit': meter['unit'],
                            'values': meter['vals'],
                            'state': meter['state'],
                            'input': meter['input'],
                            'sensor_name': sensor.get('name', '')
                        }
            
            return saures_meters
            
        except Exception as e:
            raise Exception(f"Ошибка получения счетчиков объекта: {e}")
