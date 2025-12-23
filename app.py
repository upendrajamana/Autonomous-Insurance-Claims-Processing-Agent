import json
import re
from pathlib import Path
import pdfplumber


class FNOLProcessor:

    MANDATORY_FIELDS = [
        "policy_number",
        "policyholder_name",
        "incident_date",
        "incident_location",
        "incident_description",
        "claim_type",
        "estimated_damage"
    ]

    FRAUD_KEYWORDS = ["fraud", "staged", "inconsistent"]
    FAST_TRACK_THRESHOLD = 25000

    def extract_text(self, file_path):
        path = Path(file_path)

        if path.suffix.lower() == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        if path.suffix.lower() == ".pdf":
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text

        raise ValueError("Unsupported file format")

    def extract_field(self, text, patterns):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def extract_fields(self, text):
        data = {}

        data["policy_number"] = self.extract_field(text, [
            r"Policy\s*(?:Number|No\.?)\s*:?\s*([A-Z0-9-]+)"
        ])

        data["policyholder_name"] = self.extract_field(text, [
            r"Policyholder\s*Name\s*:?\s*(.+)"
        ])

        data["incident_date"] = self.extract_field(text, [
            r"Incident\s*Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        ])

        data["incident_location"] = self.extract_field(text, [
            r"Incident\s*Location\s*:?\s*(.+)"
        ])

        data["incident_description"] = self.extract_field(text, [
            r"Incident\s*Description\s*:?\s*(.+)"
        ])

        data["claim_type"] = self.extract_field(text, [
            r"Claim\s*Type\s*:?\s*(.+)"
        ])

        damage = self.extract_field(text, [
            r"Estimated\s*Damage\s*:?\s*([\d,]+)"
        ])
        data["estimated_damage"] = float(damage.replace(",", "")) if damage else None

        return data

    def get_missing_fields(self, fields):
        missing = []
        for field in self.MANDATORY_FIELDS:
            if not fields.get(field):
                missing.append(field)
        return missing

    def has_fraud_terms(self, description):
        if not description:
            return False
        text = description.lower()
        return any(word in text for word in self.FRAUD_KEYWORDS)

    def decide_route(self, fields, missing_fields, fraud_flag):
        if missing_fields:
            return "Manual Review", f"Missing fields: {', '.join(missing_fields)}"

        if fraud_flag:
            return "Investigation", "Suspicious keywords found in description"

        claim_type = fields.get("claim_type", "").lower()
        if "injury" in claim_type:
            return "Specialist Queue", "Injury related claim"

        damage = fields.get("estimated_damage")
        if damage is not None and damage < self.FAST_TRACK_THRESHOLD:
            return "Fast-track", "Low damage claim"

        return "Standard Review", "Normal claim processing"

    def process(self, file_path):
        text = self.extract_text(file_path)
        fields = self.extract_fields(text)

        missing_fields = self.get_missing_fields(fields)
        fraud_flag = self.has_fraud_terms(fields.get("incident_description"))

        route, reason = self.decide_route(fields, missing_fields, fraud_flag)

        return {
            "extractedFields": fields,
            "missingFields": missing_fields,
            "recommendedRoute": route,
            "reasoning": reason
        }


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python app.py <fnol_file>")
        return

    processor = FNOLProcessor()
    result = processor.process(sys.argv[1])

    print(json.dumps(result, indent=2))

    output_file = Path(sys.argv[1]).stem + "_output.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nSaved output to {output_file}")


if __name__ == "__main__":
    main()
