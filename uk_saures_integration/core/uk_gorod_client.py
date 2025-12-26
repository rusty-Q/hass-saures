from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any
from .base_client import BaseAPIClient
from ..models.meter_reading import MeterReading
from ..utils.serial_normalizer import normalize_serial_number

class UkGorodClient(BaseAPIClient):
    def __init__(self):
        super().__init__('https://nd.inno-e.ru')
    
    def authenticate(self, email: str, password: str) -> bool:
        """Аутентификация в UK_GOROD"""
        try:
            # 1. Получение начального редиректа
            start_url = f"{self.base_url}/gorod"
            initial_response = self.session.get(start_url, allow_redirects=False)
            
            if initial_response.status_code not in [301, 302, 303, 307, 308]:
                return False
            
            # 2. Обработка редиректа
            redirect_path = initial_response.headers.get('Location', '')
            redirect_url = urljoin(self.base_url, redirect_path)
            final_response = self.session.get(redirect_url, allow_redirects=True)
            
            # 3. Извлечение токена CSRF
            soup = BeautifulSoup(final_response.text, 'html.parser')
            token_input = soup.find('input', {'name': '__RequestVerificationToken'})
            
            if not token_input:
                token_input = soup.find('input', {'name': lambda x: x and 'RequestVerificationToken' in x})
            
            if not token_input or not token_input.get('value'):
                return False
            
            token = token_input['value']
            
            # 4. Отправка данных для входа
            login_data = {
                '__RequestVerificationToken': token,
                'Email': email,
                'Password': password
            }
            
            login_response = self.session.post(final_response.url, data=login_data)
            
            # 5. Проверка успешности входа
            if login_response.status_code in [301, 302]:
                return True
            elif login_response.status_code == 200:
                return ('inputEmail3' not in login_response.text and 
                       'login-box-body' not in login_response.text)
            return False
            
        except Exception as e:
            raise Exception(f"Ошибка аутентификации UK_GOROD: {e}")
    
    def get_meter_readings(self) -> List[MeterReading]:
        """Получение списка счетчиков с UK_GOROD"""
        try:
            counters_url = f"{self.base_url}/gorod/Abonent/Counters"
            response = self.session.get(counters_url)
            
            if response.status_code != 200:
                raise Exception(f"Не удалось получить страницу счетчиков: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            meter_reading_inputs = soup.find_all('input', {'name': 'MeterReadingId'})
            
            readings = []
            
            for idx, input_tag in enumerate(meter_reading_inputs, 1):
                meter_id = input_tag.get('value', '').strip()
                if not meter_id:
                    continue
                
                parent_row = input_tag.find_parent('tr')
                if not parent_row:
                    continue
                
                cells = parent_row.find_all('td')
                if len(cells) >= 9:
                    service = cells[0].get_text(strip=True)
                    serial_raw = cells[1].get_text(strip=True)
                    serial_normalized = normalize_serial_number(serial_raw)
                    
                    current_value_input = parent_row.find('input', {'name': 'InputValCnt'})
                    current_value = current_value_input.get('value', '') if current_value_input else ''
                    
                    reading = MeterReading.from_uk_gorod_html(
                        idx=idx,
                        meter_id=meter_id,
                        service=service,
                        serial_number=serial_raw,
                        next_verification=cells[2].get_text(strip=True),
                        last_reading_date=cells[3].get_text(strip=True),
                        last_reading_value=cells[4].get_text(strip=True),
                        current_reading_date=cells[5].get_text(strip=True),
                        current_value=current_value,
                        askue_link=f"{self.base_url}/gorod/Abonent/GetIndication/{meter_id}"
                    )
                    
                    # Обновляем нормализованный номер
                    reading.serial_normalized = serial_normalized
                    readings.append(reading)
            
            return readings
            
        except Exception as e:
            raise Exception(f"Ошибка получения данных счетчиков: {e}")
