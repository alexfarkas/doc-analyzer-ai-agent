import asyncio
import logging
from typing import Callable, Awaitable

from agent_enums import Assignment, Role
from db_repository import PromptRepository
from rag_client import ChromaDBClientFactory

from agent.agent import Agent
from agent.council.corrector import correct_result
from agent.council.judge import judge_result
from api.models.analisys.agent_data import AgentData
from config.llm_config import llm_config
from llm.token_usage import TokenUsage, create_token_usage

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
            agent = await Agent().create_agent(
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
    ) -> dict:
        logger.info(
            f"Council of {len(self.agents)} agents: doc analysis is starting..."
        )
        if limit:
            logger.info(f"Tokens limit: {limit}")
        else:
            logger.info(f"Tokens limit is not set")

        async def run_agents(agent: Agent) -> dict:
            if progress_callback:
                await progress_callback(
                    "agent_start",
                    {
                        "agentId": agent.agent_id,
                        "agentType": "exec",
                    },
                )
            logger.info(f"Agent {agent.agent_id} (exec): doc analysis is starting...")
            try:
                return await agent.analyze_doc(resources=resources, role=role)
            finally:
                logger.info(f"Agent {agent.agent_id} (exec): doc analysis is completed")
                if progress_callback:
                    await progress_callback(
                        "agent_end",
                        {
                            "agentId": agent.agent_id,
                            "agentType": "exec",
                        },
                    )

        results = list(
            await asyncio.gather(
                *[run_agents(agent) for agent in self.agents],
            )
        )
        logger.info(f"Council of {len(self.agents)} agents: doc analysis is completed")

        answers = []
        iterations = []
        judgements = []
        scores = []

        exec_token_usage = create_token_usage()
        total_elapsed = 0

        for r in results:
            answer = r["answer"]
            token_usage = r["token_usage"]
            elapsed = r["elapsed"]

            answers.append(answer)

            exec_token_usage.add_usage(token_usage)
            total_elapsed += elapsed

        self._token_usage.add_usage(exec_token_usage)
        logger.info(f"Exec token usage: {self._token_usage}")

        if len(self.correctors) > 0:
            logger.info(f"{len(self.correctors)} correctors: correction is starting...")
            correctors_result = await correct_result(
                correctors=self.correctors,
                answers=answers,
                role=role,
                progress_callback=progress_callback,
            )
            logger.info(f"{len(self.correctors)} correctors:: correction is completed")

            answers = correctors_result["answers"]
            iterations = correctors_result["iterations"]

            correctors_token_usage = correctors_result["correctors_token_usage"]
            self._token_usage.add_usage(correctors_token_usage)
            logger.info(f"Correctors token usage: {correctors_token_usage}")
            logger.info(f"Overall token usage: {self._token_usage}")

            total_elapsed += correctors_result["correctors_elapsed"]

        if len(self.judges) == 0:
            [scores.append(None) for _ in answers]
        else:
            logger.info(f"{len(self.judges)} judges: judgement is starting...")
            judges_result = await judge_result(
                judges=self.judges,
                answers=answers,
                role=role,
                progress_callback=progress_callback,
            )
            logger.info(f"{len(self.judges)} judges:: judgement is completed")

            judgements = judges_result["judgements"]
            scores = judges_result["scores"]

            judges_token_usage = judges_result["judges_token_usage"]
            self._token_usage.add_usage(judges_token_usage)
            logger.info(f"Judges token usage: {judges_token_usage}")
            logger.info(f"Overall token usage: {self._token_usage}")

            total_elapsed += judges_result["judges_elapsed"]

        return {
            "answers": answers,
            "iterations": iterations,
            "judgements": judgements,
            "scores": scores,
            "token_usage": self._token_usage,
            "elapsed": total_elapsed,
        }
