import itertools
import logging
import os
import sys

from db_repository import PromptRepository

from scripts.data.default_system_prompts import (
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_CODE_REVIEWER,
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_SUMMARY_ANALYST,
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TEACHER,
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TECH_ANALYST,
    DEFAULT_SYSTEM_PROMPTS_CHAT_ANY_ANY,
    DEFAULT_SYSTEM_PROMPTS_CLARIFICATION_ANY_ANY,
)
from scripts.data.default_user_prompts import (
    DEFAULT_USER_PROMPTS_ANALYSIS_CODE_REVIEWER,
    DEFAULT_USER_PROMPTS_ANALYSIS_SUMMARY_ANALYST,
    DEFAULT_USER_PROMPTS_ANALYSIS_TEACHER,
    DEFAULT_USER_PROMPTS_ANALYSIS_TECH_ANALYST,
    DEFAULT_USER_PROMPTS_CHAT_ANY_ANY,
    DEFAULT_USER_PROMPTS_CLARIFICATION_ANY_ANY,
)

logger = logging.getLogger(__name__)

DEFAULT_PROMPTS = list(
    itertools.chain(
        DEFAULT_SYSTEM_PROMPTS_ANALYSIS_SUMMARY_ANALYST,
        DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TECH_ANALYST,
        DEFAULT_SYSTEM_PROMPTS_ANALYSIS_CODE_REVIEWER,
        DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TEACHER,
        DEFAULT_SYSTEM_PROMPTS_CLARIFICATION_ANY_ANY,
        DEFAULT_SYSTEM_PROMPTS_CHAT_ANY_ANY,
        DEFAULT_USER_PROMPTS_ANALYSIS_SUMMARY_ANALYST,
        DEFAULT_USER_PROMPTS_ANALYSIS_TECH_ANALYST,
        DEFAULT_USER_PROMPTS_ANALYSIS_CODE_REVIEWER,
        DEFAULT_USER_PROMPTS_ANALYSIS_TEACHER,
        DEFAULT_USER_PROMPTS_CLARIFICATION_ANY_ANY,
        DEFAULT_USER_PROMPTS_CHAT_ANY_ANY,
    )
)


def main():
    logging.info("Starting prompts database initialization...")

    db_url = os.getenv("DB_URL")
    if not db_url:
        logging.error("DB_URL environment variable is not set")
        sys.exit(1)

    safe_db_url = db_url.replace("://", "://***@")
    logging.info(f"Database connection: {safe_db_url}")

    try:
        logging.info("Connecting to database...")
        repository = PromptRepository(db_url)
        logging.info("Database connection established")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        sys.exit(1)

    try:
        logging.info(f"Seeding {len(DEFAULT_PROMPTS)} prompts...")
        repository.seed_prompts(DEFAULT_PROMPTS)
        logging.info(f"{len(DEFAULT_PROMPTS)} prompts are seeded in database")
    except Exception as e:
        logging.error(f"Prompts seeding error: {e}")
        sys.exit(1)

    logging.info("Prompts database initialization successful")


if __name__ == "__main__":
    main()
