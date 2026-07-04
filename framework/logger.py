import logging
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
output_dir = os.environ.get("TEST_UNDECLARED_OUTPUTS_DIR")
if output_dir is None:
    output_dir = PROJECT_ROOT / "output"

output_dir = Path(output_dir)
Path(output_dir).mkdir(parents=True, exist_ok=True)
log_file = output_dir / "test.log"


class PhaseFormatter(logging.Formatter):
    """Custom formatter that includes test phase information"""
    def format(self, record):
        phase = getattr(record, 'phase', 'Test')
        asctime = self.formatTime(record, self.datefmt)
        return f"{asctime} {phase} {record.levelname} {record.getMessage()}"


logger = logging.getLogger("Framework")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = PhaseFormatter(datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    