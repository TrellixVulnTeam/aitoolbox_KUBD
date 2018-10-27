from abc import ABC, abstractmethod
import boto3
import os
import time
import datetime

from AIToolbox.ExperimentSave.LocalResultsSave import LocalResultsSaver


class AbstractResultsSaver(ABC):
    @abstractmethod
    def save_experiment_results(self, result_package, project_name, experiment_name, experiment_timestamp=None,
                                save_true_pred_labels=False, protect_existing_folder=True):
        pass


class SmartResultsSaver:
    def __init__(self, bucket_name='model-result', local_results_folder_path='~/project/model_result'):
        """

        Args:
            bucket_name (str):
            local_results_folder_path (str):
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')

        self.local_model_result_folder_path = os.path.expanduser(local_results_folder_path)

    def save_file(self, local_file_path, s3_file_path):
        """

        Args:
            local_file_path (str):
            s3_file_path (str):

        Returns:
            None
        """
        self.s3_client.upload_file(os.path.expanduser(local_file_path),
                                   self.bucket_name, s3_file_path)

    def create_experiment_S3_folder_structure(self, project_name, experiment_name, experiment_timestamp):
        experiment_s3_path = os.path.join(project_name,
                                          experiment_name + '_' + experiment_timestamp,
                                          'results')
        return experiment_s3_path


class S3ResultsSaver(AbstractResultsSaver, SmartResultsSaver):
    def __init__(self, bucket_name='model-result', local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            bucket_name (str):
            local_model_result_folder_path (str):
        """
        SmartResultsSaver.__init__(self, bucket_name, local_model_result_folder_path)
        self.local_results_saver = LocalResultsSaver(local_model_result_folder_path)

    def save_experiment_results(self, result_package, project_name, experiment_name, experiment_timestamp=None,
                                save_true_pred_labels=False, protect_existing_folder=True):
        if experiment_timestamp is None:
            experiment_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

        saved_local_results_details = self.local_results_saver.save_experiment_results(result_package,
                                                                                       project_name,
                                                                                       experiment_name,
                                                                                       experiment_timestamp,
                                                                                       save_true_pred_labels,
                                                                                       protect_existing_folder)

        results_file_name, results_file_local_path = saved_local_results_details

        experiment_s3_path = self.create_experiment_S3_folder_structure(project_name, experiment_name, experiment_timestamp)
        results_file_s3_path = os.path.join(experiment_s3_path, results_file_name)

        self.save_file(local_file_path=results_file_local_path, s3_file_path=results_file_s3_path)

        return results_file_s3_path, experiment_timestamp
