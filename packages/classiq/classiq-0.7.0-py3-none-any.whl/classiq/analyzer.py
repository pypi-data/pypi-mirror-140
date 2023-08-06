"""Analyzer module, implementing facilities for analyzing circuits using Classiq platform."""
import asyncio
import webbrowser

from classiq_interface.analyzer import analysis_params, result as analysis_result
from classiq_interface.generator import result as generator_result
from classiq_interface.server import routes

from classiq._internals import api_wrapper, client
from classiq._internals.type_validation import validate_type
from classiq.exceptions import ClassiqAnalyzerError


class Analyzer:
    """Analyzer is the wrapper object for all analysis capabilities."""

    def __init__(self, circuit: generator_result.GeneratedCircuit):
        """Init self.

        Args:
            circuit (): The circuit to be analyzed.
        """
        if circuit.qasm is None:
            raise ValueError("Analysis requires a circuit with valid QASM code")
        self._params = analysis_params.AnalysisParams(qasm=circuit.qasm)

    def analyze(self) -> analysis_result.Analysis:
        """Runs the circuit analysis.

        Returns:
            The analysis result.
        """
        return asyncio.run(self.analyze_async())

    async def analyze_async(self) -> analysis_result.Analysis:
        """Async version of `analyze`
        Runs the circuit analysis.

        Returns:
            The analysis result.
        """
        wrapper = api_wrapper.ApiWrapper()
        result = await wrapper.call_analysis_task(params=self._params)

        if result.status != analysis_result.AnalysisStatus.SUCCESS:
            raise ClassiqAnalyzerError(f"Analysis failed: {result.details}")
        details = validate_type(
            obj=result.details,
            expected_type=analysis_result.Analysis,
            operation="Analysis",
            exception_type=ClassiqAnalyzerError,
        )

        dashboard_path = routes.ANALYZER_DASHBOARD
        self.run_external_app(path=dashboard_path)
        return details

    @staticmethod
    def run_external_app(path: str) -> None:
        backend_uri = client.client().get_backend_uri()
        webbrowser.open_new_tab(f"{backend_uri}{path}")
