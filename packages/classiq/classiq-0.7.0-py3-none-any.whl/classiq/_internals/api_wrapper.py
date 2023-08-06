import functools
import json
import logging
from typing import Dict, Optional

import httpx
import websockets.client
import websockets.exceptions
import websockets.typing

from classiq_interface.analyzer import analysis_params, result as analysis_result
from classiq_interface.chemistry import ground_state_problem, operator
from classiq_interface.combinatorial_optimization import (
    optimization_problem,
    result as opt_result,
)
from classiq_interface.executor import execution_request, result as execute_result
from classiq_interface.generator import result as generator_result
from classiq_interface.generator.model import Model
from classiq_interface.server import routes

from classiq._internals import client
from classiq.exceptions import ClassiqExpiredTokenError, ClassiqValueError

_FAIL_FAST_INDICATOR = "{"


def _retry_websocket_on_exception(func):
    # TODO fix this workaround
    @functools.wraps(func)
    async def wrapped(self: "ApiWrapper", *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except websockets.exceptions.InvalidStatusCode as exc:
            # If the token is missing or invalid, the handshake fails
            # with a status code of 403. In this case, we refresh the token
            # and try again.
            if exc.status_code == httpx.codes.FORBIDDEN.value:
                await self._client.update_expired_access_token()
                return await func(self, *args, **kwargs)
            raise

    return wrapped


def _decode_message(msg: websockets.typing.Data) -> str:
    return msg.decode() if isinstance(msg, bytes) else msg


async def _get_return_value_from_websocket(
    websocket: websockets.client.WebSocketClientProtocol,
) -> str:
    is_first = True
    msg: str = _decode_message(await websocket.recv())

    while msg:
        logging.info(msg)

        # HACK: This is meant to handle validation errors. It is a duplicate
        # of a similar hack implemented in the VS code extension
        if is_first:
            is_first = False
            if msg.startswith(_FAIL_FAST_INDICATOR):
                return msg

        msg = _decode_message(await websocket.recv())

    return _decode_message(await websocket.recv())


class ApiWrapper:
    def __init__(self) -> None:
        self._client = client.client()

    async def _call_task(self, http_method: str, url: str, body: Optional[Dict] = None):
        try:
            res = await self._client.call_api(
                http_method=http_method, url=url, body=body
            )
        except ClassiqExpiredTokenError:
            await self._client.update_expired_access_token()
            res = await self._client.call_api(
                http_method=http_method, url=url, body=body
            )

        if not isinstance(res, dict):
            raise ClassiqValueError(f"Unexpected returned value: {res}")

        return res

    @_retry_websocket_on_exception
    async def call_generation_task(
        self, model: Model
    ) -> generator_result.GenerationResult:
        async with self._client.establish_websocket_connection(
            path="/api/v1/ws/generate"
        ) as websocket:
            await websocket.send(model.json())
            res = await _get_return_value_from_websocket(websocket)
            return generator_result.GenerationResult.parse_raw(res)

    async def call_execute_task(
        self, request: execution_request.ExecutionRequest
    ) -> execute_result.ExecutionResult:
        data = await self._call_task(
            http_method="post",
            url=routes.EXECUTE_TASKS_FULL_PATH,
            body=json.loads(
                request.json()
            ),  # TODO: request.dict() doesn't serialize complex class
        )

        return execute_result.ExecutionResult.parse_obj(data)

    async def call_analysis_task(
        self, params: analysis_params.AnalysisParams
    ) -> analysis_result.AnalysisResult:
        data = await self._call_task(
            http_method="post",
            url=routes.ANALYZER_FULL_PATH,
            body=params.dict(),
        )

        return analysis_result.AnalysisResult.parse_obj(data)

    async def call_combinatorial_optimization_generate_task(
        self, problem: optimization_problem.OptimizationProblem
    ) -> generator_result.GenerationResult:
        data = await self._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_GENERATE_FULL_PATH,
            body=problem.dict(),
        )

        return generator_result.GenerationResult.parse_obj(data)

    @_retry_websocket_on_exception
    async def call_combinatorial_optimization_solve_task(
        self, problem: optimization_problem.OptimizationProblem
    ) -> execute_result.ExecutionResult:
        async with self._client.establish_websocket_connection(
            path=routes.COMBINATORIAL_OPTIMIZATION_WS_SOLVE_FULL_PATH, ping_interval=20
        ) as websocket:
            await websocket.send(problem.json())
            res = await _get_return_value_from_websocket(websocket)
            return execute_result.ExecutionResult.parse_raw(res)

    async def call_combinatorial_optimization_solve_classically_task(
        self, problem: optimization_problem.OptimizationProblem
    ) -> execute_result.ExecutionResult:
        data = await self._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_SOLVE_CLASSICALLY_FULL_PATH,
            body=problem.dict(),
        )

        return execute_result.ExecutionResult.parse_obj(data)

    async def call_combinatorial_optimization_operator_task(
        self, problem: optimization_problem.OptimizationProblem
    ) -> operator.OperatorResult:
        data = await self._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_OPERATOR_FULL_PATH,
            body=problem.dict(),
        )

        return operator.OperatorResult.parse_obj(data)

    async def call_combinatorial_optimization_objective_task(
        self, problem: optimization_problem.OptimizationProblem
    ) -> opt_result.PyomoObjectResult:
        data = await self._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_OBJECTIVE_FULL_PATH,
            body=problem.dict(),
        )

        return opt_result.PyomoObjectResult.parse_obj(data)

    async def call_combinatorial_optimization_initial_point_task(
        self, problem: optimization_problem.OptimizationProblem
    ) -> opt_result.AnglesResult:
        data = await self._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_INITIAL_POINT_FULL_PATH,
            body=problem.dict(),
        )

        return opt_result.AnglesResult.parse_obj(data)

    async def call_generate_hamiltonian_task(
        self, problem: ground_state_problem.GroundStateProblem
    ) -> operator.OperatorResult:
        data = await self._call_task(
            http_method="post",
            url=routes.GENERATE_CHEMISTRY_HAMILTONIAN_FULL_PATH,
            body=problem.dict(),
        )

        return operator.OperatorResult.parse_obj(data)
