import pathlib
import tempfile
from typing import Any, Dict

import joblib

from baseten_scaffolding.constants import SKLEARN
from baseten_scaffolding.definitions.base import WrittenModelScaffoldDefinition
from baseten_scaffolding.model_inference import infer_sklearn_packages, parse_requirements_file


def _serialize_sklearn_model(model: Any) -> tempfile.SpooledTemporaryFile:
    """Serializes a model based on the scikit-learn framework.

    Args:
        model (Any): The model object.

    Returns:
        tempfile.SpooledTemporaryFile: A temporary file wrapper.
    """
    model_joblib = tempfile.TemporaryFile()
    joblib.dump(model, model_joblib, compress=True)
    model_joblib.seek(0)
    return model_joblib


class SKLearnScaffoldDefinition(WrittenModelScaffoldDefinition):

    model_framework = SKLEARN
    model_filename = 'model.joblib'
    _build_args = {}

    @property
    def model_framework_requirements(self):
        if self.requirements_file is None:
            return infer_sklearn_packages()
        return parse_requirements_file(self.requirements_file)

    @property
    def build_args(self) -> Dict:
        return self._build_args

    def serialize_model_to_directory(self, model_directory):
        serialized_model = _serialize_sklearn_model(self.model)
        if self.python_major_minor:
            self._build_args['PYVERSION'] = self.python_major_minor
        with open(pathlib.Path(model_directory, self.model_filename), 'wb') as f:
            f.write(serialized_model.read())
