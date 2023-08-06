import braket._sdk
from braket.circuits import Circuit
from braket.schema_common import BraketSchemaBase
from braket.tasks import GateModelQuantumTaskResult
import json


def braket_to_sw(circuit: Circuit) -> dict:
    if not isinstance(circuit, Circuit):
        raise Exception(
            f"strangeworks-braket does not know how to serialize the type {type(circuit)}"
        )

    return {
        "circuit": circuit.to_ir().json(),
        "circuit_type": "braket.circuits.Circuit",
        "version": braket._sdk.__version__,
    }


def sw_to_braket(result: dict) -> GateModelQuantumTaskResult:
    bsh = BraketSchemaBase.parse_raw_schema(json.dumps(result))
    task_result = GateModelQuantumTaskResult.from_object(bsh)
    return task_result
