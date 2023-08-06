from typing import Dict, Iterable, List, Set, Type

from classiq_interface.generator import function_call
from classiq_interface.generator.functions import FunctionData

from classiq.exceptions import ClassiqWiringError
from classiq.model_designer import function_handler, wire


class CompositeFunctionInputWire(wire.Wire):
    def __init__(self, input_name: str) -> None:
        super().__init__()
        self._initialize_wire_name(wire_name=input_name)

    @property
    def is_ended(self) -> bool:
        return self._end_call is not None


class CompositeFunctionOutputWire(wire.Wire):
    @property
    def is_ended(self) -> bool:
        return self.is_started and self._start_name in self._start_call.outputs  # type: ignore[union-attr]


class CompositeFunctionGenerator(function_handler.FunctionHandler):
    def __init__(self, function_name: str) -> None:
        super().__init__()
        self._name = function_name
        self._logic_flow_list: List[function_call.FunctionCall] = list()
        self._input_names: Set[str] = set()

    @property
    def _logic_flow(self) -> List[function_call.FunctionCall]:
        return self._logic_flow_list

    @property
    def _output_wire_type(self) -> Type[wire.Wire]:
        return CompositeFunctionOutputWire

    def create_inputs(
        self, input_names: Iterable[str]
    ) -> Dict[str, CompositeFunctionInputWire]:
        input_names = list(input_names)
        if len(input_names) != len(set(input_names)):
            raise ClassiqWiringError("Cannot create multiple inputs with the same name")

        wire_dict = {
            name: CompositeFunctionInputWire(input_name=name) for name in input_names
        }
        self._update_generated_wires(wires=wire_dict.values())

        return wire_dict

    def set_outputs(self, outputs: Dict[str, CompositeFunctionOutputWire]) -> None:
        self._verify_legal_wires(wires=outputs.values())

        for output_name, output_wire in outputs.items():
            if isinstance(output_wire, CompositeFunctionInputWire):
                raise ClassiqWiringError(
                    f"Can't connect input directly to output {output_name}"
                )
            output_wire.set_as_output(output_name=output_name)

    def to_function_data(self) -> FunctionData:
        return FunctionData(name=self._name, logic_flow=self._logic_flow)
