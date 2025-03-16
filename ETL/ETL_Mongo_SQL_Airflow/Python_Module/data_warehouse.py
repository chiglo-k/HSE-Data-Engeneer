import psycopg2
import json
from datetime import datetime


class DataWarehouseManager:
    def __init__(self, pg_connector):
        self.pg_connector = pg_connector
        self.cursor = pg_connector.cursor
        self.conn = pg_connector.conn

    def _execute_sql(self, query, params=None):
        """Базовый метод для выполнения SQL-запросов с обработкой ошибок"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при выполнении SQL-запроса: {e}")
            raise

    def _create_index(self, table_name, column_name):
        """Создает индекс для оптимизации запросов"""
        index_query = f'''
        CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} 
        ON {table_name}({column_name});
        '''
        return self._execute_sql(index_query)

    def create_user_activity_mart(self):
        """Создает витрину активности пользователей"""
        create_query = '''
        CREATE TABLE IF NOT EXISTS user_activity_mart (
            user_id INTEGER PRIMARY KEY,
            total_sessions INTEGER,
            avg_session_duration FLOAT,
            total_pages_visited INTEGER,
            last_activity TIMESTAMP,
            device_distribution JSONB,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''

        self._execute_sql(create_query)
        self._execute_sql("TRUNCATE user_activity_mart;")

        insert_query = '''
        INSERT INTO user_activity_mart (
            user_id, 
            total_sessions, 
            avg_session_duration, 
            total_pages_visited,
            last_activity,
            device_distribution
        )
        SELECT 
            user_id,
            COUNT(DISTINCT session_id) as total_sessions,
            AVG(EXTRACT(EPOCH FROM (end_time - start_time))/60) as avg_session_duration,
            SUM(jsonb_array_length(pages_visited)) as total_pages_visited,
            MAX(end_time) as last_activity,
            jsonb_build_object(
                'mobile', SUM(CASE WHEN device->>'type' = 'mobile' THEN 1 ELSE 0 END),
                'desktop', SUM(CASE WHEN device->>'type' = 'desktop' THEN 1 ELSE 0 END),
                'tablet', SUM(CASE WHEN device->>'type' = 'tablet' THEN 1 ELSE 0 END)
            ) as device_distribution
        FROM 
            user_sessions
        GROUP BY 
            user_id
        ON CONFLICT (user_id) 
        DO UPDATE SET
            total_sessions = EXCLUDED.total_sessions,
            avg_session_duration = EXCLUDED.avg_session_duration,
            total_pages_visited = EXCLUDED.total_pages_visited,
            last_activity = EXCLUDED.last_activity,
            device_distribution = EXCLUDED.device_distribution,
            last_updated = CURRENT_TIMESTAMP
        '''

        self._execute_sql(insert_query)
        self._create_index('user_activity_mart', 'last_activity')

    def create_support_efficiency_mart(self):
        """Создает витрину эффективности поддержки"""
        create_query = '''
        CREATE TABLE IF NOT EXISTS support_efficiency_mart (
            issue_type VARCHAR(50) PRIMARY KEY,
            total_tickets INTEGER,
            avg_resolution_time FLOAT,
            open_tickets INTEGER,
            closed_tickets INTEGER,
            response_time_distribution JSONB,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''

        self._execute_sql(create_query)
        self._execute_sql("TRUNCATE support_efficiency_mart;")

        insert_query = '''
        INSERT INTO support_efficiency_mart (
            issue_type,
            total_tickets,
            avg_resolution_time,
            open_tickets,
            closed_tickets,
            response_time_distribution
        )
        SELECT 
            issue_type,
            COUNT(*) as total_tickets,
            AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/3600) as avg_resolution_time,
            SUM(CASE WHEN status IN ('open', 'in_progress') THEN 1 ELSE 0 END) as open_tickets,
            SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END) as closed_tickets,
            jsonb_build_object(
                'under_24h', SUM(CASE WHEN EXTRACT(EPOCH FROM (updated_at - created_at))/3600 < 24 THEN 1 ELSE 0 END),
                '24h_to_48h', SUM(CASE WHEN EXTRACT(EPOCH FROM (updated_at - created_at))/3600 BETWEEN 24 AND 48 THEN 1 ELSE 0 END),
                'over_48h', SUM(CASE WHEN EXTRACT(EPOCH FROM (updated_at - created_at))/3600 > 48 THEN 1 ELSE 0 END)
            ) as response_time_distribution
        FROM 
            support_tickets
        GROUP BY 
            issue_type
        ON CONFLICT (issue_type) 
        DO UPDATE SET
            total_tickets = EXCLUDED.total_tickets,
            avg_resolution_time = EXCLUDED.avg_resolution_time,
            open_tickets = EXCLUDED.open_tickets,
            closed_tickets = EXCLUDED.closed_tickets,
            response_time_distribution = EXCLUDED.response_time_distribution,
            last_updated = CURRENT_TIMESTAMP
        '''

        self._execute_sql(insert_query)
        self._create_index('support_efficiency_mart', 'total_tickets')

    def create_product_price_analytics_mart(self):
        """Создает витрину аналитики цен на продукты"""
        create_query = '''
        CREATE TABLE IF NOT EXISTS product_price_analytics_mart (
            currency VARCHAR(10),
            avg_price DECIMAL(10, 2),
            min_price DECIMAL(10, 2),
            max_price DECIMAL(10, 2),
            price_change_frequency JSONB,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''

        self._execute_sql(create_query)
        self._execute_sql("TRUNCATE product_price_analytics_mart;")

        insert_query = '''
        INSERT INTO product_price_analytics_mart (
            currency,
            avg_price,
            min_price,
            max_price,
            price_change_frequency
        )
        SELECT 
            currency,
            AVG(current_price) as avg_price,
            MIN(current_price) as min_price,
            MAX(current_price) as max_price,
            jsonb_build_object(
                'low', SUM(CASE WHEN jsonb_array_length(price_changes) < 3 THEN 1 ELSE 0 END),
                'medium', SUM(CASE WHEN jsonb_array_length(price_changes) BETWEEN 3 AND 6 THEN 1 ELSE 0 END),
                'high', SUM(CASE WHEN jsonb_array_length(price_changes) > 6 THEN 1 ELSE 0 END)
            ) as price_change_frequency
        FROM 
            product_price_history
        GROUP BY 
            currency
        '''

        self._execute_sql(insert_query)

    def _query_mart(self, query, params=None):
        """Базовый метод для выполнения запросов к витринам"""
        try:
            if params:
                result = self.pg_connector.execute_query(query, params)
            else:
                result = self.pg_connector.execute_query(query)
            return result
        except Exception as e:
            print(f"Ошибка при запросе к витрине: {e}")
            raise

    def query_user_activity(self, limit=10):
        """Запрашивает данные из витрины активности пользователей"""
        query = f'''
        SELECT * FROM user_activity_mart
        ORDER BY total_sessions DESC
        LIMIT {limit}
        '''
        return self._query_mart(query)

    def query_support_efficiency(self):
        """Запрашивает данные из витрины эффективности поддержки"""
        query = '''
        SELECT * FROM support_efficiency_mart
        ORDER BY total_tickets DESC
        '''
        return self._query_mart(query)

    def query_product_price_analytics(self):
        """Запрашивает данные из витрины аналитики цен на продукты"""
        query = '''
        SELECT * FROM product_price_analytics_mart
        ORDER BY avg_price DESC
        '''
        return self._query_mart(query)

    def get_user_activity_report(self):
        """Создает отчет об активности пользователей"""
        try:
            # Получаем общую статистику
            total_stats = self._query_mart('''
            SELECT 
                COUNT(*) as total_users,
                AVG(total_sessions) as avg_sessions_per_user,
                AVG(avg_session_duration) as avg_session_duration,
                AVG(total_pages_visited) as avg_pages_per_user
            FROM user_activity_mart
            ''')[0]

            # Получаем распределение устройств
            device_stats = self._query_mart('''
            SELECT 
                SUM((device_distribution->>'mobile')::int) as mobile_sessions,
                SUM((device_distribution->>'desktop')::int) as desktop_sessions,
                SUM((device_distribution->>'tablet')::int) as tablet_sessions
            FROM user_activity_mart
            ''')[0]

            # Получаем топ-5 самых активных пользователей
            top_users = self._query_mart('''
            SELECT 
                u.user_id,
                u.username,
                u.email,
                a.total_sessions,
                a.avg_session_duration,
                a.total_pages_visited
            FROM user_activity_mart a
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.total_sessions DESC, a.total_pages_visited DESC
            LIMIT 5
            ''')

            return {
                'total_stats': total_stats,
                'device_stats': device_stats,
                'top_users': top_users
            }
        except Exception as e:
            print(f"Ошибка при создании отчета об активности пользователей: {e}")
            raise

    def get_support_efficiency_report(self):
        """Создает отчет об эффективности поддержки"""
        try:
            # Получаем общую статистику
            total_stats = self._query_mart('''
            SELECT 
                SUM(total_tickets) as total_tickets,
                AVG(avg_resolution_time) as avg_resolution_time,
                SUM(open_tickets) as open_tickets,
                SUM(closed_tickets) as closed_tickets
            FROM support_efficiency_mart
            ''')[0]

            # Получаем статистику по типам проблем
            issue_stats = self._query_mart('''
            SELECT 
                issue_type,
                total_tickets,
                avg_resolution_time,
                open_tickets,
                closed_tickets,
                (response_time_distribution->>'under_24h')::int as resolved_under_24h,
                (response_time_distribution->>'24h_to_48h')::int as resolved_24h_to_48h,
                (response_time_distribution->>'over_48h')::int as resolved_over_48h
            FROM support_efficiency_mart
            ORDER BY total_tickets DESC
            ''')

            return {
                'total_stats': total_stats,
                'issue_stats': issue_stats
            }
        except Exception as e:
            print(f"Ошибка при создании отчета об эффективности поддержки: {e}")
            raise
