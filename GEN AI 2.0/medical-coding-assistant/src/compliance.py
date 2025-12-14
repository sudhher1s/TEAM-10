"""
HIPAA compliance and PHI detection for Medical Coding Assistant
"""
from __future__ import annotations
import re
import hashlib
from datetime import datetime
from typing import Tuple, List, Dict
from .models import Database


class PHIDetectionRegex:
    """Regex patterns for common PHI detection (rule-based fallback)"""
    
    # Patient names - basic pattern (3+ words)
    PATIENT_NAME_PATTERN = r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b'
    
    # SSN pattern
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    
    # Phone numbers
    PHONE_PATTERN = r'\b(\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4}\b'
    
    # Email addresses
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Medical record numbers
    MRN_PATTERN = r'\bMRN[:\s]*(\d{5,10})\b'
    
    # Date of birth (various formats)
    DOB_PATTERN = r'\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-](\d{4}|\d{2})\b'
    
    # Age (specific mention of patient age)
    AGE_PATTERN = r'\b(patient|pt|male|female)\s+(\d{1,3})\s*(?:yo|year|years|old)\b'
    
    # Hospital/Facility names (common patterns)
    FACILITY_PATTERN = r'\b(Hospital|Clinic|Medical Center|Health System|University)\b'
    
    # Medication with specific patient info
    MEDICATION_PATTERN = r'\b(prescribed|rx:|medication:)\s+[A-Za-z\d\s]+\s+to\s+[A-Z][a-z]+\b'


class PHIDetector:
    """Comprehensive PHI detection using regex and heuristics"""
    
    def __init__(self):
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns"""
        return {
            "ssn": re.compile(PHIDetectionRegex.SSN_PATTERN),
            "phone": re.compile(PHIDetectionRegex.PHONE_PATTERN, re.IGNORECASE),
            "email": re.compile(PHIDetectionRegex.EMAIL_PATTERN, re.IGNORECASE),
            "mrn": re.compile(PHIDetectionRegex.MRN_PATTERN, re.IGNORECASE),
            "dob": re.compile(PHIDetectionRegex.DOB_PATTERN),
            "age": re.compile(PHIDetectionRegex.AGE_PATTERN, re.IGNORECASE),
            "facility": re.compile(PHIDetectionRegex.FACILITY_PATTERN),
        }

    def detect_phi(self, note_text: str) -> Tuple[bool, List[str], Dict[str, List[str]]]:
        """
        Detect PHI in clinical note
        
        Returns:
            (is_safe, detected_fields, matches_detail)
        """
        detected_fields = []
        matches_detail = {}

        # Check each pattern
        for field_name, pattern in self.patterns.items():
            matches = pattern.findall(note_text)
            if matches:
                detected_fields.append(field_name)
                matches_detail[field_name] = matches if isinstance(matches[0], str) else [str(m) for m in matches]

        # Check for patient name pattern
        name_matches = re.findall(PHIDetectionRegex.PATIENT_NAME_PATTERN, note_text)
        if name_matches:
            detected_fields.append("patient_name")
            matches_detail["patient_name"] = name_matches

        # Heuristic: Check for specific patient identifiers
        if re.search(r'\bpatient\s+(?:named|name|is)\s+[A-Z][a-z]+', note_text, re.IGNORECASE):
            detected_fields.append("patient_identifier")

        # Remove duplicates
        detected_fields = list(set(detected_fields))

        # Note is safe if no PHI detected
        is_safe = len(detected_fields) == 0

        return is_safe, detected_fields, matches_detail

    def redact_phi(self, note_text: str) -> str:
        """Redact PHI from note (for logging/storage)"""
        redacted = note_text
        
        # Redact each pattern
        redacted = self.patterns["ssn"].sub("[SSN]", redacted)
        redacted = self.patterns["phone"].sub("[PHONE]", redacted)
        redacted = self.patterns["email"].sub("[EMAIL]", redacted)
        redacted = self.patterns["mrn"].sub("[MRN]", redacted)
        redacted = self.patterns["dob"].sub("[DOB]", redacted)
        redacted = self.patterns["age"].sub("[AGE]", redacted)

        return redacted


class HIPAACompliance:
    """HIPAA compliance tracking and enforcement"""
    
    def __init__(self, db: Database):
        self.db = db
        self.phi_detector = PHIDetector()

    def check_note_compliance(self, note_text: str, user_id: int) -> Tuple[bool, Dict]:
        """
        Check if note meets HIPAA requirements
        
        Returns:
            (is_compliant, compliance_report)
        """
        is_safe, detected_fields, matches_detail = self.phi_detector.detect_phi(note_text)
        
        # Hash the note for compliance log
        note_hash = hashlib.sha256(note_text.encode()).hexdigest()
        
        # Log compliance check
        self.db.log_compliance(user_id, note_hash, is_safe, detected_fields)

        compliance_report = {
            "is_compliant": is_safe,
            "note_hash": note_hash,
            "phi_detected": not is_safe,
            "detected_fields": detected_fields,
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": self._get_recommendations(detected_fields)
        }

        return is_safe, compliance_report

    def _get_recommendations(self, detected_fields: List[str]) -> List[str]:
        """Get HIPAA compliance recommendations"""
        recommendations = []

        field_recommendations = {
            "ssn": "Remove or mask Social Security Numbers",
            "phone": "Remove or mask phone numbers",
            "email": "Remove or mask email addresses",
            "mrn": "Remove or generalize Medical Record Numbers",
            "dob": "Use age instead of specific date of birth",
            "patient_name": "Remove patient names (use de-identified ID instead)",
            "facility": "Use facility role rather than specific name",
        }

        for field in detected_fields:
            if field in field_recommendations:
                recommendations.append(field_recommendations[field])

        return recommendations

    def get_compliance_dashboard(self) -> Dict:
        """Get compliance dashboard data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get compliance stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_checks,
                SUM(CASE WHEN phi_check_result = 1 THEN 1 ELSE 0 END) as passed_checks,
                SUM(CASE WHEN phi_check_result = 0 THEN 1 ELSE 0 END) as failed_checks
            FROM compliance_logs
        """)
        
        stats = cursor.fetchone()
        conn.close()

        total = stats[0] or 0
        passed = stats[1] or 0
        failed = stats[2] or 0

        return {
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "compliance_rate": (passed / total * 100) if total > 0 else 0,
            "status": "COMPLIANT" if (passed / total * 100) > 95 else "REVIEW_NEEDED" if total > 0 else "NO_DATA"
        }


class HIPAADisclaimer:
    """HIPAA-related disclaimers and legal text"""
    
    EDUCATIONAL_DISCLAIMER = """
    DISCLAIMER: This Medical Coding Assistant is provided for EDUCATIONAL PURPOSES ONLY.
    
    This system is not intended to:
    - Replace professional medical coding
    - Provide medical advice
    - Substitute for professional judgment
    
    Important:
    ✓ Always verify predictions with clinical documentation
    ✓ ICD-10 coding should be reviewed by certified coders
    ✓ Patient safety and accuracy are paramount
    ✓ De-identified data only - remove all PHI before submission
    
    HIPAA Notice:
    ✓ No PHI is stored permanently
    ✓ All data processed in-memory only
    ✓ Compliance logs maintained for audit purposes
    ✓ Access controlled via role-based authorization
    """

    PHI_WARNING = """
    ⚠️ PHI DETECTED - NOTE CANNOT BE PROCESSED
    
    The submitted note contains Protected Health Information (PHI) that must be removed:
    {detected_fields}
    
    Please de-identify the note by:
    • Removing patient names
    • Using age instead of birth date
    • Removing SSN, MRN, and phone numbers
    • Removing email addresses
    • Using generic facility references
    
    Once de-identified, resubmit the note for analysis.
    """

    HIPAA_COMPLIANCE_SUMMARY = """
    HIPAA COMPLIANCE SUMMARY
    
    Administrative Safeguards:
    ✓ Role-based access control (Doctor, Admin, Auditor)
    ✓ Unique user identification and authentication
    ✓ Access audit logs and controls
    ✓ Security awareness and training
    
    Technical Safeguards:
    ✓ Access controls (usernames, passwords, JWT tokens)
    ✓ Audit controls (comprehensive audit logging)
    ✓ Encryption (password hashing, token signing)
    ✓ Transmission security (HTTPS in production)
    ✓ PHI detection and redaction
    
    Physical Safeguards:
    ✓ Data stored on secured database
    ✓ In-memory processing (no persistent PHI storage)
    ✓ Facility access controls (application-level)
    """

    @staticmethod
    def get_disclaimer() -> str:
        """Get educational disclaimer"""
        return HIPAADisclaimer.EDUCATIONAL_DISCLAIMER

    @staticmethod
    def get_phi_warning(detected_fields: List[str]) -> str:
        """Get PHI warning with detected fields"""
        fields_text = "\n".join([f"  • {field}" for field in detected_fields])
        return HIPAADisclaimer.PHI_WARNING.format(detected_fields=fields_text)

    @staticmethod
    def get_compliance_summary() -> str:
        """Get HIPAA compliance summary"""
        return HIPAADisclaimer.HIPAA_COMPLIANCE_SUMMARY
