import copy
import json
import os
import tempfile

from octue.cloud import storage
from octue.cloud.storage import GoogleCloudStorageClient
from octue.resources import Datafile, Dataset, Manifest
from tests import TEST_BUCKET_NAME, TEST_PROJECT_NAME
from tests.base import BaseTestCase
from tests.resources import create_dataset_with_two_files


class TestManifest(BaseTestCase):
    def test_hash_value(self):
        """Test hashing a manifest with multiple datasets gives a hash of length 8."""
        manifest = self.create_valid_manifest()
        hash_ = manifest.hash_value
        self.assertTrue(isinstance(hash_, str))
        self.assertTrue(len(hash_) == 8)

    def test_hashes_for_the_same_manifest_are_the_same(self):
        """Ensure the hashes for two manifests that are exactly the same are the same."""
        first_manifest = self.create_valid_manifest()
        second_manifest = copy.deepcopy(first_manifest)
        self.assertEqual(first_manifest.hash_value, second_manifest.hash_value)

    def test_all_datasets_are_in_cloud(self):
        """Test whether all files of all datasets in a manifest are in the cloud or not can be determined."""
        self.assertFalse(Manifest().all_datasets_are_in_cloud)
        self.assertFalse(self.create_valid_manifest().all_datasets_are_in_cloud)

        files = [
            Datafile(path="gs://hello/file.txt", project_name="blah", hypothetical=True),
            Datafile(path="gs://goodbye/file.csv", project_name="blah", hypothetical=True),
        ]

        manifest = Manifest(datasets=[Dataset(files=files)], keys={"my_dataset": 0})
        self.assertTrue(manifest.all_datasets_are_in_cloud)

    def test_deserialise(self):
        """Test that manifests can be deserialised."""
        manifest = self.create_valid_manifest()
        serialised_manifest = manifest.to_primitive()
        deserialised_manifest = Manifest.deserialise(serialised_manifest)

        self.assertEqual(manifest.name, deserialised_manifest.name)
        self.assertEqual(manifest.id, deserialised_manifest.id)
        self.assertEqual(manifest.absolute_path, deserialised_manifest.absolute_path)
        self.assertEqual(manifest.keys, deserialised_manifest.keys)

        for original_dataset, deserialised_dataset in zip(manifest.datasets, deserialised_manifest.datasets):
            self.assertEqual(original_dataset.name, deserialised_dataset.name)
            self.assertEqual(original_dataset.id, deserialised_dataset.id)
            self.assertEqual(original_dataset.absolute_path, deserialised_dataset.absolute_path)

    def test_to_cloud(self):
        """Test that a manifest can be uploaded to the cloud as a serialised JSON file of the Manifest instance via
        (`bucket_name`, `output_directory`) and via `gs_path`.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset_directory_name = os.path.split(temporary_directory)[-1]
            dataset = create_dataset_with_two_files(temporary_directory)
            manifest = Manifest(datasets=[dataset], keys={"my-dataset": 0})

            path_to_manifest_file = storage.path.join("blah", "manifest.json")
            gs_path = storage.path.generate_gs_path(TEST_BUCKET_NAME, path_to_manifest_file)

            for location_parameters in (
                {"bucket_name": TEST_BUCKET_NAME, "path_to_manifest_file": path_to_manifest_file, "cloud_path": None},
                {"bucket_name": None, "path_to_manifest_file": None, "cloud_path": gs_path},
            ):
                manifest.to_cloud(TEST_PROJECT_NAME, **location_parameters)

        persisted_manifest = json.loads(
            GoogleCloudStorageClient(TEST_PROJECT_NAME).download_as_string(
                bucket_name=TEST_BUCKET_NAME,
                path_in_bucket=storage.path.join("blah", "manifest.json"),
            )
        )

        self.assertEqual(persisted_manifest["datasets"], [f"gs://octue-test-bucket/blah/{dataset_directory_name}"])
        self.assertEqual(persisted_manifest["keys"], {"my-dataset": 0})

    def test_to_cloud_without_storing_datasets(self):
        """Test that a manifest can be uploaded to the cloud as a serialised JSON file of the Manifest instance."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = create_dataset_with_two_files(temporary_directory)
            manifest = Manifest(datasets=[dataset], keys={"my-dataset": 0})

            manifest.to_cloud(
                TEST_PROJECT_NAME,
                bucket_name=TEST_BUCKET_NAME,
                path_to_manifest_file=storage.path.join("my-manifests", "manifest.json"),
                store_datasets=False,
            )

        persisted_manifest = json.loads(
            GoogleCloudStorageClient(TEST_PROJECT_NAME).download_as_string(
                bucket_name=TEST_BUCKET_NAME,
                path_in_bucket=storage.path.join("my-manifests", "manifest.json"),
            )
        )

        self.assertEqual(persisted_manifest["datasets"], [temporary_directory])
        self.assertEqual(persisted_manifest["keys"], {"my-dataset": 0})

    def test_from_cloud(self):
        """Test that a Manifest can be instantiated from the cloud via (`bucket_name`, `output_directory`) and via
        `gs_path`.
        """
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = create_dataset_with_two_files(temporary_directory)
            manifest = Manifest(datasets=[dataset], keys={"my-dataset": 0})

            manifest.to_cloud(
                TEST_PROJECT_NAME,
                bucket_name=TEST_BUCKET_NAME,
                path_to_manifest_file=storage.path.join("my-directory", "manifest.json"),
            )

            path_to_manifest_file = storage.path.join("my-directory", "manifest.json")
            gs_path = storage.path.generate_gs_path(TEST_BUCKET_NAME, path_to_manifest_file)

            for location_parameters in (
                {"bucket_name": TEST_BUCKET_NAME, "path_to_manifest_file": path_to_manifest_file, "cloud_path": None},
                {"bucket_name": None, "path_to_manifest_file": None, "cloud_path": gs_path},
            ):
                persisted_manifest = Manifest.from_cloud(project_name=TEST_PROJECT_NAME, **location_parameters)

                self.assertEqual(persisted_manifest.path, f"gs://{TEST_BUCKET_NAME}/my-directory/manifest.json")
                self.assertEqual(persisted_manifest.id, manifest.id)
                self.assertEqual(persisted_manifest.hash_value, manifest.hash_value)
                self.assertEqual(persisted_manifest.keys, manifest.keys)
                self.assertEqual(
                    {dataset.name for dataset in persisted_manifest.datasets},
                    {dataset.name for dataset in manifest.datasets},
                )

                for dataset in persisted_manifest.datasets:
                    self.assertEqual(dataset.path, f"gs://{TEST_BUCKET_NAME}/my-directory/{dataset.name}")
                    self.assertTrue(len(dataset.files), 2)
                    self.assertTrue(all(isinstance(file, Datafile) for file in dataset.files))

    def test_instantiating_from_serialised_cloud_datasets_with_no_dataset_json_file(self):
        """Test that a Manifest can be instantiated from a serialized cloud dataset with no `dataset.json` file. This
        simulates what happens when such a cloud dataset is referred to in a manifest received by a child service.
        """
        GoogleCloudStorageClient(TEST_PROJECT_NAME).upload_from_string(
            "[1, 2, 3]", bucket_name=TEST_BUCKET_NAME, path_in_bucket="my_dataset/file_0.txt"
        )

        GoogleCloudStorageClient(TEST_PROJECT_NAME).upload_from_string(
            "[4, 5, 6]", bucket_name=TEST_BUCKET_NAME, path_in_bucket="my_dataset/file_1.txt"
        )

        serialised_cloud_dataset = Dataset.from_cloud(
            project_name=TEST_PROJECT_NAME,
            cloud_path=f"gs://{TEST_BUCKET_NAME}/my_dataset",
        ).to_primitive()

        manifest = Manifest(datasets=[serialised_cloud_dataset], keys={"my_dataset": 0})
        self.assertEqual(len(manifest.datasets), 1)
        self.assertEqual(manifest.datasets[0].path, f"gs://{TEST_BUCKET_NAME}/my_dataset")
        self.assertEqual(len(manifest.datasets[0].files), 2)
