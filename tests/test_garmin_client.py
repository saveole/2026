"""Unit tests for Garmin Connect API client."""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch

from src.garmin_client import (
    GarminClient,
    GARMIN_CN_DOMAIN,
)


class TestGarminClientInit:
    """Tests for Garmin client initialization."""

    @patch('src.garmin_client.garth')
    def test_init_default_domain(self, mock_garth):
        """Test initialization with default domain."""
        client = GarminClient()

        assert client.domain == GARMIN_CN_DOMAIN
        assert client.ssl_verify is False
        assert client.authenticated is False

    @patch('src.garmin_client.garth')
    def test_init_custom_domain(self, mock_garth):
        """Test initialization with custom domain."""
        client = GarminClient(
            domain="garmin.com",
            ssl_verify=True
        )

        assert client.domain == "garmin.com"
        assert client.ssl_verify is True

    @patch('src.garmin_client.garth')
    def test_configure_domain_cn(self, mock_garth):
        """Test domain configuration for CN."""
        client = GarminClient(
            domain=GARMIN_CN_DOMAIN,
            ssl_verify=False
        )

        # Verify garth.configure was called
        mock_garth.configure.assert_called_once_with(
            domain=GARMIN_CN_DOMAIN,
            ssl_verify=False
        )


class TestGarminClientAuthentication:
    """Tests for Garmin client authentication."""

    @patch('src.garmin_client.garth')
    @patch.dict('os.environ', {}, clear=True)
    def test_authenticate_without_token(self, mock_garth):
        """Test authentication attempt without token."""
        client = GarminClient()

        # Mock garth.client.dumps() to return a token string
        mock_garth.client.dumps.return_value = "exported_token_string"

        client.authenticate()

        # Without token, authentication doesn't mark as authenticated
        # (it just exports the token for CN domain)
        assert client.authenticated is False

    @patch('src.garmin_client.garth')
    @patch.dict('os.environ', {'GARTH_TOKEN_STRING': 'mock_token'}, clear=True)
    def test_authenticate_with_token(self, mock_garth):
        """Test authentication with saved token."""
        client = GarminClient()

        client.authenticate()

        assert client.authenticated is True
        # Should not call login if token is present
        mock_garth.login.assert_not_called()
        mock_garth.client.loads.assert_called_once_with('mock_token')


class TestGetSleepData:
    """Tests for fetching sleep data."""

    @patch('src.garmin_client.garth')
    def test_get_sleep_data_success(self, mock_garth):
        """Test successful sleep data retrieval."""
        client = GarminClient(domain="garmin.cn", ssl_verify=False)
        client.authenticated = True

        target_date = date(2026, 1, 6)

        # Create expected sleep and wake times
        sleep_time = datetime(2026, 1, 5, 23, 30)
        wake_time = datetime(2026, 1, 6, 7, 0)

        # Convert to milliseconds timestamp
        sleep_start_ms = int(sleep_time.timestamp() * 1000)
        sleep_end_ms = int(wake_time.timestamp() * 1000)

        # Mock SleepData objects
        mock_sleep_data = Mock()
        mock_daily_dto = Mock()
        mock_daily_dto.sleep_start_timestamp_local = sleep_start_ms
        mock_daily_dto.sleep_end_timestamp_local = sleep_end_ms
        mock_sleep_data.daily_sleep_dto = mock_daily_dto

        # Mock SleepData.list() to return list of SleepData objects
        mock_garth.SleepData.list.return_value = [mock_sleep_data]

        result = client.get_sleep_data(target_date)

        assert result is not None
        assert "sleep_time" in result
        assert "wake_time" in result
        assert result["date"] == target_date
        assert isinstance(result["sleep_time"], datetime)
        assert isinstance(result["wake_time"], datetime)
        assert result["sleep_time"].hour == 23
        assert result["sleep_time"].minute == 30
        assert result["wake_time"].hour == 7
        assert result["wake_time"].minute == 0

    @patch('src.garmin_client.garth')
    def test_get_sleep_data_no_data_available(self, mock_garth):
        """Test handling when no sleep data is available."""
        client = GarminClient(domain="garmin.cn", ssl_verify=False)
        client.authenticated = True

        target_date = date(2026, 1, 6)
        mock_garth.SleepData.list.return_value = []  # Empty response

        result = client.get_sleep_data(target_date)

        assert result is None

    @patch('src.garmin_client.garth')
    def test_get_sleep_data_not_authenticated(self, mock_garth):
        """Test that error is raised when not authenticated."""
        client = GarminClient(domain="garmin.cn", ssl_verify=False)
        client.authenticated = False

        with pytest.raises(Exception, match="Not authenticated"):
            client.get_sleep_data(date(2026, 1, 6))

    @patch('src.garmin_client.garth')
    def test_get_sleep_data_empty_dto(self, mock_garth):
        """Test handling empty daily sleep DTO."""
        client = GarminClient(domain="garmin.cn", ssl_verify=False)
        client.authenticated = True

        target_date = date(2026, 1, 6)

        # Mock SleepData with empty DTO
        mock_sleep_data = Mock()
        mock_sleep_data.daily_sleep_dto = None
        mock_garth.SleepData.list.return_value = [mock_sleep_data]

        result = client.get_sleep_data(target_date)

        assert result is None

    @patch('src.garmin_client.garth')
    def test_get_sleep_data_missing_timestamps(self, mock_garth):
        """Test handling missing timestamps."""
        client = GarminClient(domain="garmin.cn", ssl_verify=False)
        client.authenticated = True

        target_date = date(2026, 1, 6)

        # Mock SleepData with missing timestamps
        mock_sleep_data = Mock()
        mock_daily_dto = Mock()
        mock_daily_dto.sleep_start_timestamp_local = None
        mock_daily_dto.sleep_end_timestamp_local = None
        mock_sleep_data.daily_sleep_dto = mock_daily_dto
        mock_garth.SleepData.list.return_value = [mock_sleep_data]

        result = client.get_sleep_data(target_date)

        assert result is None

