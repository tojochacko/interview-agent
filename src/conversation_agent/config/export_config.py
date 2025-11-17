"""Configuration for CSV export functionality."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExportConfig(BaseSettings):
    """Configuration for interview transcript export.

    Attributes:
        output_directory: Directory where transcripts will be saved
        filename_format: Format string for output filenames
        include_metadata: Include additional metadata in CSV
        csv_encoding: Character encoding for CSV files
    """

    output_directory: Path = Field(
        default=Path("./interview_transcripts"),
        description="Directory for saving transcripts",
    )
    filename_format: str = Field(
        default="interview_{timestamp}.csv",
        description="Format for CSV filenames",
    )
    include_metadata: bool = Field(
        default=True, description="Include metadata columns in CSV"
    )
    csv_encoding: str = Field(
        default="utf-8", description="Character encoding for CSV files"
    )

    model_config = SettingsConfigDict(
        env_prefix="EXPORT_", env_file=".env", extra="ignore"
    )
