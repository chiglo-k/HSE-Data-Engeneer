import pymongo
import random
import datetime
import uuid
from faker import Faker


class MongoDataGenerator:
    def __init__(self, host='127.0.0.1', port=27017, db_name='etl_project',
                 user='root', password='example'):

        # Создаем строку подключения с учетом аутентификации
        if user and password:
            connection_string = f"mongodb://{user}:{password}@{host}:{port}/"
        else:
            connection_string = f"mongodb://{host}:{port}/"

        try:
            self.client = pymongo.MongoClient(connection_string)
            # Проверяем соединение
            self.client.admin.command('ping')
            print(f"Успешное подключение к MongoDB на {host}:{port}")
        except Exception as e:
            print(f"Ошибка подключения к MongoDB: {e}")
            raise

        self.db = self.client[db_name]
        self.fake = Faker('ru_RU')  # Используем русскую локализацию для данных

    def generate_data(self, collection_name, num_records=100):
        """
        Генерирует данные для указанной коллекции.
        """
        collection = self.db[collection_name]

        # Очищаем коллекцию перед генерацией новых данных
        collection.delete_many({})

        if collection_name == 'UserSessions':
            records = self._generate_user_sessions(num_records)
        elif collection_name == 'SupportTickets':
            records = self._generate_support_tickets(num_records)
        elif collection_name == 'ProductPriceHistory':
            records = self._generate_product_price_history(num_records)
        else:
            print(f"Неизвестная коллекция: {collection_name}")
            return 0

        if records:
            collection.insert_many(records)
            return len(records)
        return 0

    def _generate_user_sessions(self, num_records):
        """Генерирует данные для коллекции UserSessions"""
        sessions = []
        for _ in range(num_records):
            start_time = self.fake.date_time_between(start_date='-30d', end_date='now')
            end_time = start_time + datetime.timedelta(minutes=random.randint(5, 120))

            sessions.append({
                'session_id': str(uuid.uuid4()),
                'user_id': random.randint(1, 1000),
                'start_time': start_time,
                'end_time': end_time,
                'pages_visited': [self.fake.uri_path() for _ in range(random.randint(1, 10))],
                'device': {
                    'type': random.choice(['mobile', 'desktop', 'tablet']),
                    'os': random.choice(['iOS', 'Android', 'Windows', 'MacOS', 'Linux']),
                    'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
                },
                'actions': [
                    {'type': random.choice(['click', 'scroll', 'view', 'purchase']),
                     'timestamp': start_time + datetime.timedelta(minutes=random.randint(1, 60))}
                    for _ in range(random.randint(1, 15))
                ]
            })
        return sessions

    def _generate_support_tickets(self, num_records):
        """Генерирует данные для коллекции SupportTickets"""
        tickets = []
        for _ in range(num_records):
            created_at = self.fake.date_time_between(start_date='-60d', end_date='-10d')
            updated_at = created_at + datetime.timedelta(days=random.randint(1, 10))

            messages = []
            for i in range(random.randint(1, 5)):
                msg_time = created_at + datetime.timedelta(hours=i * random.randint(1, 24))
                messages.append({
                    'sender': random.choice(['user', 'support']),
                    'text': self.fake.paragraph(),
                    'timestamp': msg_time
                })

            tickets.append({
                'ticket_id': str(uuid.uuid4()),
                'user_id': random.randint(1, 1000),
                'status': random.choice(['open', 'in_progress', 'resolved', 'closed']),
                'issue_type': random.choice(['billing', 'technical', 'account', 'product']),
                'messages': messages,
                'created_at': created_at,
                'updated_at': updated_at
            })
        return tickets

    def _generate_product_price_history(self, num_records):
        """Генерирует данные для коллекции ProductPriceHistory"""
        products = []
        for i in range(num_records):
            current_price = round(random.uniform(10, 1000), 2)
            price_changes = []

            for j in range(random.randint(1, 10)):
                change_date = self.fake.date_time_between(start_date='-1y', end_date='now')
                old_price = round(current_price * random.uniform(0.8, 1.2), 2)

                price_changes.append({
                    'date': change_date,
                    'old_price': old_price,
                    'new_price': current_price
                })

            products.append({
                'product_id': i + 1,
                'price_changes': price_changes,
                'current_price': current_price,
                'currency': random.choice(['RUB', 'USD', 'EUR'])
            })
        return products

    def get_collection_data(self, collection_name, limit=100):
        """
        Получает данные из указанной коллекции.
        """
        collection = self.db[collection_name]
        return list(collection.find().limit(limit))
