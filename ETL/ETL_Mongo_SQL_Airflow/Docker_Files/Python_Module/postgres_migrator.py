import psycopg2
import json
from datetime import datetime
from faker import Faker


class PostgresMigrator:
    def __init__(self, host='127.0.0.1', port=5432, dbname='migrate_data',
                 user='admin', password='admin'):
        """
        Инициализирует подключение к PostgreSQL.
        """
        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            self.cursor = self.conn.cursor()
            print(f"Успешное подключение к PostgreSQL на {host}:{port}")
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    def create_tables(self):
        """Создает таблицы в PostgreSQL для хранения данных из MongoDB"""
        try:
            # Создание таблицы users (для связи с user_sessions и support_tickets)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username VARCHAR(100),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            ''')

            # Создание таблицы user_sessions с внешним ключом на users
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id VARCHAR(50) PRIMARY KEY,
                user_id INTEGER,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                pages_visited JSONB,
                device JSONB,
                actions JSONB,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE
            );
            ''')

            # Создание таблицы support_tickets с внешним ключом на users
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id VARCHAR(50) PRIMARY KEY,
                user_id INTEGER,
                status VARCHAR(20),
                issue_type VARCHAR(20),
                messages JSONB,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE
            );
            ''')

            # Создание таблицы product_price_history
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_price_history (
                product_id INTEGER PRIMARY KEY,
                price_changes JSONB,
                current_price DECIMAL(10, 2),
                currency VARCHAR(10)
            );
            ''')

            # Создание индексов для оптимизации запросов
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON support_tickets(user_id);')
            self.cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_support_tickets_issue_type ON support_tickets(issue_type);')

            self.conn.commit()
            print("Таблицы успешно созданы в PostgreSQL")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при создании таблиц: {e}")
            raise

    def generate_users(self, num_users=1000):
        """
        Генерирует пользователей для связи с другими таблицами
        """
        try:
            fake = Faker('ru_RU')

            # Очищаем таблицу перед генерацией новых данных
            self.cursor.execute("TRUNCATE users CASCADE;")

            for i in range(1, num_users + 1):
                self.cursor.execute('''
                INSERT INTO users (user_id, username, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
                ''', (
                    i,
                    fake.user_name(),
                    fake.email()
                ))

            self.conn.commit()
            print(f"Сгенерировано {num_users} пользователей в PostgreSQL")
            return num_users
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при генерации пользователей: {e}")
            raise

    def migrate_data(self, mongo_connector, collection_name, batch_size=100):
        """
        Мигрирует данные из MongoDB в PostgreSQL.
        """
        try:
            # Получение данных из MongoDB
            collection = mongo_connector.db[collection_name]
            total_count = collection.count_documents({})
            processed = 0

            # Очищаем соответствующую таблицу перед миграцией
            if collection_name == 'UserSessions':
                self.cursor.execute("TRUNCATE user_sessions;")
            elif collection_name == 'SupportTickets':
                self.cursor.execute("TRUNCATE support_tickets;")
            elif collection_name == 'ProductPriceHistory':
                self.cursor.execute("TRUNCATE product_price_history;")

            # Обработка данных пакетами
            for skip in range(0, total_count, batch_size):
                documents = list(collection.find().skip(skip).limit(batch_size))

                if collection_name == 'UserSessions':
                    self._migrate_user_sessions(documents)
                elif collection_name == 'SupportTickets':
                    self._migrate_support_tickets(documents)
                elif collection_name == 'ProductPriceHistory':
                    self._migrate_product_price_history(documents)

                processed += len(documents)
                print(f"Мигрировано {processed}/{total_count} записей из {collection_name}")

            self.conn.commit()
            return processed
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при миграции данных: {e}")
            raise

    def _migrate_user_sessions(self, documents):
        """Мигрирует данные из коллекции UserSessions"""
        for doc in documents:
            # Трансформация данных
            # Преобразование MongoDB ObjectId в строку
            doc['_id'] = str(doc['_id'])

            # Преобразование datetime объектов в строки ISO формата
            if isinstance(doc['start_time'], datetime):
                start_time = doc['start_time'].isoformat()
            else:
                start_time = doc['start_time']

            if isinstance(doc['end_time'], datetime):
                end_time = doc['end_time'].isoformat()
            else:
                end_time = doc['end_time']

            # Преобразование вложенных datetime объектов в actions
            actions = []
            for action in doc['actions']:
                action_copy = action.copy()
                if isinstance(action_copy.get('timestamp'), datetime):
                    action_copy['timestamp'] = action_copy['timestamp'].isoformat()
                actions.append(action_copy)

            self.cursor.execute('''
            INSERT INTO user_sessions (session_id, user_id, start_time, end_time, pages_visited, device, actions)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                start_time = EXCLUDED.start_time,
                end_time = EXCLUDED.end_time,
                pages_visited = EXCLUDED.pages_visited,
                device = EXCLUDED.device,
                actions = EXCLUDED.actions
            ''', (
                doc['session_id'],
                doc['user_id'],
                start_time,
                end_time,
                json.dumps(doc['pages_visited']),
                json.dumps(doc['device']),
                json.dumps(actions)
            ))

    def _migrate_support_tickets(self, documents):
        """Мигрирует данные из коллекции SupportTickets"""
        for doc in documents:
            # Трансформация данных
            doc['_id'] = str(doc['_id'])

            if isinstance(doc['created_at'], datetime):
                created_at = doc['created_at'].isoformat()
            else:
                created_at = doc['created_at']

            if isinstance(doc['updated_at'], datetime):
                updated_at = doc['updated_at'].isoformat()
            else:
                updated_at = doc['updated_at']

            # Преобразование вложенных datetime объектов в messages
            messages = []
            for message in doc['messages']:
                message_copy = message.copy()
                if isinstance(message_copy.get('timestamp'), datetime):
                    message_copy['timestamp'] = message_copy['timestamp'].isoformat()
                messages.append(message_copy)

            self.cursor.execute('''
            INSERT INTO support_tickets (ticket_id, user_id, status, issue_type, messages, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticket_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                status = EXCLUDED.status,
                issue_type = EXCLUDED.issue_type,
                messages = EXCLUDED.messages,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at
            ''', (
                doc['ticket_id'],
                doc['user_id'],
                doc['status'],
                doc['issue_type'],
                json.dumps(messages),
                created_at,
                updated_at
            ))

    def _migrate_product_price_history(self, documents):
        """Мигрирует данные из коллекции ProductPriceHistory"""
        for doc in documents:
            # Трансформация данных
            doc['_id'] = str(doc['_id'])

            # Преобразование datetime объектов в price_changes
            price_changes = []
            for change in doc['price_changes']:
                change_copy = change.copy()
                if isinstance(change_copy.get('date'), datetime):
                    change_copy['date'] = change_copy['date'].isoformat()
                price_changes.append(change_copy)

            self.cursor.execute('''
            INSERT INTO product_price_history (product_id, price_changes, current_price, currency)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET
                price_changes = EXCLUDED.price_changes,
                current_price = EXCLUDED.current_price,
                currency = EXCLUDED.currency
            ''', (
                doc['product_id'],
                json.dumps(price_changes),
                doc['current_price'],
                doc['currency']
            ))

    def execute_query(self, query, params=None):
        """
        Выполняет SQL-запрос к базе данных.
        """
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith(('SELECT', 'WITH')):
                columns = [desc[0] for desc in self.cursor.description]
                return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            else:
                self.conn.commit()
                return None
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при выполнении запроса: {e}")
            raise

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
