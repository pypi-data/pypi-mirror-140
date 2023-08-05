import logging
from apache_beam.runners import runner

_LOGGER = logging.getLogger(__name__)

class RayRunner(runner.PipelineRunner):
    def is_fnapi_compatible(self):
        return True

    def run_pipeline(self, pipeline, options):
        pass

    def run_pipeline_via_runner_api(self, pipeline_proto):
        pass