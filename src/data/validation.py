# lead_scoring_system/src/data/validation.py
import re
import pandas as pd
from email_validator import validate_email, EmailNotValidError
import logging

class DataValidator:
    def __init__(self):
        """
        Initialize DataValidator.
        
        No runtime initialization is performed and no instance attributes are created. The module relies on the email-validator library for email checks (so a compiled email regex is not used); this constructor exists for API compatibility.
        """
        pass

    def validate_email(self, email: str) -> bool:
        """
        Return True if `email` is a valid and deliverable email address (syntax + MX check).
        
        Performs input checks (must be a non-empty string and not pandas NA), then delegates validation to
        email_validator.validate_email(...) with deliverability checking (MX record lookup). Any validation
        errors or unexpected exceptions are handled internally and result in False.
        
        Parameters:
            email (str): Email address to validate; non-string, empty, or NA values return False.
        
        Returns:
            bool: True if the address is syntactically valid and passes deliverability checks, False otherwise.
        """
        # Ensure the input is a non-empty string before validation
        if not isinstance(email, str) or not email or pd.isna(email):
            return False
            
        try:
            # The validate_email function checks for both syntax and MX records by default.
            # check_deliverability=True is the default, but we're explicit here.
            validate_email(email, check_deliverability=True)
            return True
        except EmailNotValidError as e:
            # Log the reason for the invalid email for debugging purposes.
            # Use logging.debug to avoid cluttering the console unless needed.
            logging.debug(f"Invalid email address '{email}': {e}")
            return False
        except Exception as e:
            # Catch other potential errors (e.g., DNS timeout during check)
            logging.warning(f"An unexpected error occurred validating email '{email}': {e}")
            return False

    def validate_phone(self, phone: str) -> bool:
        """
        Validate a phone number by normalizing digits and checking length.
        
        Returns True if `phone` is a non-empty value (not NA) that, after removing all non-digit characters, contains exactly 10 or 11 digits; otherwise returns False.
        
        Parameters:
            phone: The phone number to validate; may be any value convertible to string (common formats with spaces, dashes, parentheses, or country code are supported by the normalization step).
        """
        if not phone or pd.isna(phone):
            return False
        # Remove non-digits and check length
        digits = re.sub(r'\D', '', str(phone))
        return len(digits) == 10 or len(digits) == 11
    
    def validate_url(self, url: str) -> bool:
        if not url or pd.isna(url):
            return False
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))