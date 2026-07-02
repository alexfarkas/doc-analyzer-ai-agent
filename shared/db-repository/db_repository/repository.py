import logging
import os
from contextlib import contextmanager
from pathlib import Path

from agent_enums import Mode, Role, Assignment, PromptType
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    func,
    Index,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from db_repository.prompt_model import PromptModel

logger = logging.getLogger(__name__)

Base = declarative_base()


class PromptDB(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String(20), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)
    assignment = Column(String(20), nullable=False, index=True)
    prompt_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=True, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "idx_prompts_lookup",
            "mode",
            "role",
            "assignment",
            "prompt_type",
            "is_active",
        ),
    )


class PromptRepository:
    def __init__(self, db_url):
        logger.info("Initializing SQL database client...")

        self.is_sqlite = db_url.startswith("sqlite")

        if self.is_sqlite:
            logger.info("Using local SQL database")
            db_path = db_url.replace("sqlite:///", "").replace("sqlite:////", "")
            Path(db_path).mkdir(parents=True, exist_ok=True)
            engine_kwargs = {}
        else:
            logger.info("Using SQL database service")
            engine_kwargs = {
                "pool_pre_ping": True,
                "pool_size": 3600,
            }

        self.engine = create_engine(
            db_url,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            **engine_kwargs,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Session:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_prompt(
        self, mode: Mode, role: Role, assignment: Assignment, prompt_type: PromptType
    ) -> PromptModel | None:
        logger.info(
            f"Getting {prompt_type.value} prompt from SQL database: mode={mode.value}, "
            f"role={role.value}, assignment={assignment.value}..."
        )
        with self.get_session() as session:
            db_prompt = (
                session.query(PromptDB)
                .filter(
                    PromptDB.mode == mode.value,
                    PromptDB.role == role.value,
                    PromptDB.assignment == assignment.value,
                    PromptDB.prompt_type == prompt_type.value,
                    PromptDB.is_active,
                )
                .first()
            )

            if not db_prompt:
                logger.error("Prompt not found in SQL database")
                return None

            logger.info("Prompt found in SQL database successfully")
            return PromptModel(
                mode=Mode(db_prompt.mode),
                role=Role(db_prompt.role),
                assignment=Assignment(db_prompt.assignment),
                prompt_type=PromptType(db_prompt.prompt_type),
                content=db_prompt.content,
            )

    def get_prompt_with_format(
        self,
        mode: Mode,
        role: Role,
        assignment: Assignment,
        prompt_type: PromptType,
        **kwargs,
    ):
        logger.info(
            f"Getting {prompt_type} prompt from SQL database: mode={mode.value}, "
            f"role={role.value}, assignment={assignment.value} and injecting placeholders..."
        )
        prompt = self.get_prompt(mode, role, assignment, prompt_type)
        if not prompt:
            logger.error(
                "Prompt not found in SQL database, nowhere to inject placeholders"
            )
            return None

        placeholders = [
            "resources",
            "init_system_prompt",
            "init_user_prompt",
            "ai_answer",
            "history",
        ]
        for placeholder in placeholders:
            value = kwargs.get(placeholder, None)
            if value and placeholder in prompt.content:
                return prompt.content.format(placeholder=value)

        logger.info("Prompt is found in SQL database successfully")
        return prompt.content

    def upsert_prompt(self, prompt: PromptModel) -> int:
        logger.info(
            f"Writing {prompt.prompt_type.value} prompt into SQL database: mode={prompt.mode.value}, "
            f"role={prompt.role.value}, assignment={prompt.assignment.value}..."
        )
        with self.get_session() as session:
            existing = (
                session.query(PromptDB)
                .filter(
                    PromptDB.mode == prompt.mode.value,
                    PromptDB.role == prompt.role.value,
                    PromptDB.assignment == prompt.assignment.value,
                    PromptDB.prompt_type == prompt.prompt_type.value,
                )
                .first()
            )

            if existing:
                logger.info("Prompt already exists in SQL database")
                existing.content = prompt.content
                existing.is_active = True
                session.add(existing)
                return existing.id
            else:
                db_prompt = PromptDB(
                    mode=prompt.mode.value,
                    role=prompt.role.value,
                    assignment=prompt.assignment.value,
                    prompt_type=prompt.prompt_type.value,
                    content=prompt.content,
                    is_active=True,
                )
                session.add(db_prompt)
                session.flush()
                logger.info("Prompt is written into SQL database")
                return db_prompt.id

    def seed_prompts(self, prompts_data: list[dict]):
        logger.info(f"Seeding {len(prompts_data)} prompts into SQL database...")
        for data in prompts_data:
            prompt = PromptModel(**data)
            if not self.get_prompt(
                mode=prompt.mode,
                role=prompt.role,
                assignment=prompt.assignment,
                prompt_type=prompt.prompt_type,
            ):
                self.upsert_prompt(prompt)
        logger.info(f"{len(prompts_data)} prompts are seeded into SQL database")

    def deactivate_prompt(
        self, mode: Mode, role: Role, assignment: Assignment, prompt_type: PromptType
    ) -> bool:
        logger.info(
            f"Deactivating {prompt_type.value} prompt in SQL database: mode={mode.value}, "
            f"role={role.value}, assignment={assignment.value}..."
        )
        with self.get_session() as session:
            db_prompt = (
                session.query(PromptDB)
                .filter(
                    PromptDB.mode == mode.value,
                    PromptDB.role == role.value,
                    PromptDB.assignment == assignment.value,
                    PromptDB.prompt_type == prompt_type.value,
                )
                .first()
            )

            if db_prompt:
                db_prompt.is_active = False
                logger.info("Prompt deactivated in SQL database")
                return True

            logger.error("Deactivating prompt is not found in SQL database")
            return False
