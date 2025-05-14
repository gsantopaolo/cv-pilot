#!/usr/bin/env python3
# src/job_application_crew.py
import logging
import os
from pathlib import Path
from typing import Any

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import SerperDevTool, FileReadTool, MDXSearchTool
from crewai_tools.tools.directory_read_tool.directory_read_tool import DirectoryReadTool
from crewai_tools.tools.file_writer_tool.file_writer_tool import FileWriterTool
from crewai_tools.tools.scrape_website_tool.scrape_website_tool import ScrapeWebsiteTool

# Choose a provider via env LLM_PROVIDER
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
# Default model names per provider (override via MODEL_NAME if needed)
_default_models = {
    "openai": "openai/gpt-4.1-mini",
    # "openai": "openai/gpt-4.1-2025-04-14",
    # "openai": "openai/o3-2025-04-16",
    "anthropic": "anthropic/claude-3-7-sonnet-20250219",
    # "anthropic": "claude-3-5-sonnet-latest",
    "gemini": "gemini/gemini-2.5-pro-exp-03-25"
}
model_name = os.getenv("MODEL_NAME", _default_models.get(LLM_PROVIDER))

# Build the LLM client
api_key_env = f"{LLM_PROVIDER.upper()}_API_KEY"
llm_client = LLM(
    model=model_name,
    api_key=os.getenv(api_key_env)
)

logger = logging.getLogger(__name__)

logger.info(f"🧠 GenAI provider in use: {llm_client.model}")

@CrewBase
class JobApplicationCrew:
    """
    JobApplicationCrew: orchestrates agents for the job application support process.
    """
    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"
    agents: Any
    tasks: Any

    def __init__(self, doc_path: str):
        self.doc_path = doc_path

        # Cache function for tools
        always_cache = lambda args, result: True

        # Web search tool for gathering job posting and profile info
        self._search_tool = SerperDevTool()
        self._search_tool.cache_function = always_cache

        self._doc_dir_tool = DirectoryReadTool(directory=self.doc_path)
        self._doc_dir_tool.cache_function = always_cache

        # File reading tool for reading personal writeups or local files
        self._file_read_tool = FileReadTool()
        # self._file_read_tool.cache_function = always_cache

        self._file_write_tool = FileWriterTool()

        self._scrape_website_tool = ScrapeWebsiteTool()

    # ────────── Agents ──────────


    @agent
    def resume_project_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_project_manager"],
            # tools=[self._search_tool, self._doc_dir_tool, self._file_read_tool],
            llm=llm_client,
            verbose=True,
            allow_delegation=True
        )


    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[self._search_tool, self._doc_dir_tool, self._file_read_tool, self._scrape_website_tool ],
            llm=llm_client,
            verbose=True,
            allow_delegation=True
        )

    @agent
    def profiler(self) -> Agent:
        return Agent(
            config=self.agents_config["profiler"],
            tools=[self._search_tool, self._doc_dir_tool, self._file_read_tool],
            llm=llm_client,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def resume_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_strategist"],
            tools=[self._doc_dir_tool, self._file_read_tool, self._file_write_tool],
            llm=llm_client,
            verbose=True,
            allow_delegation=False
        )
    # ────────── Tasks ──────────

    @task
    def extract_job_requirements(self) -> Task:
        return Task(config=self.tasks_config["extract_job_requirements"])

    @task
    def compile_candidate_profile(self) -> Task:
        return Task(config=self.tasks_config["compile_candidate_profile"])

    @task
    def tailor_resume(self) -> Task:
        return Task(config=self.tasks_config["tailor_resume"])

    # ────────── Build Crew ──────────

    @crew
    def crew(self) -> Crew:
        manager = self.resume_project_manager()
        operational_agents = [a for a in self.agents if a is not manager]
        return Crew(
            agents=operational_agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            manager_llm=llm_client,
            planning=True,
            verbose=True
        )
