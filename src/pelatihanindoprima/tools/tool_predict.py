from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd
from prophet import Prophet

class Tool_predict_input(BaseModel):
    file: str= Field(..., description ="ini adalah input tool predict")

class Tool_predict(BaseTool):
    name : str = "Tool predict"
    description:str = "Prediksi data time series menggunakan Prophet"
    args_schema:Type[BaseModel]= Tool_predict_input

    def _run(self, file: str):
        df = pd.read_csv(file)
        df['ds'] = pd.to_datetime(df['ds'])

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        return forecast[['ds', 'yhat']].tail(10).to_dict()

