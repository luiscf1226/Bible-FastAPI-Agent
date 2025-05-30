from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import HTTPException
import json
import os
from pathlib import Path
import threading
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_day: int = 5, storage_file: str = "rate_limits.json"):
        self.requests_per_day = requests_per_day
        # Structure: {endpoint: {ip: (count, timestamp)}}
        self.endpoint_requests: Dict[str, Dict[str, Tuple[int, datetime]]] = {}
        self.storage_file = storage_file
        self.lock = threading.Lock()
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=30)  # Cleanup every 30 minutes
        
        # Create storage directory if it doesn't exist
        storage_path = Path(storage_file)
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data if available
        self._load_data()

    def _load_data(self):
        """Load rate limit data from file if it exists."""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.endpoint_requests = {
                        endpoint: {
                            ip: (count, datetime.fromisoformat(timestamp))
                            for ip, (count, timestamp) in ip_data.items()
                        }
                        for endpoint, ip_data in data.items()
                    }
                logger.info(f"Loaded rate limit data for {len(self.endpoint_requests)} endpoints")
        except Exception as e:
            logger.error(f"Error loading rate limit data: {e}")
            self.endpoint_requests = {}

    def _save_data(self):
        """Save rate limit data to file."""
        try:
            with open(self.storage_file, 'w') as f:
                data = {
                    endpoint: {
                        ip: (count, timestamp.isoformat())
                        for ip, (count, timestamp) in ip_data.items()
                    }
                    for endpoint, ip_data in self.endpoint_requests.items()
                }
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving rate limit data: {e}")

    def is_rate_limited(self, endpoint: str, ip: str) -> bool:
        with self.lock:
            current_time = datetime.now()
            
            # Initialize endpoint if it doesn't exist
            if endpoint not in self.endpoint_requests:
                self.endpoint_requests[endpoint] = {}
            
            # Periodic cleanup
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_expired()
                self.last_cleanup = current_time
                self._save_data()
            
            if ip not in self.endpoint_requests[endpoint]:
                self.endpoint_requests[endpoint][ip] = (1, current_time)
                self._save_data()
                return False
                
            count, first_request_time = self.endpoint_requests[endpoint][ip]
            
            # Check if 24 hours have passed since first request
            if current_time - first_request_time > timedelta(hours=24):
                self.endpoint_requests[endpoint][ip] = (1, current_time)
                self._save_data()
                return False
                
            # Check if limit is reached
            if count >= self.requests_per_day:
                return True
                
            # Increment request count
            self.endpoint_requests[endpoint][ip] = (count + 1, first_request_time)
            self._save_data()
            return False

    def _cleanup_expired(self):
        """Remove expired entries and limit total storage."""
        current_time = datetime.now()
        
        # Remove expired entries for each endpoint
        for endpoint in self.endpoint_requests:
            expired_ips = [
                ip for ip, (_, timestamp) in self.endpoint_requests[endpoint].items()
                if current_time - timestamp > timedelta(hours=24)
            ]
            for ip in expired_ips:
                del self.endpoint_requests[endpoint][ip]
            
            # Limit total storage per endpoint
            if len(self.endpoint_requests[endpoint]) > 100000:  # Limit to 100k IPs per endpoint
                sorted_ips = sorted(
                    self.endpoint_requests[endpoint].items(),
                    key=lambda x: x[1][1]  # Sort by timestamp
                )
                # Keep only the most recent 100k entries
                self.endpoint_requests[endpoint] = dict(sorted_ips[-100000:])
            
        logger.info(f"Cleaned up rate limit data. Current endpoints: {len(self.endpoint_requests)}")

    def get_remaining_requests(self, endpoint: str, ip: str) -> int:
        if endpoint not in self.endpoint_requests or ip not in self.endpoint_requests[endpoint]:
            return self.requests_per_day
            
        count, first_request_time = self.endpoint_requests[endpoint][ip]
        if datetime.now() - first_request_time > timedelta(hours=24):
            return self.requests_per_day
            
        return max(0, self.requests_per_day - count)

    def get_reset_time(self, endpoint: str, ip: str) -> datetime:
        """Get the time when the rate limit will reset for an IP on a specific endpoint."""
        if endpoint not in self.endpoint_requests or ip not in self.endpoint_requests[endpoint]:
            return datetime.now()
        return self.endpoint_requests[endpoint][ip][1] + timedelta(hours=24)

# Create a singleton instance
rate_limiter = RateLimiter() 