from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class Analisator():
    """Analisator crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # ✅ AGENT
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True
        )

    # 🔥 OPTIONAL (kalau mau upgrade langsung)
    @agent
    def summarizer(self) -> Agent:
        return Agent(
            role="Market Summary Specialist",
            goal="Merangkum analisis menjadi 5 poin penting",
            backstory="Ahli dalam membuat insight singkat dan padat",
            verbose=True
        )

    # ✅ TASK UTAMA
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    # 🔥 TASK TAMBAHAN (opsional tapi direkomendasikan)
    @task
    def summary_task(self) -> Task:
        return Task(
            description=(
                "Buat ringkasan dari hasil analisis pasar terkait {topic} "
                "menjadi 5 poin penting dalam Bahasa Indonesia."
            ),
            expected_output="5 poin ringkasan utama dalam Bahasa Indonesia",
            agent=self.summarizer()
        )

    # ✅ CREW
    @crew
    def crew(self) -> Crew:
        """Creates the Analisator crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
