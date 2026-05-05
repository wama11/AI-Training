from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd
from sklearn.ensemble import IsolationForest

class Tool_anomali_input(BaseModel):
    file: str= Field(..., description ="ini adalah input tool anomali")

class Tool_anomali(BaseTool):
    name : str = "Tool deteksi anomali"
    description:str = "Untuk deteksi anomali data excel"
    args_schema:Type[BaseModel]= Tool_anomali_input

    def _run(self, file:str)-> str:
        df = pd.read_excel(file,sheet_name=0)
        df = df.iloc[:,1:]
        for col in df.select_dtypes(include=['object']).columns:
            df[col]= pd.to_numeric(df[col], errors='coerce')
        df_clean = df.dropna()
        df_clean['day_number'] = (df_clean['time']-pd.Timestamp('2000-01-01')).dt.days
        df_fix = df_clean.iloc[:,1:]

        iso_forest = IsolationForest(
            contamination=0.05,
            random_state=40,
            n_estimators=100,
            )
        iso_forest.fit(df_fix)
        df_fix['anomali']= iso_forest.predict(df_fix)
        anomali_count = (df_fix['anomali']==-1).sum()
        total_data = len(df_fix)

        dataReturn = {
            "anomali" : anomali_count,
            "total_data" : total_data
        }

        return dataReturn
