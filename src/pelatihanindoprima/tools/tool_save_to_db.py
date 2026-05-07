from typing import Type

from pydantic import BaseModel, Field

from crewai.tools import BaseTool
import mysql.connector


class Tool_save_to_db_input(BaseModel):
    head: int = Field(..., description="count of head detected")
    person: int = Field(..., description="count of person detected")
    helmet: int = Field(..., description="count of helmet detected")


class Tool_save_to_db(BaseTool):
    name: str = "tool save to db"
    description: str = "tool untuk save ke db."
    args_schema: Type[BaseModel] = Tool_save_to_db_input

    def _run(self, head: int, person: int, helmet: int) -> str:

        connec = None
        cursor = None

        try:
            connec = mysql.connector.connect(
                host = "10.255.255.254",
                user = "root",
                password = "wa123",
                database = "test",
                connection_timeout=5  # 🔥 biar tidak nge-hang
            )

            cursor = connec.cursor()
            if (head > 0):
                detil = "{head} heads, {helmet} helmets, and {person} persons"
                query = "INSERT INTO helmet_report (report_result, report_detected) VALUES (%s, %s)"
                cursor.execute(query, (detil, head))
                connec.commit()

                cursor.close()
                connec.close()
                return ("stored to db")
            else:
                # return ("report that everybody is safe")
                return f"all safe, total head: {head}"
                # return str("total of head is {head}")
        except mysql.connector.Error as e:
            return f"MySQL Error: {e}"

        except Exception as e:
            return f"General Error: {e}"

        finally:
            # ✅ FIX: pastikan selalu ditutup
            if cursor:
                cursor.close()
            if connec:
                connec.close()
