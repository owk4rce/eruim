# Связываем со всеми интерфейсами на порту 10000
bind = "0.0.0.0:10000"

# Количество рабочих процессов
workers = 4

# Используем gevent для лучшей обработки загрузки файлов
worker_class = "gevent"

# Увеличиваем таймаут
timeout = 300

# Убираем ограничения на размер запроса
max_request_line = 0
limit_request_fields = 32768
limit_request_field_size = 0

# Настройки для multipart/form-data
worker_connections = 1000
keepalive = 2