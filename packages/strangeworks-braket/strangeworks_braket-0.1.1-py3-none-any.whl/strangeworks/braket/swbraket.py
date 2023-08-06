from .utils.serialize import braket_to_sw, sw_to_braket
from braket.circuits import Circuit
from braket.tasks import GateModelQuantumTaskResult
import strangeworks
from strangeworks.jobs.jobs import Job


def get_backends():
    res = []
    backends = strangeworks.client.circuit_runner.get_backends(pprint=False)
    for b in backends:
        if "aws" in b.selector_id():
            res.append(b.selector_id())
    return res


def run_circuit(circuit: Circuit, backend: str, shots: int = 1, **kwargs) -> Job:
    payload = braket_to_sw(circuit)
    job = strangeworks.circuit_runner.run(
        payload=payload, shots=shots, backend=backend, **kwargs
    )
    return job


def get_circuit_results(job: Job) -> GateModelQuantumTaskResult:
    return sw_to_braket(job.results())
