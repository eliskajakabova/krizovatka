from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.simulation import (
    SimulationResponse,
    SimulationStartRequest,
    SimulationStartResponse,
    SimulationStatsResponse,
)

router = APIRouter(tags=["Simulations"])


def get_simulation_service(request: Request):
    return request.app.state.simulation_service


@router.post("/simulations/start", response_model=SimulationStartResponse)
def start_simulation(payload: SimulationStartRequest, service=Depends(
        get_simulation_service)):
    return service.start_simulation(payload)


@router.get("/simulations")
def list_simulations(status: str | None = None, config_id: str | None = None,
                     service=Depends(get_simulation_service)):
    return service.list_simulations(status=status, config_id=config_id)


@router.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: str, service=Depends(
        get_simulation_service)):
    simulation = service.get_simulation_response(simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation


@router.get("/simulations/{simulation_id}/stats",
            response_model=SimulationStatsResponse)
def get_simulation_stats(simulation_id: str, service=Depends(
        get_simulation_service)):
    stats = service.get_simulation_stats(simulation_id)
    if stats is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return stats


@router.delete("/simulations/{simulation_id}")
def stop_simulation(simulation_id: str, service=Depends(
        get_simulation_service)):
    result = service.stop_simulation(simulation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return result
