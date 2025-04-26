from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.integrations.dental_agent import DentalAgentManager
from app.db import db_session


def get_db() -> Generator[Session, None, None]:
    with db_session() as db:
        yield db


class DentalAgentManagerProvider:
    def __init__(self):
        self.dental_agent_manager_instance = None

    def get_manager(self) -> DentalAgentManager:
        if self.dental_agent_manager_instance is None:
            self.dental_agent_manager_instance = DentalAgentManager()
        return self.dental_agent_manager_instance


agent_provider = DentalAgentManagerProvider()
get_dental_manager = agent_provider.get_manager

DentalAgentManagerDep = Annotated[DentalAgentManager, Depends(get_dental_manager)]
SessionDep = Annotated[Session, Depends(get_db)]
