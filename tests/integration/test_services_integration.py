import unittest
from services.crypto_service import get_crypto_price, get_crypto_price_history
from services.currency_service import get_exchange_rate, get_exchange_rate_history
import asyncio


class TestIntegrationServices(unittest.TestCase):
    def test_get_exchange_rate_live(self):
        """Проверяем интеграцию и адекватное значение для валютной пары"""
        result = asyncio.run(get_exchange_rate('USD', 'RUB'))
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertLess(result, 200)

    def test_get_crypto_price_live(self):
        """Проверяем интеграцию и адекватное значение для криптовалютной пары"""
        result = asyncio.run(get_crypto_price('bitcoin'))
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertLess(result, 1000000)

    def test_get_exchange_rate_history_live(self):
        """Проверяем интеграцию для получения исторических значений валютной пары"""
        result = asyncio.run(get_exchange_rate_history('USD', 'RUB', '5 дней'))
        self.assertIsInstance(result, str)

    def test_get_crypto_price_history_live(self):
        """Проверяем интеграцию для получения исторических значений криптовалютной пары"""
        result = asyncio.run(get_crypto_price_history('bitcoin', '5 дней'))
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
