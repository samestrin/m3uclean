"""
Module for validating stream URLs in M3U playlists. 
"""

import logging
import time
import concurrent.futures
from typing import List, Dict, Any, Tuple
import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class StreamValidator:
    """Validator for checking stream URLs in M3U playlists."""
    
    def __init__(self, logger: logging.Logger, timeout: int = 10, max_workers: int = 10, 
                 slow_mode: bool = False):
        """
        Initialize the stream validator.
        
        Args:
            logger: Logger instance for logging events.
            timeout: Timeout in seconds for stream validation requests.
            max_workers: Maximum number of concurrent workers for validation.
            slow_mode: If True, uses more conservative rate limiting.
        """
        self.logger = logger
        self.timeout = timeout
        self.max_workers = 1 if slow_mode else max_workers
        self.slow_mode = slow_mode
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'm3uclean/1.0 Stream Validator'
        })
        # Rate limiting parameters
        self.min_wait = 10 if slow_mode else 4
        self.max_wait = 30 if slow_mode else 10
        self.last_request_time = {}  # Track last request time per domain
        self.rate_limit_delays = {}  # Track increasing delays per domain
        self.rate_limit_base_delay = 60  # Base delay for rate limits (1 minute)

    def _handle_rate_limit(self, domain: str) -> None:
        """Handle rate limiting by implementing exponential backoff per domain"""
        current_delay = self.rate_limit_delays.get(domain, self.rate_limit_base_delay)
        self.logger.warning(f"Rate limited on {domain}, waiting {current_delay} seconds")
        time.sleep(current_delay)
        
        # Increase delay for next rate limit (max 5 minutes)
        self.rate_limit_delays[domain] = min(current_delay * 2, 300)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError)),
        before_sleep=lambda retry_state: time.sleep(1)
    )
    def _make_request(self, url: str, method: str = 'head') -> requests.Response:
        domain = self._get_domain(url)
        
        # Standard rate limiting
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.min_wait:
                time.sleep(self.min_wait - elapsed)
        
        self.last_request_time[domain] = time.time()
        
        request_func = self.session.head if method == 'head' else self.session.get
        response = request_func(
            url,
            timeout=self.timeout,
            allow_redirects=True,
            stream=(method == 'get')
        )
        
        # Handle rate limiting response
        if response.status_code == 429:
            self._handle_rate_limit(domain)
            raise RequestException("Rate limited, retrying after backoff")
            
        return response

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for rate limiting"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url

    def validate(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate stream URLs in parallel and return only valid entries.
        
        Args:
            entries: List of playlist entries to validate.
            
        Returns:
            List of entries with valid streams.
        """
        self.logger.info(f"Validating {len(entries)} stream URLs")
        
        valid_entries = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all validation tasks
            future_to_entry = {
                executor.submit(self.validate_stream, entry): entry 
                for entry in entries
            }
            
            # Process results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(future_to_entry), 1):
                entry = future_to_entry[future]
                valid, message = future.result()
                
                if valid:
                    valid_entries.append(entry)
                    self.logger.debug(f"[{i}/{len(entries)}] Valid stream: {entry.get('name')} - {entry.get('url')}")
                else:
                    self.logger.info(f"[{i}/{len(entries)}] Invalid stream: {entry.get('name')} - {entry.get('url')} - {message}")
                
                # Log progress periodically
                if i % 10 == 0 or i == len(entries):
                    self.logger.info(f"Validated {i}/{len(entries)} streams...")
        
        self.logger.info(f"Validation complete: {len(valid_entries)}/{len(entries)} streams are valid")
        return valid_entries

    def validate_stream(self, entry: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single stream URL by making a HEAD or GET request.
        
        Args:
            entry: Playlist entry containing the URL to validate.
            
        Returns:
            Tuple of (is_valid, message).
        """
        url = entry.get('url', '').strip()
        
        if not url:
            return False, "Empty URL"
        
        if not (url.startswith('http://') or url.startswith('https://') or 
                url.startswith('rtmp://') or url.startswith('rtsp://')):
            # Non-HTTP streams (like local files) are considered valid
            return True, "Non-HTTP stream"
        
        try:
            # First try a HEAD request as it's faster
            response = self.session.head(
                url, 
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # If the HEAD request is not supported or returns an error, try a GET request
            if response.status_code >= 400:
                # Use stream=True to avoid downloading the entire content
                response = self.session.get(
                    url, 
                    timeout=self.timeout,
                    stream=True,
                    allow_redirects=True
                )
                # Just read a small portion to validate
                response.raw.read(1024)
            
            if response.status_code < 400:
                return True, f"Status: {response.status_code}"
            else:
                return False, f"HTTP error: {response.status_code}"
                
        except RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"