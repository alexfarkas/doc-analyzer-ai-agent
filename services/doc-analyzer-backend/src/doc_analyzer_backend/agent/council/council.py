import logging
from typing import Callable, Awaitable

from agent_enums import Assignment, Role
from db_repository import PromptRepository
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.stages.corrector_stage import (
    run_corrector_stage,
)
from src.doc_analyzer_backend.agent.council.stages.exec_stage import run_exec_stage
from src.doc_analyzer_backend.agent.council.stages.judge_stage import run_judge_stage
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import (
    create_consumption_data,
)
from src.doc_analyzer_backend.agent.models.analysis.council_analysis_data import (
    CouncilAnalysisData,
)
from src.doc_analyzer_backend.api.models.analisys.agent_data import AgentData
from src.doc_analyzer_backend.config.loader.settings import app_settings

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, dict], Awaitable[None]]


class Council:
    def __init__(self):
        self.agents = []
        self.correctors = []
        self.judges = []
        self.post_correctors = []

        self._prompt_repository: PromptRepository | None = None
        self._chromadb_client_factory: ChromaDBClientFactory | None = None

    @classmethod
    async def init_council(
        cls,
        prompt_repository: PromptRepository | None = None,
        chromadb_client_factory: ChromaDBClientFactory | None = None,
    ) -> Council:
        instance = cls()
        await instance._initialize(prompt_repository, chromadb_client_factory)
        return instance

    async def _initialize(
        self,
        prompt_repository: PromptRepository | None = None,
        chromadb_client_factory: ChromaDBClientFactory | None = None,
    ) -> None:
        self._prompt_repository = prompt_repository
        self._chromadb_client_factory = chromadb_client_factory

    async def create_council(self, agents_data: list[AgentData]) -> None:
        self.agents = []
        self.correctors = []
        self.judges = []
        self.post_correctors = []

        for agent_index, agent_data in enumerate(agents_data, start=1):
            agent = await Agent.create_agent(
                app_settings().llm,
                agent_index,
                self._prompt_repository,
                self._chromadb_client_factory,
            )
            await agent.setup_model(agent_data.model)
            match agent_data.assignment:
                case Assignment.EXEC:
                    self.agents.append(agent)
                case Assignment.CORRECTOR:
                    self.correctors.append(agent)
                case Assignment.JUDGE:
                    self.judges.append(agent)
                case Assignment.POST_CORRECTOR:
                    self.post_correctors.append(agent)

        logger.info(
            f"Council created, "
            f"agents: {len(self.agents)}, correctors: {len(self.correctors)}, judges: {len(self.judges)}"
        )

    async def analyze_doc(
        self,
        resources: list[str],
        role: Role,
        limit: int | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> CouncilAnalysisData:
        logger.info(
            f"Council of "
            f"agents: {len(self.agents)}, correctors: {len(self.correctors)}, judges: {len(self.judges)} "
            "doc analysis is starting..."
        )

        if limit:
            logger.info(f"Tokens limit: {limit}")
        else:
            logger.info("Tokens limit is not set")

        council_consumption_data = create_consumption_data()

        answer_seqs, exec_consumption_data = await run_exec_stage(
            agents=self.agents,
            resources=resources,
            role=role,
            progress_callback=progress_callback,
        )

        logger.info(
            f"Updating consumption data by EXEC total data: {exec_consumption_data}"
        )
        council_consumption_data.update_by_data(data=exec_consumption_data)

        if self.correctors:
            answer_seqs, corrector_consumption_data = await run_corrector_stage(
                correctors=self.correctors,
                answer_seqs=answer_seqs,
                role=role,
                progress_callback=progress_callback,
            )

            logger.info(
                f"Updating consumption data by CORRECTORS total data: {corrector_consumption_data}"
            )
            council_consumption_data.update_by_data(data=corrector_consumption_data)

            logger.info(
                f"Current council token usage: {council_consumption_data.token_usage}"
            )
            logger.info(f"Current council cost: {council_consumption_data.cost}")

        judgements = []
        scores = [None] * len(answer_seqs)

        if self.judges:
            judges_result, judge_consumption_data = await run_judge_stage(
                judges=self.judges,
                answer_seqs=answer_seqs,
                role=role,
                progress_callback=progress_callback,
            )

            logger.info(
                f"Updating consumption data by JUDGES total data: {judge_consumption_data}"
            )
            council_consumption_data.update_by_data(data=judge_consumption_data)

            logger.info(
                f"Current council token usage: {council_consumption_data.token_usage}"
            )
            logger.info(f"Current council cost: {council_consumption_data.cost}")

            judgements = judges_result.judgements
            scores = judges_result.scores

        logger.info(
            f"Council of "
            f"agents: {len(self.agents)}, correctors: {len(self.correctors)}, judges: {len(self.judges)} "
            "doc analysis is completed"
        )

        return CouncilAnalysisData(
            answer_seqs=answer_seqs,
            judgements=judgements,
            scores=scores,
            consumption_data=council_consumption_data,
        )
