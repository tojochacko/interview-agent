# Feature: Structured Data Normalization (Inverse Text Normalization)

**Status**: Planned
**Priority**: High
**Complexity**: Medium
**Estimated Time**: 6-8 hours

## Problem Statement

When users speak structured data like email addresses or phone numbers during interviews, the STT system transcribes them phonetically rather than in their proper written format:

**Current Behavior (❌):**
- User says: "My email is john dot smith at gmail dot com"
- STT output: `"my email is john dot smith at gmail dot com"`
- Saved to CSV: `"my email is john dot smith at gmail dot com"`

**Desired Behavior (✅):**
- User says: "My email is john dot smith at gmail dot com"
- STT output: `"my email is john dot smith at gmail dot com"`
- **Post-processing**: Normalize to `"my email is john.smith@gmail.com"`
- Saved to CSV: `"my email is john.smith@gmail.com"`

## Scope

### Structured Data Types to Support

1. **Email Addresses** (Priority: High)
   - "john dot smith at gmail dot com" → "john.smith@gmail.com"
   - "jane underscore doe at company dot org" → "jane_doe@company.org"
   - "support dash team at example dot co dot uk" → "support-team@example.co.uk"

2. **Phone Numbers** (Priority: High)
   - "five five five one two three four" → "555-1234"
   - "one eight hundred five five five zero one zero one" → "1-800-555-0101"
   - "plus one four one five five five five one two three four" → "+1-415-555-1234"
   - "area code four one five five five five one two three four" → "(415) 555-1234"

3. **Dates** (Priority: Medium)
   - "january first two thousand twenty five" → "01/01/2025"
   - "first of january twenty twenty five" → "01/01/2025"
   - "one slash one slash twenty five" → "01/01/2025"

4. **Numbers & Currency** (Priority: Medium)
   - "one hundred twenty three" → "123"
   - "twenty dollars" → "$20"
   - "three point five" → "3.5"

5. **Times** (Priority: Low)
   - "three thirty p m" → "3:30 PM"
   - "half past two" → "2:30"

6. **URLs** (Priority: Low)
   - "h t t p colon slash slash w w w dot example dot com" → "http://www.example.com"

## Research Summary

### Industry Solutions

| Solution | Type | Pros | Cons | Recommendation |
|----------|------|------|------|----------------|
| **NVIDIA NeMo ITN** | WFST-based | Production-ready, deterministic, comprehensive | External dependency (300MB+) | **⭐ BEST for production** |
| **Custom Regex** | Rule-based | Lightweight, no dependencies, fast | Must handle edge cases manually | **Good for MVP** |
| **LLM Post-processing** | Neural | Intelligent context handling | Slow (1-2s), non-deterministic | Optional enhancement |
| **Cloud APIs** | Managed | Built-in ITN | Requires cloud, breaks offline | Not suitable |

### Benchmarks

**NeMo ITN Accuracy:**
- Email addresses: ~99% accuracy
- Phone numbers: ~98% accuracy
- Dates/currency: ~99% accuracy
- Processing speed: <10ms per sentence

**Custom Regex:**
- Email addresses: ~95% accuracy (with good patterns)
- Phone numbers: ~90% accuracy (varies by format)
- Processing speed: <1ms per sentence

## Proposed Solution

### Architecture: Hybrid Approach

**Phase 1: Lightweight Regex Post-Processor (MVP)** ⭐ Start Here
- Add `TextNormalizer` class with regex-based patterns
- Focus on emails and phone numbers (highest priority)
- Zero external dependencies
- Fast (<1ms per response)

**Phase 2: NeMo ITN Integration (Production)**
- Add optional NeMo dependency
- Support all structured data types
- Provider pattern: `RegexNormalizer` (default) vs `NeMoNormalizer` (optional)
- Configurable via `NORMALIZATION_PROVIDER` env var

**Phase 3: LLM Enhancement (Future)**
- Optional LLM pass for ambiguous cases
- User-configurable via `NORMALIZATION_USE_LLM` flag
- Fallback to regex if LLM unavailable

## Implementation Plan

### Phase 1: Regex-Based Text Normalization (6-8 hours)

#### Step 1: Create Core Normalizer Module (2 hours)

**File**: `src/conversation_agent/core/text_normalizer.py`

```python
"""Text normalization for structured data (emails, phone numbers, etc.)."""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class TextNormalizer:
    """Normalize spoken-domain text to written-domain format.

    Handles email addresses, phone numbers, and other structured data
    that STT systems transcribe phonetically.

    Example:
        normalizer = TextNormalizer()
        text = "my email is john dot smith at gmail dot com"
        normalized = normalizer.normalize(text)
        # "my email is john.smith@gmail.com"
    """

    def __init__(self, enable_emails: bool = True, enable_phones: bool = True):
        """Initialize normalizer with enabled features."""
        self.enable_emails = enable_emails
        self.enable_phones = enable_phones

        # Compile regex patterns once for performance
        self._compile_patterns()

    def normalize(self, text: str) -> str:
        """Normalize all structured data in text.

        Args:
            text: Raw STT transcription

        Returns:
            Normalized text with structured data formatted properly
        """
        if not text:
            return text

        original = text

        # Apply normalizations in order
        if self.enable_emails:
            text = self._normalize_emails(text)

        if self.enable_phones:
            text = self._normalize_phone_numbers(text)

        # Log if changes were made
        if text != original:
            logger.info(f"📝 Normalized: '{original}' → '{text}'")

        return text

    def _normalize_emails(self, text: str) -> str:
        """Normalize email addresses.

        Patterns supported:
        - john dot smith at gmail dot com → john.smith@gmail.com
        - jane underscore doe at company dot org → jane_doe@company.org
        - support dash team at example dot co dot uk → support-team@example.co.uk
        """
        # Pattern: word (dot|underscore|dash word)* at word (dot word)+
        # This captures: "john dot smith at gmail dot com"

        # Step 1: Find potential email patterns
        email_pattern = re.compile(
            r'\b([a-z0-9]+(?:\s+(?:dot|underscore|dash)\s+[a-z0-9]+)*)'
            r'\s+at\s+'
            r'([a-z0-9]+(?:\s+dot\s+[a-z0-9]+)+)\b',
            re.IGNORECASE
        )

        def replace_email(match: re.Match) -> str:
            local = match.group(1)  # "john dot smith"
            domain = match.group(2)  # "gmail dot com"

            # Convert local part
            local = local.replace(' dot ', '.')
            local = local.replace(' underscore ', '_')
            local = local.replace(' dash ', '-')
            local = local.replace(' ', '')

            # Convert domain part
            domain = domain.replace(' dot ', '.')
            domain = domain.replace(' ', '')

            email = f"{local}@{domain}"
            logger.debug(f"Email normalized: {match.group(0)} → {email}")
            return email

        return email_pattern.sub(replace_email, text)

    def _normalize_phone_numbers(self, text: str) -> str:
        """Normalize phone numbers.

        Patterns supported:
        - five five five one two three four → 555-1234
        - one eight hundred five five five zero one zero one → 1-800-555-0101
        - plus one four one five five five five one two three four → +1-415-555-1234
        """
        # Word-to-digit mapping
        word_to_digit = {
            'zero': '0', 'oh': '0', 'o': '0',
            'one': '1',
            'two': '2', 'to': '2', 'too': '2',
            'three': '3',
            'four': '4', 'for': '4',
            'five': '5',
            'six': '6',
            'seven': '7',
            'eight': '8', 'ate': '8',
            'nine': '9',
        }

        # Pattern: sequence of digit words (possibly with "plus" prefix)
        # This captures: "five five five one two three four"
        phone_pattern = re.compile(
            r'\b(plus\s+)?'  # Optional "plus" for international
            r'((?:zero|oh|o|one|two|to|too|three|four|for|five|six|seven|eight|ate|nine)'
            r'(?:\s+(?:zero|oh|o|one|two|to|too|three|four|for|five|six|seven|eight|ate|nine))+)\b',
            re.IGNORECASE
        )

        def replace_phone(match: re.Match) -> str:
            prefix = match.group(1)  # "plus " or None
            words = match.group(2).lower().split()  # ["five", "five", "five", ...]

            # Convert words to digits
            digits = ''.join(word_to_digit.get(w, w) for w in words)

            # Only format if it looks like a phone number (7-15 digits)
            if not (7 <= len(digits) <= 15):
                return match.group(0)  # Keep original

            # Format based on length
            if prefix:
                # International: +1-415-555-1234
                if len(digits) == 11:  # e.g., 14155551234
                    return f"+{digits[0]}-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
                elif len(digits) == 10:  # e.g., 4155551234
                    return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
            else:
                # US format
                if len(digits) == 10:  # e.g., 4155551234
                    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                elif len(digits) == 11 and digits[0] == '1':  # e.g., 14155551234
                    return f"1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
                elif len(digits) == 7:  # e.g., 5551234
                    return f"{digits[:3]}-{digits[3:]}"

            # Default: just digits with dashes every 3-4 characters
            logger.debug(f"Phone normalized: {match.group(0)} → {digits}")
            return digits

        return phone_pattern.sub(replace_phone, text)

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        pass  # Patterns are compiled in methods for readability
```

#### Step 2: Integrate with Interview Orchestrator (1 hour)

**File**: `src/conversation_agent/core/interview.py`

Changes:
1. Import `TextNormalizer`
2. Initialize in `__init__`
3. Apply normalization in `_listen_for_response()` after transcription

```python
# In __init__:
from conversation_agent.core.text_normalizer import TextNormalizer

self.text_normalizer = TextNormalizer(
    enable_emails=True,
    enable_phones=True,
)

# In _listen_for_response(), after line 375:
user_text = result.get("text", "").strip()

# APPLY NORMALIZATION HERE
user_text = self.text_normalizer.normalize(user_text)
```

#### Step 3: Configuration Support (1 hour)

**File**: `src/conversation_agent/config/normalization_config.py`

```python
"""Configuration for text normalization."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NormalizationConfig(BaseSettings):
    """Configuration for text normalization (ITN).

    Environment Variables:
        NORMALIZATION_ENABLED: Enable/disable normalization (default: True)
        NORMALIZATION_ENABLE_EMAILS: Normalize email addresses (default: True)
        NORMALIZATION_ENABLE_PHONES: Normalize phone numbers (default: True)
        NORMALIZATION_ENABLE_DATES: Normalize dates (default: False, future)
        NORMALIZATION_ENABLE_CURRENCY: Normalize currency (default: False, future)
    """

    model_config = SettingsConfigDict(
        env_prefix="NORMALIZATION_",
        case_sensitive=False,
    )

    enabled: bool = Field(
        default=True,
        description="Enable text normalization (ITN)",
    )

    enable_emails: bool = Field(
        default=True,
        description="Normalize email addresses",
    )

    enable_phones: bool = Field(
        default=True,
        description="Normalize phone numbers",
    )

    enable_dates: bool = Field(
        default=False,
        description="Normalize dates (future feature)",
    )

    enable_currency: bool = Field(
        default=False,
        description="Normalize currency (future feature)",
    )
```

#### Step 4: Testing (2 hours)

**File**: `tests/test_text_normalizer.py`

Test categories:
- Email normalization (15 tests)
  - Basic: "john dot smith at gmail dot com"
  - Underscore: "jane underscore doe at company dot org"
  - Dash: "support dash team at example dot co dot uk"
  - Multi-level domain: "name at company dot co dot uk"
  - Edge cases: multiple emails, partial matches, no match

- Phone number normalization (15 tests)
  - 7-digit: "five five five one two three four"
  - 10-digit: "four one five five five five one two three four"
  - 11-digit: "one eight hundred five five five zero one zero one"
  - International: "plus one four one five five five five one two three four"
  - Word variations: "oh" vs "zero", "to" vs "two"
  - Edge cases: too short, too long, mixed

- Integration tests (5 tests)
  - Multiple normalizations in one text
  - Disabled features
  - Empty/None text
  - Configuration via env vars
  - Interview orchestrator integration

**Target coverage**: >90%

#### Step 5: Documentation (1 hour)

**Files to update:**
1. `docs/interview_agent_guide.md` - Add "Structured Data Recognition" section
2. `CLAUDE.md` - Update features list
3. `README.md` - Add normalization to features
4. Create `docs/text-normalization-guide.md` - Detailed guide for users

**Content:**
- What is normalization and why it's needed
- Supported data types
- Configuration options
- Examples of before/after
- Known limitations
- Troubleshooting tips

#### Step 6: CLI Support (1 hour)

**File**: `src/conversation_agent/cli/interview.py`

Add options to `start` command:
```bash
python -m conversation_agent.cli start questionnaire.pdf \
    --normalize / --no-normalize \
    --normalize-emails / --no-normalize-emails \
    --normalize-phones / --no-normalize-phones
```

Add to `config` command output:
```
Normalization Settings:
  Enabled: True
  Email normalization: True
  Phone normalization: True
```

## Files to Create/Modify

### New Files
1. `src/conversation_agent/core/text_normalizer.py` (~250 lines)
2. `src/conversation_agent/config/normalization_config.py` (~50 lines)
3. `tests/test_text_normalizer.py` (~350 lines)
4. `docs/text-normalization-guide.md` (~200 lines)

### Modified Files
1. `src/conversation_agent/core/interview.py` - Add normalizer integration (~5 lines)
2. `src/conversation_agent/config/__init__.py` - Export NormalizationConfig (~1 line)
3. `src/conversation_agent/cli/interview.py` - Add CLI options (~30 lines)
4. `docs/interview_agent_guide.md` - Add normalization section (~50 lines)
5. `CLAUDE.md` - Update features list (~5 lines)
6. `README.md` - Update features (~5 lines)

## Testing Strategy

### Unit Tests
- `TestTextNormalizer` - Test each normalization method independently
- `TestNormalizationConfig` - Test configuration loading and validation
- `TestEmailNormalization` - Comprehensive email pattern tests
- `TestPhoneNormalization` - Comprehensive phone number tests

### Integration Tests
- `TestInterviewWithNormalization` - End-to-end interview with normalization
- `TestCLINormalizationOptions` - CLI flag handling

### Manual Testing
```bash
# Test 1: Email normalization
python -m conversation_agent.cli start questionnaire.pdf
# Q: "What is your email address?"
# A: "My email is john dot smith at gmail dot com"
# Verify CSV contains: "My email is john.smith@gmail.com"

# Test 2: Phone normalization
# Q: "What is your phone number?"
# A: "My phone is five five five one two three four"
# Verify CSV contains: "My phone is 555-1234"

# Test 3: Disable normalization
NORMALIZATION_ENABLED=false python -m conversation_agent.cli start questionnaire.pdf
# Verify no normalization occurs

# Test 4: Disable only emails
NORMALIZATION_ENABLE_EMAILS=false python -m conversation_agent.cli start questionnaire.pdf
# Verify phones normalized but emails kept as-is
```

## Future Enhancements (Phase 2+)

### Phase 2: NeMo ITN Integration
- Add `nemo-text-processing` dependency
- Create `NeMoNormalizer` class
- Provider pattern: regex (default) vs NeMo (optional)
- Support dates, currency, measurements, times
- Configuration: `NORMALIZATION_PROVIDER=nemo`

### Phase 3: LLM Enhancement
- Add optional LLM post-processing for ambiguous cases
- Configuration: `NORMALIZATION_USE_LLM=true`
- Fallback to regex if LLM unavailable
- Smart context-aware corrections

### Phase 4: Custom Vocabulary
- User-provided normalization rules (JSON/YAML)
- Domain-specific patterns (medical terms, technical jargon)
- Per-question normalization hints

## Known Limitations (Phase 1)

### Emails
- ❌ Doesn't handle numbers in email: "john 123 at gmail dot com" → won't normalize
- ❌ Complex TLDs: "dot co dot uk dot something" may fail
- ✅ Basic formats work: "name at domain dot tld"

### Phone Numbers
- ❌ Spelled-out patterns: "one eight hundred flowers" → won't normalize
- ❌ Mixed format: "four one five, five five five, one two three four" → may fail
- ✅ Consistent digit words work well

### General
- ❌ Case-sensitive: "John Dot Smith" may not match (though STT usually lowercase)
- ❌ Ambiguous cases: "to" could be "2" or "to" (preposition)
- ✅ Common patterns work reliably

## Success Metrics

### Accuracy Targets
- Email normalization: >95% success rate
- Phone normalization: >90% success rate
- False positive rate: <2%

### Performance Targets
- Normalization overhead: <1ms per response
- Test coverage: >90%
- Zero regressions in existing tests

### User Experience
- Transparent to user (no extra prompts)
- CSV exports contain properly formatted data
- Configuration options available but not required

## Dependencies

### Phase 1 (Regex)
- **None** - Pure Python regex, part of standard library

### Phase 2 (NeMo) - Optional
```toml
[project.optional-dependencies]
nemo-itn = [
    "nemo-text-processing>=1.0.0",
]
```

### Phase 3 (LLM) - Optional
```toml
[project.optional-dependencies]
llm = [
    "anthropic>=0.25.0",
]
```

## Risk Assessment

### Low Risk
- Regex-based normalization is deterministic and predictable
- No external dependencies for Phase 1
- Can be disabled if issues occur
- Doesn't break existing functionality

### Medium Risk
- May incorrectly normalize edge cases (false positives)
- Mitigation: Comprehensive testing, allow disabling per feature

### High Risk
- None identified

## Rollout Plan

### Week 1
- Days 1-2: Implement core `TextNormalizer` class
- Days 3-4: Write comprehensive tests
- Day 5: Integration with orchestrator

### Week 2
- Days 1-2: Configuration support and CLI options
- Days 3-4: Documentation
- Day 5: Manual testing and bug fixes

### Release
- Include in next minor version (e.g., v0.8.0)
- Enable by default (can be disabled)
- Announce in release notes with examples

## Questions for User

1. **Priority**: Should we start with Phase 1 (regex) or go straight to Phase 2 (NeMo)?
   - Recommendation: Start with Phase 1 for quick wins, add Phase 2 later

2. **Scope**: Are dates and currency important for your use case?
   - If yes, consider going straight to NeMo ITN

3. **False Positives**: How should we handle ambiguous cases?
   - Conservative (only normalize if highly confident)
   - Aggressive (normalize when likely, may have errors)

4. **User Feedback**: Should we show users what was normalized?
   - Option 1: Silent normalization
   - Option 2: Log normalization in metadata
   - Option 3: Ask user to confirm normalized values

## References

- [NVIDIA NeMo ITN Paper](https://arxiv.org/abs/2104.05055)
- [Apple ITN Research](https://machinelearning.apple.com/research/inverse-text-normal)
- [AssemblyAI Universal-2-TF](https://www.assemblyai.com/research/universal-2)
- [Azure Display Text Formatting](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/display-text-format)
