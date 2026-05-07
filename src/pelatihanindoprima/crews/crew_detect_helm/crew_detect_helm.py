from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from src.pelatihanindoprima.tools.tool_helmet_detection import Tool_helmet_detection
from src.pelatihanindoprima.tools.tool_save_to_db import Tool_save_to_db
from crewai_tools import FileReadTool
from pydantic import BaseModel, Field
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class CrewDetectHelm():
    """CrewDetectHelm crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    fileReadTool=FileReadTool()

    # ✅ FIX: gunakan int, bukan string
    class Output_hasil_detection(BaseModel):
        helmet: int = Field(..., description="jumlah helmet")
        head: int = Field(..., description="jumlah kepala tanpa helmet")
        person: int = Field(..., description="jumlah orang")

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def agent_helmet_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['agent_helmet_detector'], # type: ignore[index]
            verbose=True,
            tools =[Tool_helmet_detection()]
        )

    @agent
    def agent_helmet_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['agent_helmet_analyzer'],
            verbose=True,
            tools=[Tool_save_to_db()]  # ✅ FIX: tool DB dipakai di analyzer
        )



    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def helmet_detector_task(self) -> Task:
        return Task(
            config=self.tasks_config['helmet_detector_task'], # type: ignore[index]
            # output_json = self.Output_hasil_detection
        )

    @task
    def task_helmet_analyzer(self) -> Task:
        return Task(
            # config=self.tasks_config['task_helmet_analyzer'], # type: ignore[index]

            config=self.tasks_config['task_helmet_analyzer'],
            # ✅ FIX: ambil output dari task sebelumnya
            context=[self.helmet_detector_task()]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the CrewDetectHelm crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
