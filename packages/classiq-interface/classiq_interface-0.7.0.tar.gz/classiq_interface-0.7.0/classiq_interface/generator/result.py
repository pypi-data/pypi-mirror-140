import base64
import enum
import io
import json
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pydantic
from PIL import Image

from classiq_interface.generator.generation_metadata import GenerationMetadata
from classiq_interface.generator.synthesis_metrics import SynthesisMetrics

_MAXIMUM_STRING_LENGTH = 250

_LOGO_HTML = '<p>\n    <img src="https://classiq-public.s3.amazonaws.com/logo/Green/classiq_RGB_Green.png" alt="Classiq logo" height="40">\n    <br>\n  </p>\n'


class LongStr(str):
    def __repr__(self):
        if len(self) > _MAXIMUM_STRING_LENGTH:
            length = len(self)
            return f'"{self[:4]}...{self[-4:]}" (length={length})'
        return super().__repr__()


class QasmVersion(str, enum.Enum):
    V2 = "2.0"
    V3 = "3.0"


class QuantumFormat(str, enum.Enum):
    QASM = "qasm"
    QSHARP = "qs"
    QIR = "ll"
    IONQ = "ionq"
    CIRQ_JSON = "cirq_json"
    QASM_CIRQ_COMPATIBLE = "qasm_cirq_compatible"


class GenerationStatus(str, enum.Enum):
    NONE = "none"
    SUCCESS = "success"
    UNSAT = "unsat"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"


# TODO: Merge all output formats to single field (dictionary?) to avoid clutter
class GeneratedCircuit(pydantic.BaseModel):
    qubit_count: int
    depth: Optional[int]
    qasm: Optional[str]
    transpiled_qasm: Optional[str]
    qsharp: Optional[str]
    qir: Optional[str]
    ionq: Optional[str]
    cirq_json: Optional[str]
    qasm_cirq_compatible: Optional[str]
    output_format: List[QuantumFormat]
    qasm_version: QasmVersion
    image_raw: str
    interactive_html: Optional[str]
    metadata: Optional[GenerationMetadata]
    synthesis_metrics: Optional[SynthesisMetrics]
    analyzer_data: Dict

    def show(self) -> None:
        self.image.show()

    def show_interactive(self, jupyter=False):
        if self.interactive_html is None:
            raise ValueError("Missing interactive html")
        if jupyter:  # show inline in jupyter
            # We assume that we're inside a jupyter-notebook
            # We cannot test it, since this is a part of the interface, while the jupyter-related code is in the SDK
            from IPython.core.display import HTML, display  # type: ignore

            h = HTML(self.interactive_html.replace(_LOGO_HTML, ""))
            display(h)

        else:  # open webbrowser
            with tempfile.NamedTemporaryFile(
                "w", delete=False, suffix="_interactive_circuit.html"
            ) as f:
                url = f"file://{f.name}"
                f.write(self.interactive_html)
            webbrowser.open(url)

    @property
    def image(self):
        return Image.open(io.BytesIO(base64.b64decode(self.image_raw)))

    def save_results(self, filename: Optional[Union[str, Path]] = None) -> None:
        """
        Saves generated circuit results as json.
            Parameters:
                filename (Union[str, Path]): Optional, path + filename of file.
                                             If filename supplied add `.json` suffix.

            Returns:
                  None
        """
        if filename:
            path = Path(filename)
        else:
            path = Path(
                f"generated_circuit_{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.json"
            )
        path.write_text(json.dumps(self.dict(), indent=4))

    @pydantic.validator("qasm", "transpiled_qasm", "image_raw", "interactive_html")
    def reformat_long_strings(cls, v):
        if v is None:
            return v
        return LongStr(v)


class GenerationResult(pydantic.BaseModel):
    status: GenerationStatus
    details: Union[GeneratedCircuit, str]
