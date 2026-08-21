import re

class ModerationService:
    BLOCKED_TERMS = [
        "batman", "superman", "spiderman", "ironman", "avengers",
        "mickey mouse", "disney", "star wars",
        "manchester united", "chelsea", "arsenal", "liverpool",
        "nike", "adidas", "gucci", "louis vuitton",
        "nsfw", "nude", "naked", "sex", "porn", "blood", "gore"
    ]

    @classmethod
    def check_instructions(cls, text: str) -> tuple[bool, list[str]]:
        if not text:
            return True, []
            
        found_terms = []
        lower_text = text.lower()
        for term in cls.BLOCKED_TERMS:
            # simple substring check for now, can be improved with word boundaries
            if term in lower_text:
                found_terms.append(term)
                
        return len(found_terms) == 0, found_terms

    @classmethod
    def sanitize_instructions(cls, text: str) -> str:
        if not text:
            return text
            
        sanitized = text
        for term in cls.BLOCKED_TERMS:
            # Case insensitive replace
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            sanitized = pattern.sub("***", sanitized)
            
        return sanitized
