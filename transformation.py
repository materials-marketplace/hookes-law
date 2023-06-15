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


class HookesLaw:
    """Manage a Hooke's Law calculation."""

    def __init__(self, transformation_input: TransformationInput):
        self.id: str = str(uuid.uuid4())
        self.parameters = transformation_input
        self.state: TransformationState = TransformationState.CREATED
        self.result = None

    def run(self):
        """
        Run a new transformation

        Raises:
            RuntimeError: when the transformation has already ran
        """
        if self.state != TransformationState.CREATED:
            msg = f"Simulation '{self.job_id}' already run."
            logging.error(msg)
            raise RuntimeError(msg)
        self.compute_hookes_law()
        self.state = TransformationState.COMPLETED
        logging.info(f"Simulation '{self.job_id}' started successfully.")

    def compute_hookes_law(self):
        """
        Carry out the calculation.

        Read the relevant parameters and update the transformation result.
        """
        self.result = self.parameters.stiffness * self.parameters.displacement
