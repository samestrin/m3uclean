"""
Module for writing cleaned M3U playlists to files. 
"""

import os
import logging
from typing import List, Dict, Any


class PlaylistWriter:
    """Writer for M3U playlist files."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize the playlist writer.
        
        Args:
            logger: Logger instance for logging events.
        """
        self.logger = logger
    
    def write(self, entries: List[Dict[str, Any]], output_file: str) -> None:
        """
        Write a list of entries to an M3U playlist file.
        
        Args:
            entries: List of playlist entries to write.
            output_file: Path to the output M3U file.
            
        Raises:
            IOError: If the output file cannot be written.
        """
        self.logger.info(f"Writing {len(entries)} entries to {output_file}")
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write the M3U header
                f.write("#EXTM3U\n")
                
                # Write each entry
                for entry in entries:
                    # Write the info line
                    f.write(f"{entry['raw_info']}\n")
                    
                    # Write any additional info
                    if 'additional_info' in entry and isinstance(entry['additional_info'], list):
                        for info in entry['additional_info']:
                            f.write(f"{info}\n")
                    
                    # Write the URL
                    f.write(f"{entry['url']}\n")
            
            self.logger.info(f"Successfully wrote playlist to {output_file}")
        
        except IOError as e:
            self.logger.error(f"Error writing playlist to {output_file}: {e}")
            raise