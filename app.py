"""Simple transformation app for Hooke's Law."""
import logging

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from marketplace_standard_app_api.models.transformation import (
    TransformationCreateResponse,
    TransformationId,
    TransformationListResponse,
    TransformationState,
    TransformationStateResponse,
    TransformationUpdateModel,
    TransformationUpdateResponse,
)

from transformation import HookesLaw, TransformationInput, TransformationOutput

app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Hooke's Law app",
        description="MarketPlace simple transformation app",
        version="1.0.0",
        contact={
            "name": "Pablo de Andres",
            "url": "https://materials-marketplace.eu/",
            "email": "pablo.de.andres@iwm.fraunhofer.de",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        servers=[{"url": "https://hookes-law.materials-data.space"}],
        routes=app.routes,
    )
    openapi_schema["info"]["x-api-version"] = "0.4.0"
    openapi_schema["info"]["x-products"] = [{"name": "Monthly"}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


transformations = dict()


@app.get("/", summary="Frontend", operation_id="frontend")
async def get_index():
    return FileResponse("frontend/index.html")


@app.get("/script.js")
async def get_script():
    return FileResponse("frontend/script.js")


@app.get("/styles.css")
async def get_styles():
    return FileResponse("frontend/styles.css")


@app.get(
    "/heartbeat", operation_id="heartbeat", summary="Check if app is alive"
)
async def heartbeat():
    return "Simple transformation app up and running"


@app.post(
    "/transformations",
    operation_id="newTransformation",
    summary="Create a new transformation",
    response_model=TransformationCreateResponse,
)
async def new_transformation(
    payload: TransformationInput,
) -> TransformationCreateResponse:
    new_transformation = HookesLaw(payload)
    transformations[new_transformation.id] = new_transformation
    return {"id": new_transformation.id}


@app.patch(
    "/transformations/{transformation_id}",
    summary="Update the state of the transformation.",
    response_model=TransformationUpdateResponse,
    operation_id="updateTransformation",
    responses={
        404: {"description": "Not Found."},
        400: {"description": "Requested state not supported"},
    },
)
async def update_transformation_state(
    transformation_id: TransformationId, payload: TransformationUpdateModel
) -> TransformationUpdateResponse:
    state = payload.state
    try:
        if state == "RUNNING":
            transformations[str(transformation_id)].run()
        else:
            msg = f"{state} is not a supported state."
            raise HTTPException(status_code=400, detail=msg)
        return {"id": TransformationId(transformation_id), "state": state}
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Transformation not found: {transformation_id}",
        )


@app.get(
    "/transformations/{transformation_id}/state",
    summary="Get the state of the transformation.",
    response_model=TransformationStateResponse,
    operation_id="getTransformationState",
    responses={404: {"description": "Unknown transformation"}},
)
async def get_transformation_state(
    transformation_id: TransformationId,
) -> TransformationStateResponse:
    try:
        state = transformations[str(transformation_id)].state
        return {"id": transformation_id, "state": state}

    except KeyError:
        raise HTTPException(status_code=404, detail="Simulation not found")


@app.get(
    "/transformations",
    summary="Get all transformations.",
    response_model=TransformationListResponse,
    operation_id="getTransformationList",
)
async def get_transformations():
    items = [
        {
            "id": transformation.id,
            "parameters": transformation.parameters,
            "state": transformation.state,
        }
        for transformation in transformations.values()
    ]

    logging.info(f"transformations: {items}")
    return {"items": items}


@app.delete(
    "/transformations/{transformation_id}",
    summary="Delete a transformation",
    operation_id="deleteTransformation",
)
async def delete_transformation(transformation_id: TransformationId):
    try:
        del transformations[str(transformation_id)]
        return {
            "status": f"Simulation '{transformation_id}' deleted successfully!"
        }

    except KeyError as ke:
        raise HTTPException(status_code=404, detail=ke)


@app.get(
    "/datasets/{transformation_id}",
    summary="Get a transformation's result",
    operation_id="getDataset",
    response_model=TransformationOutput,
)
async def get_results(transformation_id: TransformationId):
    try:
        transformation = transformations[str(transformation_id)]
        if transformation.state != TransformationState.COMPLETED:
            raise HTTPException(
                "Transformation {transformation_id} has not run."
            )
        return transformation.result
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=ke)
