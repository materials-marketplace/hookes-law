import logging
import uuid

from marketplace_standard_app_api.models.transformation import (
    TransformationState,
)
from pydantic import BaseModel


class TransformationInput(BaseModel):
    # Default stiffness of gold at 20C
    stiffness: float = 78
    displacement: float = 3.0


class TransformationOutput(BaseModel):
    result: float


class HookesLaw:
    """Manage a Hooke's Law calculation."""

    def __init__(self, transformation_input: TransformationInput):
        self.id: str = str(uuid.uuid4())
        self.parameters = transformation_input
        self.state: TransformationState = TransformationState.CREATED
        self.result: TransformationOutput

    def run(self):
        """
        Run a new transformation

        Raises:
            RuntimeError: when the transformation has already ran
        """
        if self.state != TransformationState.CREATED:
            msg = f"Simulation '{self.id}' already run."
            logging.error(msg)
            raise RuntimeError(msg)
        result = self.compute_hookes_law(
            self.parameters.stiffness, self.parameters.displacement
        )
        self.result = TransformationOutput(result=result)
        self.state = TransformationState.COMPLETED
        logging.info(f"Simulation '{self.id}' started successfully.")

    @staticmethod
    def compute_hookes_law(stiffness: float, displacement: float) -> float:
        """Compute a force via Hooke's Law (F = kx)

        Args:
            stiffness (float): stiffness constant (k)
            displacement (float): displacement on a body (x)

        Returns:
            float: computed force (F)
        """
        return stiffness * displacement
