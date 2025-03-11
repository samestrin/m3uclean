#!/usr/bin/env python3
"""
m3uclean - A tool for validating and cleaning M3U playlists.

This application validates M3U playlist entries, checks stream availability,
removes duplicates, and cleans malformed entries. 
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Optional

from m3uclean.parser import M3UParser
from m3uclean.validator import StreamValidator
from m3uclean.cleaner import EntryCleaner
from m3uclean.writer import PlaylistWriter


def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure the logger.
    
    Args:
        log_file: Path to log file. If None, logs to stderr.
        
    Returns:
        Configured logger instance.
    """
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('m3uclean')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        try:
            # Ensure the directory for the log file exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(log_formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to set up log file: {e}")
    
    return logger


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Clean and validate M3U playlists.')
    
    parser.add_argument('input_file', nargs='?', help='Path to input M3U playlist file')
    parser.add_argument('-o', '--output', help='Path to output M3U playlist file')
    parser.add_argument('-l', '--log', help='Path to log file')
    parser.add_argument('-v', '--validate', action='store_true', 
                        help='Validate stream URLs (slower but more thorough)')
    parser.add_argument('-a', '--aggressive', action='store_true',
                        help='Enable aggressive cleaning of entries')
    parser.add_argument('--slow', action='store_true',
                       help='Enable slow mode for more conservative rate limiting')
    
    args = parser.parse_args()
    
    # Get input file from args or environment
    input_file = args.input_file or os.environ.get('INPUT_FILE')
    if not input_file:
        parser.error("No input file specified. Use positional argument or INPUT_FILE environment variable.")
    
    # Validate input file exists
    if not os.path.exists(input_file):
        parser.error(f"Input file does not exist: {input_file}")
        
    # Override with environment variables if set
    output_file = args.output or os.environ.get('OUTPUT_FILE') or f"{input_file}.clean"
    
    # Validate output directory is writable
    output_dir = os.path.dirname(output_file) or '.'
    if not os.access(output_dir, os.W_OK):
        parser.error(f"Output directory is not writable: {output_dir}")
    
    log_file = args.log or os.environ.get('LOG_FILE')
    validate_streams = args.validate or os.environ.get('STREAM_VALIDATE', 'false').lower() in ('true', '1', 'yes')
    aggressive_clean = args.aggressive or os.environ.get('AGGRESSIVE_CLEAN', 'false').lower() in ('true', '1', 'yes')
    
    # Setup logging
    logger = setup_logger(args.log or os.environ.get('LOG_FILE'))
    
    # Now we can create the validator after logger exists
    validator = StreamValidator(logger, slow_mode=args.slow)
    
    logger.info("Starting m3uclean")
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")
    logger.info(f"Stream validation: {'Enabled' if validate_streams else 'Disabled'}")
    logger.info(f"Aggressive cleaning: {'Enabled' if aggressive_clean else 'Disabled'}")
    
    try:
        # Parse the M3U playlist
        m3u_parser = M3UParser(logger)
        playlist_entries = m3u_parser.parse(input_file)
        total_entries = len(playlist_entries)
        logger.info(f"Parsed {total_entries} entries from playlist")
        
        # Clean the entries
        entry_cleaner = EntryCleaner(logger, aggressive=aggressive_clean)
        cleaned_entries = entry_cleaner.clean(playlist_entries)
        cleaned_count = total_entries - len(cleaned_entries)
        logger.info(f"Removed {cleaned_count} duplicate or malformed entries")
        
        # Validate stream URLs if requested
        if validate_streams:
            validator = StreamValidator(logger)
            valid_entries = validator.validate(cleaned_entries)
            invalid_count = len(cleaned_entries) - len(valid_entries)
            logger.info(f"Removed {invalid_count} entries with invalid streams")
            final_entries = valid_entries
        else:
            final_entries = cleaned_entries
        
        # Write the final playlist
        writer = PlaylistWriter(logger)
        writer.write(final_entries, output_file)
        
        logger.info(f"Successfully wrote {len(final_entries)} entries to {output_file}")
        logger.info(f"Cleaning summary: {total_entries} entries -> {len(final_entries)} entries")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error processing playlist: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())