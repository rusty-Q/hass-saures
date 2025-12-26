#!/usr/bin/env python3
import sys
import json
from datetime import datetime
from uk_saures_integration import DataIntegrator

def main():
    """Точка входа для CLI"""
    try:
        print("🚀 Запуск интеграции UK_GOROD и Saures API")
        print("=" * 60)
        
        # Создаем интегратор
        integrator = DataIntegrator()
        
        # Собираем и интегрируем данные
        readings = integrator.collect_and_integrate_data()
        
        # Сохраняем результаты
        output_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'source': 'uk_saures_integration',
                'total_records': len(readings)
            },
            'meter_readings': [
                {
                    'id': r.id,
                    'meter_reading_id': r.meter_reading_id,
                    'service': r.service,
                    'serial_number': r.serial_number,
                    'serial_normalized': r.serial_normalized,
                    'next_verification_date': r.next_verification_date,
                    'last_reading': {
                        'date': r.last_reading.date,
                        'value': r.last_reading.value
                    },
                    'current_reading': {
                        'value': r.current_reading.value,
                        'source': r.current_reading.source,
                        'date': r.current_reading.date,
                        'saures_type': r.current_reading.saures_type,
                        'saures_unit': r.current_reading.saures_unit,
                        'update_time': r.current_reading.update_time
                    },
                    'metadata': r.metadata
                }
                for r in readings
            ]
        }
        
        # Сохраняем в файл
        with open('meter_readings.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Интеграция завершена успешно!")
        print(f"📁 Результаты сохранены в: meter_readings.json")
        print(f"📊 Обработано счетчиков: {len(readings)}")
        
        # Статистика
        with_saures = sum(1 for r in readings if r.current_reading.source == 'saures_api')
        print(f"   • С данными из Saures: {with_saures}")
        print(f"   • Только UK_GOROD: {len(readings) - with_saures}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
