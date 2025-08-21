from fastapi import APIRouter, Request

from .schemas import SolveRequest, SolveResponse
from .service import solve as solve_service

router = APIRouter()


@router.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest, request: Request) -> SolveResponse:
    return await solve_service(req, request)
