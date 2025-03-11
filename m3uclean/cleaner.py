"""
Module for cleaning and deduplicating M3U playlist entries. 
"""

import re
import logging
from typing import List, Dict, Any, Set
import html


class EntryCleaner:
    """Cleaner for M3U playlist entries."""
    
    def __init__(self, logger: logging.Logger, aggressive: bool = False):
        """
        Initialize the entry cleaner.
        
        Args:
            logger: Logger instance for logging events.
            aggressive: Whether to use aggressive cleaning.
        """
        self.logger = logger
        self.aggressive = aggressive
    
    def clean(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and deduplicate playlist entries.
        
        Args:
            entries: List of playlist entries to clean.
            
        Returns:
            List of cleaned and deduplicated entries.
        """
        self.logger.info(f"Cleaning {len(entries)} entries (aggressive={self.aggressive})")
        
        cleaned_entries = []
        seen_urls = set()  # For deduplication
        
        for entry in entries:
            # Skip entries without URLs
            if 'url' not in entry or not entry['url'].strip():
                self.logger.warning(f"Skipping entry without URL: {entry.get('name', 'Unknown')}")
                continue
            
            # Clean the URL
            original_url = entry['url']
            entry['url'] = self.clean_url(original_url)
            
            # Check if this is a duplicate URL
            if entry['url'] in seen_urls:
                self.logger.info(f"Removing duplicate URL: {entry['url']} ({entry.get('name', 'Unknown')})")
                continue
            
            # Clean the channel name and attributes
            if 'name' in entry:
                original_name = entry['name']
                entry['name'] = self.clean_text(original_name)
                
                if original_name != entry['name']:
                    self.logger.debug(f"Cleaned channel name: '{original_name}' -> '{entry['name']}'")
            
            # Clean attributes
            if 'attributes' in entry and isinstance(entry['attributes'], dict):
                for key, value in list(entry['attributes'].items()):
                    cleaned_value = self.clean_text(value)
                    
                    if value != cleaned_value:
                        self.logger.debug(f"Cleaned attribute '{key}': '{value}' -> '{cleaned_value}'")
                        entry['attributes'][key] = cleaned_value
            
            # Regenerate raw_info with cleaned values
            self.regenerate_raw_info(entry)
            
            # Add to cleaned entries and mark URL as seen
            cleaned_entries.append(entry)
            seen_urls.add(entry['url'])
        
        self.logger.info(f"Cleaning complete: {len(cleaned_entries)} entries after cleaning and deduplication")
        return cleaned_entries
    
    def clean_url(self, url: str) -> str:
        """
        Clean a URL by removing whitespace and normalizing.
        
        Args:
            url: The URL to clean.
            
        Returns:
            The cleaned URL.
        """
        # Strip whitespace
        url = url.strip()
        
        # Ensure proper protocol prefix
        if url and not (url.startswith('http://') or url.startswith('https://') or 
                       url.startswith('rtmp://') or url.startswith('rtsp://')):
            # If URL starts with //, add http:
            if url.startswith('//'):
                url = 'http:' + url
        
        return url
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing or replacing problematic characters.
        
        Args:
            text: The text to clean.
            
        Returns:
            The cleaned text.
        """
        if not text:
            return text
            
        # Decode HTML entities
        text = html.unescape(text)
        
        if self.aggressive:
            # First remove already-encoded entities before aggressive cleaning
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            text = text.replace('&apos;', "'")
            
            # Remove HTML/XML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Remove special characters
            text = re.sub(r'[&<>\'"\\\[\]{}]', '', text)
            
            # Replace multiple spaces with a single space
            text = re.sub(r'\s+', ' ', text)
        else:
            # Standard cleaning: only encode unencoded special characters
            text = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', text)
            text = re.sub(r'<(?![^>]*>)', '&lt;', text)
            text = re.sub(r'>(?![^<]*<)', '&gt;', text)
            text = text.replace('"', '&quot;')
            text = text.replace("'", '&apos;')
        
        return text.strip()
    
    def regenerate_raw_info(self, entry: Dict[str, Any]) -> None:
        """
        Regenerate the raw_info field with cleaned values.
        
        Args:
            entry: The entry to update.
        """
        duration = entry.get('duration', '-1')
        name = entry.get('name', 'Unknown')
        
        # Build attributes string
        attrs = []
        if 'attributes' in entry and isinstance(entry['attributes'], dict):
            for key, value in entry['attributes'].items():
                attrs.append(f'{key}="{value}"')
        
        # Regenerate EXTINF line
        attrs_str = ' '.join(attrs)
        if attrs_str:
            raw_info = f'#EXTINF:{duration} {attrs_str},{name}'
        else:
            raw_info = f'#EXTINF:{duration},{name}'
        
        entry['raw_info'] = raw_info

    def clean_entry(self, entry: Dict[str, str]) -> Dict[str, str]:
        cleaned = entry.copy()
        
        # Clean group-title without affecting other attributes
        if 'group-title' in cleaned:
            cleaned['group-title'] = self.clean_text(cleaned['group-title'])
            
        # We should NOT modify tvg-name as it's a critical identifier
        return cleaned