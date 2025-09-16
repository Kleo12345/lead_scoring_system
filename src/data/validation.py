# lead_scoring_system/src/data/validation.py
import re
from email_validator import validate_email, EmailNotValidError

class DataValidator:
    def __init__(self):
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
    def validate_email_syntax(self, email: str) -> bool:
        if not email or pd.isna(email):
            return False
        return bool(self.email_regex.match(email))
    
    def validate_phone(self, phone: str) -> bool:
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