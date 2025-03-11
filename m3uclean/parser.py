"""
Module for parsing M3U playlist files. 
"""

import os
import logging
from typing import List, Dict, Any, Optional


class M3UParser:
    """Parser for M3U playlist files."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize the M3U parser.
        
        Args:
            logger: Logger instance for logging events.
        """
        self.logger = logger
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse an M3U playlist file into a list of entries.
        
        Args:
            file_path: Path to the M3U playlist file.
            
        Returns:
            List of dictionary entries, each containing channel information.
            
        Raises:
            FileNotFoundError: If the playlist file does not exist.
            ValueError: If the playlist is not a valid M3U file.
        """
        if not os.path.exists(file_path):
            self.logger.error(f"Playlist file not found: {file_path}")
            raise FileNotFoundError(f"Playlist file not found: {file_path}")
        
        self.logger.info(f"Parsing playlist file: {file_path}")
        
        entries = []
        current_entry = None
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        # Verify this is an M3U file
        if not lines or not lines[0].strip().startswith('#EXTM3U'):
            self.logger.error(f"Not a valid M3U file: {file_path}")
            raise ValueError(f"Not a valid M3U file: {file_path}")
        
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line:
                continue
                
            if line.startswith('#EXTINF:'):
                # Parse the EXTINF line which contains channel metadata
                try:
                    # Format is typically: #EXTINF:-1 tvg-id="id" tvg-name="name" ... group-title="category",Channel Name
                    
                    # First, split at the comma to separate attributes and channel name
                    if ',' in line:
                        attrs_part, channel_name = line.split(',', 1)
                    else:
                        attrs_part, channel_name = line, ""
                    
                    # Initialize a new entry
                    current_entry = {
                        'name': channel_name.strip(),
                        'attributes': {},
                        'raw_info': line
                    }
                    
                    # Parse the duration and any tvg attributes
                    parts = attrs_part.split()
                    for part in parts:
                        if part.startswith('#EXTINF:'):
                            # Extract duration: #EXTINF:-1
                            try:
                                duration = part.split(':')[1].strip()
                                current_entry['duration'] = duration
                            except (IndexError, ValueError):
                                current_entry['duration'] = '-1'
                        elif '=' in part:
                            # Extract attributes like tvg-id="value"
                            try:
                                attr_name, attr_value = part.split('=', 1)
                                # Remove quotes if present
                                attr_value = attr_value.strip('"\'')
                                current_entry['attributes'][attr_name] = attr_value
                            except ValueError:
                                continue
                
                except Exception as e:
                    self.logger.warning(f"Error parsing line {line_number}: {line} - {e}")
                    current_entry = None
            
            elif line.startswith('#') and current_entry is not None:
                # Other comments or directives - store as additional info
                if 'additional_info' not in current_entry:
                    current_entry['additional_info'] = []
                current_entry['additional_info'].append(line)
            
            elif not line.startswith('#') and current_entry is not None:
                # This should be the URL line that follows an EXTINF line
                current_entry['url'] = line
                entries.append(current_entry)
                current_entry = None
            
            elif not line.startswith('#'):
                # URL without preceding EXTINF - create a minimal entry
                self.logger.warning(f"Line {line_number}: URL without EXTINF metadata: {line}")
                entries.append({
                    'name': f"Unknown Channel {line_number}",
                    'url': line,
                    'attributes': {},
                    'raw_info': f"#EXTINF:-1,Unknown Channel {line_number}"
                })
        
        if current_entry is not None:
            self.logger.warning("Last entry was incomplete (missing URL)")
        
        self.logger.info(f"Parsed {len(entries)} entries from playlist")
        return entries