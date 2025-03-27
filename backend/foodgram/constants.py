from django.core.validators import RegexValidator

# Пагинация
BASIC_PAGE_SIZE = 6

# Ограничения длины
EMAIL_MAX_LENGTH = 254
USERNAME_MAX_LENGTH = 150
NAME_MAX_LENGTH = 150
TAG_NAME_MAX_LENGTH = 32
COLOR_NAME_MAX_LENGTH = 7
PASSWORD_MIN_LENGTH = 8  # Рекомендуемый минимум

# Регулярное выражение для имени пользователя
USERNAME_REGEX = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_'
)