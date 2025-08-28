"""Data storage and loading for bitstream captures."""

import csv
import json
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class CaptureMetadata:
    """Metadata for a capture session."""

    timestamp: str
    device_info: dict[str, Any]
    window_size: int
    sensitivity: float
    total_bytes: int
    total_anomalies: int
    duration_seconds: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CaptureMetadata":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class BitstreamRecord:
    """Single record in the bitstream."""

    position: int
    timestamp: float
    byte_value: int
    anomaly_type: str | None = None
    z_score: float | None = None
    p_value: float | None = None
    significance: str | None = None


class BitstreamWriter:
    """Write bitstream data to file."""

    def __init__(self, filepath: Path, metadata: CaptureMetadata):
        """Initialize writer.

        Args:
            filepath: Path to output file
            metadata: Capture metadata
        """
        self.filepath = filepath
        self.metadata = metadata
        self.csv_file = None
        self.csv_writer = None
        self.records_written = 0

    def __enter__(self) -> "BitstreamWriter":
        """Context manager entry."""
        self.csv_file = open(self.filepath, "w", newline="")

        # Write metadata as JSON comment in first line
        metadata_json = json.dumps(asdict(self.metadata))
        self.csv_file.write(f"# {metadata_json}\n")

        # CSV writer for data
        self.csv_writer = csv.DictWriter(
            self.csv_file,
            fieldnames=[
                "position",
                "timestamp",
                "byte_value",
                "anomaly_type",
                "z_score",
                "p_value",
                "significance",
            ],
        )
        self.csv_writer.writeheader()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if self.csv_file:
            self.csv_file.close()

    def write_record(self, record: BitstreamRecord) -> None:
        """Write a single record."""
        if not self.csv_writer:
            raise RuntimeError("Writer not initialized")

        self.csv_writer.writerow(asdict(record))
        self.records_written += 1

        # Flush periodically for live viewing
        if self.records_written % 1000 == 0:
            self.csv_file.flush()


class BitstreamReader:
    """Read bitstream data from file."""

    def __init__(self, filepath: Path):
        """Initialize reader.

        Args:
            filepath: Path to input file
        """
        self.filepath = filepath
        self.metadata: CaptureMetadata | None = None

    def load_metadata(self) -> CaptureMetadata:
        """Load metadata from file.

        Returns:
            Capture metadata
        """
        with open(self.filepath) as f:
            first_line = f.readline().strip()

        if not first_line.startswith("# "):
            raise ValueError("File does not contain metadata header")

        metadata_json = first_line[2:]  # Remove '# ' prefix
        metadata_dict = json.loads(metadata_json)
        self.metadata = CaptureMetadata.from_dict(metadata_dict)

        return self.metadata

    def iter_records(self) -> Iterator[BitstreamRecord]:
        """Iterate over all records in file.

        Yields:
            BitstreamRecord objects
        """
        with open(self.filepath) as f:
            # Skip metadata line
            f.readline()

            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                # Convert numeric fields
                position = int(row["position"])
                timestamp = float(row["timestamp"])
                byte_value = int(row["byte_value"])

                # Handle optional fields
                anomaly_type = row["anomaly_type"] if row["anomaly_type"] else None
                z_score = float(row["z_score"]) if row["z_score"] else None
                p_value = float(row["p_value"]) if row["p_value"] else None
                significance = row["significance"] if row["significance"] else None

                yield BitstreamRecord(
                    position=position,
                    timestamp=timestamp,
                    byte_value=byte_value,
                    anomaly_type=anomaly_type,
                    z_score=z_score,
                    p_value=p_value,
                    significance=significance,
                )

    def load_all_records(self) -> list[BitstreamRecord]:
        """Load all records into memory.

        Returns:
            List of all records
        """
        return list(self.iter_records())

    def get_records_range(self, start: int, end: int) -> list[BitstreamRecord]:
        """Get records within a position range.

        Args:
            start: Start position (inclusive)
            end: End position (exclusive)

        Returns:
            List of records in range
        """
        records = []
        for record in self.iter_records():
            if start <= record.position < end:
                records.append(record)
            elif record.position >= end:
                break

        return records

    def get_anomalies(self) -> list[BitstreamRecord]:
        """Get only records with anomalies.

        Returns:
            List of anomaly records
        """
        return [record for record in self.iter_records() if record.anomaly_type]

    def get_file_stats(self) -> dict[str, Any]:
        """Get statistics about the file.

        Returns:
            Dictionary with file statistics
        """
        if not self.metadata:
            self.load_metadata()

        total_records = 0
        anomaly_count = 0

        for record in self.iter_records():
            total_records += 1
            if record.anomaly_type:
                anomaly_count += 1

        return {
            "filepath": str(self.filepath),
            "total_records": total_records,
            "anomaly_count": anomaly_count,
            "anomaly_rate": anomaly_count / total_records if total_records > 0 else 0,
            "metadata": asdict(self.metadata) if self.metadata else None,
        }


def create_capture_metadata(
    device_info: dict[str, Any], window_size: int, sensitivity: float
) -> CaptureMetadata:
    """Create metadata for a new capture session.

    Args:
        device_info: Information about the device
        window_size: Analysis window size
        sensitivity: Statistical sensitivity threshold

    Returns:
        CaptureMetadata object
    """
    return CaptureMetadata(
        timestamp=datetime.now().isoformat(),
        device_info=device_info,
        window_size=window_size,
        sensitivity=sensitivity,
        total_bytes=0,
        total_anomalies=0,
        duration_seconds=0.0,
    )
