import unittest
import os
from tempfile import TemporaryDirectory
from brevettiai.platform import Job, JobSettings, PlatformBackend


class TestPlatformJob(unittest.TestCase):
    def test_extra_arguments_on_job(self):
        job = Job(name=str(self), settings=JobSettings(test="value"))
        assert job.settings.extra["test"] == "value"

    def test_job_create_schema(self):
        job = Job(name=str(self), settings=JobSettings(test="value"))
        builder = job.settings.platform_schema()

    def test_job_lifecycle(self):
        with TemporaryDirectory() as tempdir:
            backend = PlatformBackend(data_bucket=tempdir)
            job = Job(name=str(self), settings=JobSettings(test="value"),
                      backend=backend)
            job.start()
            job.upload_artifact("modelfile", "")
            job.complete()

            assert {"modelfile", "output.json"} == set(os.listdir(job.artifact_path()))


if __name__ == '__main__':
    unittest.main()
