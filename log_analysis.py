import pandas as pd


# Загрузка JSON-файла
file_name = 'botsv1.json' # Файл с логом в формате JSON
raw_df = pd.read_json(file_name)

# Разворачиваем вложенное поле result
log_for_analyse = pd.json_normalize(raw_df['result'])

# Приведение типов
log_for_analyse['EventCode'] = pd.to_numeric(log_for_analyse.get('EventCode'), errors='coerce')
log_for_analyse['_time'] = pd.to_datetime(
    log_for_analyse['_time'],
    format='%Y-%m-%d %H:%M:%S.%f %Z',
    errors='coerce'
)

# Очистка данных
log_for_analyse = log_for_analyse.dropna(how='all')
log_for_analyse.columns = log_for_analyse.columns.str.strip()

print("Размер итогового датасета:", log_for_analyse.shape)
