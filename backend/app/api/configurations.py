from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.configuration import (
    ConfigurationCreate,
    ConfigurationResponse,
    ConfigurationUpdate,
    ConfigurationValidationRequest,
    ConfigurationValidationResponse,
)

router = APIRouter(tags=["Configurations"])


def get_configuration_service(request: Request):
    return request.app.state.configuration_service


@router.post("/configurations", response_model=ConfigurationResponse)
def create_configuration(payload: ConfigurationCreate, service=Depends(
        get_configuration_service)):
    return service.create_configuration(payload)


@router.get("/configurations")
def list_configurations(include_presets: bool = True, service=Depends(
        get_configuration_service)):
    return service.list_configurations(include_presets=include_presets)


@router.get("/configurations/{config_id}",
            response_model=ConfigurationResponse)
def get_configuration(config_id: str, service=Depends(
        get_configuration_service)):
    config = service.get_configuration(config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/configurations/{config_id}",
            response_model=ConfigurationResponse)
def update_configuration(config_id: str, payload: ConfigurationUpdate,
                         service=Depends(get_configuration_service)):
    updated = service.update_configuration(config_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return updated


@router.delete("/configurations/{config_id}")
def delete_configuration(config_id: str, service=Depends(
        get_configuration_service)):
    deleted = service.delete_configuration(config_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"config_id": config_id, "status": "deleted"}


@router.post("/configurations/validate",
             response_model=ConfigurationValidationResponse)
def validate_configuration(payload: ConfigurationValidationRequest,
                           service=Depends(get_configuration_service)):
    return service.validate_configuration(payload)
