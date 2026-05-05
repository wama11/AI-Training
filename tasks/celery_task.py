from tasks.celery_app import celery_app
from src.pelatihanindoprima.crews.content_crew.content_crew import ContentCrew
from src.pelatihanindoprima.crews.analisator.analisator import Analisator
from src.pelatihanindoprima.crews.recommender.recommender import Recommender
from src.pelatihanindoprima.crews.file_analyzer.file_analyzer import FileAnalyzer
import logging
import traceback

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="research")
def research(self, topic: str):
    self.update_state(state= 'RUNNING', meta={'current':f'start job for:{topic}'})

    try:
        result = ContentCrew().crew().kickoff(inputs={"topic":topic})
        return str(result)
    except Exception as e:
        logger.error(f'Task failed with error: {e}\n{traceback.format_exc()}')
    raise

@celery_app.task(bind=True, name="market")
def market(self, topic: str):
    self.update_state(state= 'RUNNING', meta={'current':f'start job for:{topic}'})

    try:
        result = Analisator().crew().kickoff(inputs={"topic":topic})
        return str(result)
    except Exception as e:
        logger.error(f'Task failed with error: {e}\n{traceback.format_exc()}')
    raise

# @celery_app.task(bind=True, name="recommendation")
# def recommendation(self, topic: str):
#     self.update_state(state= 'RUNNING', meta={'current':f'start job for:{topic}'})

#     try:
#         result = Recommender().crew().kickoff(inputs={"topic":topic})
#         return str(result)
#     except Exception as e:
#         logger.error(f'Task failed with error: {e}\n{traceback.format_exc()}')
#     raise

@celery_app.task(bind=True, name="recommendation")
def recommendation(self, motor_type: str, km: int, complaint: str, usage: str):

    self.update_state(
        state='RUNNING',
        meta={'current': f'Recommendation for {motor_type}'}
    )

    try:
        result = Recommender().crew().kickoff(inputs={
            "motor_type": motor_type,
            "km": km,
            "complaint": complaint,
            "usage": usage
        })

        return str(result)

    except Exception as e:
        logger.error(f'Task failed with error: {e}\n{traceback.format_exc()}')
        raise

@celery_app.task(bind=True, name="file-txt-analyzer")
def file_txt_analyzer(self,file:str):
    self.update_state(state ="RUNNING",meta={'current':f'start job for:{file}'}
    )

    try:
        result = FileAnalyzer().crew().kickoff(inputs={
            "file": file
        })
        # return getattr(result, "raw", result)
        return result.raw
    except Exception as e:
        logger.error(f'Task failed with error: {e}\n{traceback.format_exc()}')
        raise

