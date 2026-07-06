import asyncio
import logging
from typing import Callable, Awaitable

from agent_enums import Assignment, Role
from db_repository import PromptRepository
from rag_client import ChromaDBClientFactory

from agent.agent import Agent
from agent.council.corrector import correct_result
from agent.council.judge import judge_result
from agent.models.council_analysis_data import CouncilAnalysisData
from agent.runners.council_agents_runner import run_agent, run_stage
from api.models.analisys.agent_data import AgentData
from config.llm_config import llm_config
from llm.tokens.token_usage import TokenUsage, create_token_usage

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, dict], Awaitable[None]]


class Council:
    def __init__(self):
        self.agents = []
        self.correctors = []
        self.judges = []
        self.post_correctors = []

        self._token_usage: TokenUsage = create_token_usage()

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

        self._token_usage = create_token_usage()

        for agent_index, agent_data in enumerate(agents_data, start=1):
            agent = await Agent.create_agent(
                llm_config,
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
            f"Council of {len(self.agents)} agents: doc analysis is starting..."
        )
        if limit:
            logger.info(f"Tokens limit: {limit}")
        else:
            logger.info(f"Tokens limit is not set")

        results = list(
            await asyncio.gather(
                *[run_agent(
                    agent=agent,
                    role=role,
                    resources=resources,
                    progress_callback=progress_callback,
                ) for agent in self.agents],
            )
        )
        logger.info(f"Council of {len(self.agents)} agents: doc analysis is completed")

        answer_seqs = []
        judgements = []

        exec_token_usage = create_token_usage()
        total_elapsed = 0

        for r in results:
            answer_seqs.append(r.answer_seq)
            exec_token_usage.add_usage(r.token_usage)
            total_elapsed += r.elapsed

        self._token_usage.add_usage(exec_token_usage)
        logger.info(f"Exec token usage: {self._token_usage}")

        if self.correctors:
            correctors_result, total_elapsed = await run_stage(
                stage_name=f"{len(self.correctors)} correctors: correction",
                stage_fn=lambda: correct_result(
                    correctors=self.correctors,
                    answer_seqs=answer_seqs,
                    role=role,
                    progress_callback=progress_callback,
                ),
                council_token_usage=self._token_usage,
                total_elapsed=total_elapsed,
            )

            answer_seqs = correctors_result.answer_seqs

        if self.judges:
            judges_result, total_elapsed = await run_stage(
                stage_name=f"{len(self.correctors)} judges: judgement",
                stage_fn=lambda: judge_result(
                    judges=self.judges,
                    answer_seqs=answer_seqs,
                    role=role,
                    progress_callback=progress_callback,
                ),
                council_token_usage=self._token_usage,
                total_elapsed=total_elapsed,
            )

            judgements = judges_result.judgements
            scores = judges_result.scores
        else:
            scores = [None] * len(answer_seqs)

        return CouncilAnalysisData(
            answer_seqs=answer_seqs,
            judgements=judgements,
            scores=scores,
            token_usage=self._token_usage,
            elapsed=total_elapsed,
        )
