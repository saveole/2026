"""Garmin Connect API client using garth library."""

import logging
import os
from datetime import date, datetime
from typing import Optional, Dict, Any

import garth

logger = logging.getLogger(__name__)

# Garmin domain configuration
GARMIN_CN_DOMAIN = "garmin.cn"
GARMIN_COM_DOMAIN = "garmin.com"


class GarminClient:
    """Client for interacting with Garmin Connect API via garth."""

    def __init__(
        self,
        domain: str = GARMIN_CN_DOMAIN,
        ssl_verify: bool = False,
    ):
        """
        Initialize Garmin Connect client.

        Args:
            domain: Garmin domain to use ('garmin.com' or 'garmin.cn', defaults to 'garmin.cn')
            ssl_verify: Whether to verify SSL certificates (set False for garmin.cn)
        """
        self.domain = domain
        self.ssl_verify = ssl_verify
        self.authenticated = False

        # Configure garth for the specified domain
        self._configure_domain()

    def _configure_domain(self) -> None:
        """Configure garth for the specific Garmin domain."""
        if self.domain == GARMIN_CN_DOMAIN:
            logger.info(f"Configuring garth for Garmin China domain: {self.domain}")
            garth.configure(domain=self.domain, ssl_verify=self.ssl_verify)
        else:
            logger.info(f"Configuring garth for Garmin international domain: {self.domain}")
            # Use default settings for international domain

    def authenticate(self) -> None:
        """
        Authenticate with Garmin Connect API.

        Raises:
            Exception: If authentication fails
        """
        try:
            # Check if there's a saved auth token (for CN domain)
            secret_string = os.environ.get("GARTH_TOKEN_STRING")

            if secret_string:
                logger.info("Attempting to load existing authentication token")
                try:
                    garth.client.loads(secret_string)
                    self.authenticated = True
                    logger.info("Successfully authenticated with Garmin Connect using saved token")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load saved token, will login with credentials: {e}")

            # For CN domain, export the token for reuse
            if self.domain == GARMIN_CN_DOMAIN:
                token_string = garth.client.dumps()
                logger.info("GARTH_TOKEN_STRING exported for reuse (CN domain)")

        except Exception as e:
            logger.error(f"Garmin authentication failed: {e}")
            raise

    def get_sleep_data(self, target_date: date) -> Optional[Dict[str, Any]]:
        """
        Fetch sleep data for a specific date.

        Args:
            target_date: The date to fetch sleep data for

        Returns:
            Dictionary with 'sleep_time' and 'wake_time' as datetime objects,
            or None if no data is available

        Raises:
            Exception: If not authenticated or API request fails
        """
        if not self.authenticated:
            raise Exception("Not authenticated. Call authenticate() first.")

        try:
            # Get sleep data using garth.SleepData.list()
            # This returns a list of SleepData objects for the specified date range
            sleep_data_list = garth.SleepData.list(target_date, 1)

            if not sleep_data_list:
                logger.warning(f"No sleep data available for {target_date}")
                return None

            # Get the daily sleep DTO from the first result
            daily_sleep_dto = sleep_data_list[0].daily_sleep_dto

            if not daily_sleep_dto:
                logger.warning(f"Empty daily sleep DTO for {target_date}")
                return None

            # Extract timestamps in milliseconds
            sleep_start_ms = daily_sleep_dto.sleep_start_timestamp_local
            sleep_end_ms = daily_sleep_dto.sleep_end_timestamp_local

            if not sleep_start_ms or not sleep_end_ms:
                logger.warning(f"Missing sleep timestamps for {target_date}")
                return None

            # Convert milliseconds to datetime (local time)
            sleep_time = datetime.fromtimestamp(sleep_start_ms / 1000)
            wake_time = datetime.fromtimestamp(sleep_end_ms / 1000)

            logger.info(
                f"Retrieved sleep data for {target_date}: "
                f"sleep={sleep_time.isoformat()}, wake={wake_time.isoformat()}"
            )

            return {
                "sleep_time": sleep_time,
                "wake_time": wake_time,
                "date": target_date,
            }

        except Exception as e:
            logger.error(f"Failed to fetch sleep data for {target_date}: {e}")
            return None
