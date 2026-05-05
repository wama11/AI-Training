from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileReadTool
# from pydantic import BaseModel
from pydantic import BaseModel, Field
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FileAnalyzer():
    """FileAnalyzer crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    fileReadTool=FileReadTool()

    class Output_txt_analyzer(BaseModel):
        insight:str
        indicator:str

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def agent_file_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['agent_file_analyzer'], # type: ignore[index]
            verbose=True,
            tools = [self.fileReadTool]
        )

    class Output_txt_analyzer_schema(BaseModel):
        analyzer : list["Output_txt_analyzer"] = Field(..., min_length=5)

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def task_agent_analyzer(self) -> Task:
        return Task(
            config=self.tasks_config['task_file_analyzer'], # type: ignore[index]

            output_json = self.Output_txt_analyzer
        )


    @crew
    def crew(self) -> Crew:
        """Creates the FileAnalyzer crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
