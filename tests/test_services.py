import unittest
from unittest.mock import patch, AsyncMock, Mock
import asyncio
from services.crypto_service import get_crypto_price_history


class TestCryptoService(unittest.TestCase):

    @patch('services.crypto_service.aiohttp.ClientSession')
    def test_get_crypto_price_history_invalid_crypto_id(self, mock_client_session):
        """ Мок для возврата 404 статуса """
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.read = AsyncMock(return_value=b'Not Found')

        mock_get_context = AsyncMock()
        mock_get_context.__aenter__.return_value = mock_response
        mock_get_context.__aexit__.return_value = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_get_context

        mock_client_session.return_value.__aenter__.return_value = mock_session

        with self.assertRaises(ValueError) as context:
            asyncio.run(get_crypto_price_history('invalid_crypto', '1 месяц'))
        self.assertEqual(str(context.exception), "Произошла ошибка при получении исторических данных криптовалюты.")

    @patch('services.crypto_service.aiohttp.ClientSession')
    def test_get_crypto_price_history_api_error(self, mock_client_session):
        """ Мок для возврата 500 статуса """
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.read = AsyncMock(return_value=b'Internal Server Error')

        mock_get_context = AsyncMock()
        mock_get_context.__aenter__.return_value = mock_response
        mock_get_context.__aexit__.return_value = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_get_context

        mock_client_session.return_value.__aenter__.return_value = mock_session

        with self.assertRaises(ValueError) as context:
            asyncio.run(get_crypto_price_history('bitcoin', '1 день'))
        self.assertEqual(str(context.exception), "Произошла ошибка при получении исторических данных криптовалюты.")

    @patch('services.crypto_service.aiohttp.ClientSession')
    async def test_get_crypto_price_history_no_prices(self, mock_client_session):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})

        mock_get_context = AsyncMock()
        mock_get_context.__aenter__.return_value = mock_response
        mock_get_context.__aexit__.return_value = AsyncMock()

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_get_context

        mock_client_session.return_value.__aenter__.return_value = mock_session

        with self.assertRaises(ValueError) as context:
            await get_crypto_price_history('bitcoin', '1 месяц')

        self.assertEqual(str(context.exception), "Не удалось получить исторические данные криптовалюты.")

    @patch('services.crypto_service.aiohttp.ClientSession')
    async def test_get_crypto_price_history_malformed_prices(self, mock_client_session):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'prices': "Некорректные данные"
        })

        mock_get_context = AsyncMock()
        mock_get_context.__aenter__.return_value = mock_response
        mock_get_context.__aexit__.return_value = AsyncMock()
        mock_session = AsyncMock()
        mock_session.get.return_value = mock_get_context

        mock_client_session.return_value.__aenter__.return_value = mock_session

        with self.assertRaises(ValueError) as context:
            await get_crypto_price_history('bitcoin', '1 месяц')

        self.assertEqual(str(context.exception), "Не удалось получить исторические данные криптовалюты.")


if __name__ == '__main__':
    unittest.main()
