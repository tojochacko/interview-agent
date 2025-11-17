# Phase 5: CSV Export & Data Persistence

## Overview

Phase 5 implements the CSV export functionality to save interview transcripts in a structured format. This allows users to persist conversation data for analysis, record-keeping, and reporting.

## Implementation Status

✅ **COMPLETE** - All Phase 5 requirements implemented and tested.

## Components Implemented

### 1. Export Configuration (`config/export_config.py`)

**Purpose**: Configuration management for CSV export settings

**Features**:
- Configurable output directory
- Customizable filename format with template variables (`{timestamp}`, `{session_id}`)
- Toggle for metadata inclusion
- Configurable CSV encoding (default: UTF-8)
- Environment variable support via Pydantic Settings

**Configuration Example**:
```python
from conversation_agent.config import ExportConfig

config = ExportConfig(
    output_directory=Path("./transcripts"),
    filename_format="interview_{timestamp}.csv",
    include_metadata=True,
    csv_encoding="utf-8"
)
```

### 2. CSV Exporter (`core/csv_exporter.py`)

**Purpose**: Core CSV export functionality

**Key Methods**:
- `export_session(session, output_path)`: Export interview session to CSV
- `_generate_output_path(session)`: Generate filename based on config
- `_get_header()`: Generate CSV header row
- `_turn_to_row(turn, session)`: Convert conversation turn to CSV row

**Features**:
- Automatic directory creation
- Configurable metadata columns
- UTF-8 encoding support for internationalization
- Empty session handling
- Custom output path support

**CSV Schema**:

**With Metadata** (default):
- `question_number`: Sequential question number (1-indexed)
- `question_id`: Unique question UUID
- `question_text`: The question text
- `response_text`: Transcribed user response
- `timestamp`: Response timestamp (ISO 8601 format)
- `confidence`: Transcription confidence score (0.0-1.0)
- `retry_count`: Number of retry attempts
- `clarification_requested`: Boolean flag
- `skipped`: Whether question was skipped
- `duration_seconds`: Time taken for the turn

**Without Metadata**:
- `question_number`
- `question_id`
- `question_text`
- `response_text`
- `timestamp`

### 3. Convenience Function

```python
from conversation_agent.core import export_interview

# Simple export
output_path = export_interview(session)

# With custom config
config = ExportConfig(output_directory=Path("./exports"))
output_path = export_interview(session, config=config)

# With custom path
output_path = export_interview(session, output_path=Path("./custom.csv"))
```

## Test Coverage

**Total Tests**: 16 comprehensive tests

**Test Classes**:
1. `TestExportConfig`: Configuration validation
2. `TestCSVExporter`: Core exporter functionality
3. `TestExportInterview`: Convenience function tests

**Coverage**: 100% for all Phase 5 modules

**Test Scenarios**:
- Default and custom configuration
- Basic session export
- Custom output paths
- Directory creation
- CSV content with/without metadata
- Filename generation (timestamp and session ID)
- UTF-8 encoding with Unicode characters
- Empty session handling
- Skipped questions
- Clarification requests and retries

## File Structure

```
src/conversation_agent/
├── config/
│   ├── __init__.py           (updated with ExportConfig)
│   └── export_config.py      (NEW - 38 lines)
└── core/
    ├── __init__.py           (updated with CSVExporter)
    └── csv_exporter.py       (NEW - 166 lines)

tests/
└── test_csv_exporter.py      (NEW - 328 lines)

examples/
└── demo_csv_export.py        (NEW - demo script)
```

## Usage Example

```python
from conversation_agent.models import InterviewSession
from conversation_agent.core import export_interview
from conversation_agent.config import ExportConfig

# Create or load session
session = InterviewSession(questionnaire_path="questionnaire.pdf")
# ... conduct interview ...
session.mark_completed()

# Export with default settings
output_path = export_interview(session)
print(f"Exported to: {output_path}")

# Export with custom settings
config = ExportConfig(
    output_directory=Path("./my_transcripts"),
    include_metadata=False
)
output_path = export_interview(session, config=config)
```

## Demo Script

Run the demo to see CSV export in action:

```bash
python examples/demo_csv_export.py
```

This creates sample CSV files in `./demo_exports/`:
1. `interview_{timestamp}.csv` - with metadata
2. `interview_no_metadata_{timestamp}.csv` - without metadata
3. `custom_interview.csv` - custom filename

## Integration with Other Phases

**Integrates with**:
- Phase 1: Uses `Question` and `Response` models
- Phase 4: Uses `InterviewSession` and `ConversationTurn` from orchestrator
- Phase 6: Will be called by CLI to save transcripts after interviews

**Used by**:
- Phase 6 (CLI): Will automatically export after interview completion
- Phase 7 (Polish): May add additional export formats

## Code Quality

✅ All files under line limits:
- `export_config.py`: 38 lines (limit: 500)
- `csv_exporter.py`: 166 lines (limit: 500)
- `test_csv_exporter.py`: 328 lines (limit: 500)

✅ Functions under 50 lines
✅ Classes under 100 lines
✅ All Ruff checks pass
✅ 100% test coverage for Phase 5 modules
✅ Overall project coverage: 78%

## Environment Variables

Export settings can be configured via environment variables:

```bash
export EXPORT_OUTPUT_DIRECTORY="./my_transcripts"
export EXPORT_FILENAME_FORMAT="session_{session_id}.csv"
export EXPORT_INCLUDE_METADATA="false"
export EXPORT_CSV_ENCODING="utf-8"
```

## Error Handling

- **OSError**: Raised if file cannot be written (permissions, disk full)
- **Directory Creation**: Automatically creates output directory if missing
- **Empty Sessions**: Gracefully handles sessions with no turns
- **Skipped Questions**: Properly records skipped questions with empty responses

## Next Steps (Phase 6)

Phase 6 will integrate CSV export into the CLI:
1. Auto-export after interview completion
2. Manual export command: `interview export <session_id>`
3. List previous sessions: `interview list`
4. Re-export with different settings

## Dependencies

No new dependencies added. Uses standard library:
- `csv`: CSV file I/O
- `pathlib`: Path handling
- `datetime`: Timestamp formatting (already in use)

## Notes

- CSV files use UTF-8 encoding by default for international character support
- Timestamps use ISO 8601 format for consistency and parseability
- Question IDs are UUIDs for uniqueness and traceability
- Skipped questions appear in CSV with empty response fields
- Metadata can be toggled off for simpler CSV format
