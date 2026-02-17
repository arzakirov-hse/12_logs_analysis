import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ЭТАП 2. ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ
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

# ЭТАП 2. АНАЛИЗ ДАННЫХ
# 2.1 Анализ WinEventLog
suspicious_event_ids = [4625, 4672, 4688, 4720]
# 4625 — неудачный вход
# 4672 — эскалация
# 4688 — создание процесса
# 4720 — создание пользователя

win_suspicious = log_for_analyse[log_for_analyse['EventCode'].isin(suspicious_event_ids)]

# Подсчёт количества подозрительных событий
win_counts = win_suspicious['EventCode'].value_counts()

print("\nПодозрительные WinEvent события:")
print(win_counts)

# 2.2 Анализ DNS-логов

dns_df = log_for_analyse[log_for_analyse['sourcetype'].str.contains('dns', case=False, na=False)]

if not dns_df.empty:

    # Подсчёт частоты запросов
    dns_counts = dns_df['query'].value_counts()

    # Подозрительные длинные домены (часто DGA)
    dns_df['domain_length'] = dns_df['query'].astype(str).apply(len)
    suspicious_dns = dns_df[dns_df['domain_length'] > 50]

    print("\nТоп DNS-запросов:")
    print(dns_counts.head())

    print("\nПодозрительные длинные DNS-запросы:")
    print(suspicious_dns[['query', 'src']].head())

else:
    print("\nDNS-логи в данном файле не обнаружены.")
    dns_counts = pd.Series()

# ЭТАП 3. ВИЗУАЛИЗАЦИЯ

# 3.1 Визуализация топ-10 WinEvent событий

if not win_counts.empty:
    plt.figure()
    sns.barplot(x=win_counts.head(10).index,
                y=win_counts.head(10).values)

    plt.title("Топ-10 подозрительных WinEvent событий")
    plt.xlabel("EventCode")
    plt.ylabel("Количество")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# 3.2 Визуализация топ-10 DNS-запросов

if not dns_counts.empty:
    top_dns = dns_counts.head(10)

    plt.figure()
    sns.barplot(x=top_dns.index,
                y=top_dns.values)

    plt.title("Топ-10 DNS-запросов")
    plt.xlabel("Домен")
    plt.ylabel("Количество")
    plt.xticks(rotation=75)
    plt.tight_layout()
    plt.show()


print("\nАнализ завершён.")