"""
Google Sheets Handler
Manages reading video requests and writing results to Google Sheets
"""

import logging
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleSheetsHandler:
    """Handle Google Sheets operations for video automation"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Initialize Google Sheets handler
        
        Args:
            credentials_path: Path to Google service account credentials JSON
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials = self._load_credentials(credentials_path)
        self.service = build('sheets', 'v4', credentials=self.credentials)
        
    def _load_credentials(self, credentials_path: str):
        """Load Google service account credentials"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        try:
            credentials = ServiceAccountCredentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )
            logger.info("Google Sheets credentials loaded successfully")
            return credentials
        except Exception as e:
            logger.error(f"Failed to load credentials: {str(e)}")
            raise
    
    def get_pending_videos(self, sheet_name: str) -> List[Dict]:
        """
        Get all pending video requests from the input sheet
        
        Args:
            sheet_name: Name of the sheet to read from
            
        Returns:
            List of dictionaries containing video request data
        """
        try:
            # Read the sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:E"  # Adjust range as needed
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.info("No data found in sheet")
                return []
            
            # Assume first row is headers
            headers = values[0]
            pending_videos = []
            
            for i, row in enumerate(values[1:], start=2):
                # Skip if row is marked as processed
                if len(row) > 3 and row[3].lower() == 'completed':
                    continue
                
                # Parse row data
                video_data = {
                    'id': row[0] if len(row) > 0 else f"video_{i}",
                    'topic': row[1] if len(row) > 1 else '',
                    'prompts': row[2] if len(row) > 2 else '',
                    'status': row[3] if len(row) > 3 else 'pending',
                    'row_number': i
                }
                
                if video_data['topic']:  # Only include rows with topics
                    pending_videos.append(video_data)
            
            logger.info(f"Found {len(pending_videos)} pending videos")
            return pending_videos
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error reading sheet: {str(e)}")
            raise
    
    def update_row_status(self, sheet_name: str, row_number: int, status: str):
        """
        Update the status of a specific row
        
        Args:
            sheet_name: Name of the sheet
            row_number: Row number to update (1-indexed)
            status: New status value
        """
        try:
            range_name = f"{sheet_name}!D{row_number}"  # Column D is status
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [[status]]}
            ).execute()
            
            logger.info(f"Updated row {row_number} status to: {status}")
            
        except Exception as e:
            logger.error(f"Error updating row status: {str(e)}")
            raise
    
    def append_to_sheet(self, sheet_name: str, rows: List[Dict]):
        """
        Append rows to a sheet
        
        Args:
            sheet_name: Name of the sheet to append to
            rows: List of dictionaries to append
        """
        try:
            # Convert dictionaries to rows
            if not rows:
                return
            
            # Get headers from first row
            headers = list(rows[0].keys())
            values = [[row.get(h, '') for h in headers] for row in rows]
            
            # Check if sheet has headers, if not add them
            try:
                existing = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1:Z1"
                ).execute()
                
                if not existing.get('values'):
                    # Add headers
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{sheet_name}!A1",
                        valueInputOption='RAW',
                        body={'values': [headers]}
                    ).execute()
            except:
                pass
            
            # Append the data
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:Z",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': values}
            ).execute()
            
            logger.info(f"Appended {len(rows)} rows to {sheet_name}")
            
        except Exception as e:
            logger.error(f"Error appending to sheet: {str(e)}")
            raise
    
    def create_sheet_if_not_exists(self, sheet_name: str):
        """
        Create a new sheet if it doesn't exist
        
        Args:
            sheet_name: Name of the sheet to create
        """
        try:
            # Get spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            # Check if sheet exists
            sheets = spreadsheet.get('sheets', [])
            sheet_names = [s['properties']['title'] for s in sheets]
            
            if sheet_name not in sheet_names:
                # Create the sheet
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }
                
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
                
                logger.info(f"Created new sheet: {sheet_name}")
            
        except Exception as e:
            logger.error(f"Error creating sheet: {str(e)}")
            raise


def setup_sample_sheet(handler: GoogleSheetsHandler):
    """
    Set up a sample input sheet with example data
    
    Args:
        handler: GoogleSheetsHandler instance
    """
    # Create sample sheet
    handler.create_sheet_if_not_exists("Video Ideas")
    
    # Add sample data
    sample_data = [
        {
            'id': 'video_001',
            'topic': '5 Tips for Better Sleep',
            'prompts': 'Create a calm, informative video about sleep hygiene. Include visuals of bedrooms and peaceful scenes.',
            'status': 'pending'
        },
        {
            'id': 'video_002',
            'topic': 'The Future of AI in 2025',
            'prompts': 'Discuss recent AI developments, breakthroughs, and predictions. Use futuristic visuals and tech imagery.',
            'status': 'pending'
        }
    ]
    
    handler.append_to_sheet("Video Ideas", sample_data)
    logger.info("Sample sheet created with example videos")
