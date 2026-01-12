"""Job lifecycle management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .job_id import generate_job_id
from .models import Job, JobConfig, JobEvent, JobStatus


class JobManager:
    """Manages job lifecycle and persistence."""

    def __init__(self, jobs_dir: Optional[Path] = None):
        """Initialize the job manager.

        Args:
            jobs_dir: Directory to store job manifests. If None, jobs are only in-memory.
        """
        self.jobs_dir = jobs_dir
        self._jobs: dict[str, Job] = {}

        if jobs_dir:
            jobs_dir.mkdir(parents=True, exist_ok=True)

    def create_job(
        self,
        description: str,
        config: JobConfig,
        job_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Job:
        """Create a new job.

        Args:
            description: User's description of the simulation request
            config: Job configuration
            job_id: Optional custom job ID (auto-generated if not provided)
            notes: Optional additional notes

        Returns:
            The created Job instance
        """
        if job_id is None:
            job_id = generate_job_id()

        now = datetime.utcnow()
        job = Job(
            job_id=job_id,
            created_at=now,
            status=JobStatus.PENDING,
            description=description,
            config=config,
            notes=notes,
        )

        # Record creation event
        event = JobEvent(
            job_id=job_id,
            event_type="created",
            timestamp=now,
            details={"config": config.to_dict()},
        )
        job.events.append(event)

        self._jobs[job_id] = job
        self._save_job(job)

        return job

    def start_job(self, job_id: str) -> None:
        """Mark a job as started.

        Args:
            job_id: The job ID to start

        Raises:
            KeyError: If job not found
        """
        job = self.get_job(job_id)
        if job is None:
            raise KeyError(f"Job not found: {job_id}")

        job.status = JobStatus.RUNNING
        event = JobEvent(
            job_id=job_id,
            event_type="started",
            timestamp=datetime.utcnow(),
        )
        job.events.append(event)
        self._save_job(job)

    def record_progress(
        self,
        job_id: str,
        run_id: str,
        metrics: Optional[dict] = None,
        modal_call_id: Optional[str] = None,
    ) -> None:
        """Record progress on a job (a run completed).

        Args:
            job_id: The job ID
            run_id: The completed run ID
            metrics: Optional metrics from the run
            modal_call_id: Optional Modal function call ID for debugging

        Raises:
            KeyError: If job not found
        """
        job = self.get_job(job_id)
        if job is None:
            raise KeyError(f"Job not found: {job_id}")

        job.run_ids.append(run_id)
        if modal_call_id:
            job.modal_call_ids[run_id] = modal_call_id
        event = JobEvent(
            job_id=job_id,
            event_type="progress",
            timestamp=datetime.utcnow(),
            details={"run_id": run_id, "metrics": metrics or {}, "modal_call_id": modal_call_id},
        )
        job.events.append(event)
        self._save_job(job)

    def complete_job(self, job_id: str, summary: Optional[dict] = None) -> None:
        """Mark a job as completed.

        Args:
            job_id: The job ID
            summary: Optional summary statistics

        Raises:
            KeyError: If job not found
        """
        job = self.get_job(job_id)
        if job is None:
            raise KeyError(f"Job not found: {job_id}")

        now = datetime.utcnow()
        job.status = JobStatus.COMPLETED
        job.completed_at = now

        event = JobEvent(
            job_id=job_id,
            event_type="completed",
            timestamp=now,
            details={"summary": summary or {}},
        )
        job.events.append(event)
        self._save_job(job)

    def fail_job(self, job_id: str, error: str) -> None:
        """Mark a job as failed.

        Args:
            job_id: The job ID
            error: Error message

        Raises:
            KeyError: If job not found
        """
        job = self.get_job(job_id)
        if job is None:
            raise KeyError(f"Job not found: {job_id}")

        now = datetime.utcnow()
        job.status = JobStatus.FAILED
        job.completed_at = now
        job.error = error

        event = JobEvent(
            job_id=job_id,
            event_type="failed",
            timestamp=now,
            details={"error": error},
        )
        job.events.append(event)
        self._save_job(job)

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID.

        Args:
            job_id: The job ID

        Returns:
            The Job instance or None if not found
        """
        # Check in-memory cache first
        if job_id in self._jobs:
            return self._jobs[job_id]

        # Try to load from disk
        if self.jobs_dir:
            manifest_path = self.jobs_dir / job_id / "job_manifest.json"
            if manifest_path.exists():
                job = self._load_job(manifest_path)
                self._jobs[job_id] = job
                return job

        return None

    def list_jobs(self) -> list[Job]:
        """List all known jobs.

        Returns:
            List of Job instances
        """
        # Load any jobs from disk that aren't in memory
        if self.jobs_dir and self.jobs_dir.exists():
            for job_dir in self.jobs_dir.iterdir():
                if job_dir.is_dir():
                    job_id = job_dir.name
                    if job_id not in self._jobs:
                        manifest_path = job_dir / "job_manifest.json"
                        if manifest_path.exists():
                            job = self._load_job(manifest_path)
                            self._jobs[job_id] = job

        return list(self._jobs.values())

    def _save_job(self, job: Job) -> None:
        """Save job manifest to disk.

        Args:
            job: The job to save
        """
        if self.jobs_dir is None:
            return

        job_dir = self.jobs_dir / job.job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = job_dir / "job_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(job.to_dict(), f, indent=2)

    def _load_job(self, manifest_path: Path) -> Job:
        """Load a job from a manifest file.

        Args:
            manifest_path: Path to job_manifest.json

        Returns:
            The loaded Job instance
        """
        with open(manifest_path) as f:
            data = json.load(f)
        return Job.from_dict(data)
