import os

class Config:
    SECRET_KEY = 'supersecretkey'
    UPLOAD_FOLDER = 'static/uploads'
    DISCOUNTS = [5, 10, 15, 20, 25, 30]
    BOT_RESPONSES = [
        "Привет! Какой товар вас интересует?",
        "Этот товар - отличный выбор!",
        "Вы хотите добавить его в корзину?",
        "У нас сегодня действует скидка!",
        "Не забудьте посмотреть другие товары."
    ]
