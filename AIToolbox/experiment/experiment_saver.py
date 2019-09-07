from abc import ABC, abstractmethod
import time
import datetime

from AIToolbox.cloud.AWS.model_save import KerasS3ModelSaver, TensorFlowS3ModelSaver, PyTorchS3ModelSaver
from AIToolbox.cloud.AWS.results_save import S3ResultsSaver
from AIToolbox.cloud.GoogleCloud.model_save import KerasGoogleStorageModelSaver, TensorFlowGoogleStorageModelSaver, \
    PyTorchGoogleStorageModelSaver
from AIToolbox.cloud.GoogleCloud.results_save import GoogleStorageResultsSaver


class AbstractExperimentSaver(ABC):
    @abstractmethod
    def save_experiment(self, model, result_package, experiment_timestamp=None,
                        save_true_pred_labels=False, separate_files=False,
                        protect_existing_folder=True):
        """

        Args:
            model:
            result_package (AIToolbox.ExperimentSave.result_package.AbstractResultPackage):
            experiment_timestamp (str): time stamp of the training start
            save_true_pred_labels (bool):
            separate_files (bool):
            protect_existing_folder (bool): can override potentially already existing folder or not

        Returns:
            list: string paths where the experiment files were saved
        """
        pass


class BaseFullExperimentSaver(AbstractExperimentSaver):
    def __init__(self, model_saver, results_saver, project_name, experiment_name):
        """

        Args:
            model_saver (AIToolbox.cloud.AWS.model_save.AbstractModelSaver):
            results_saver (AIToolbox.cloud.AWS.results_save.AbstractResultsSaver):
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
        """
        self.model_saver = model_saver
        self.results_saver = results_saver

        self.project_name = project_name
        self.experiment_name = experiment_name

    def save_experiment(self, model, result_package, experiment_timestamp=None,
                        save_true_pred_labels=False, separate_files=False,
                        protect_existing_folder=True):
        """

        Args:
            model (dict or keras.engine.training.Model):
            result_package (AIToolbox.experiment.result_package.abstract_result_packages.AbstractResultPackage):
            experiment_timestamp (str): time stamp at the start of training
            save_true_pred_labels (bool):
            separate_files (bool):
            protect_existing_folder (bool): can override potentially already existing folder or not

        Returns:
            (str, str): cloud_model_path, cloud_results_path
        """
        if experiment_timestamp is None:
            experiment_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

        cloud_model_path, _, _ = self.model_saver.save_model(model=model,
                                                             project_name=self.project_name,
                                                             experiment_name=self.experiment_name,
                                                             experiment_timestamp=experiment_timestamp,
                                                             protect_existing_folder=protect_existing_folder)

        cloud_results_path, _ = self.results_saver.save_experiment_results(result_package=result_package,
                                                                           project_name=self.project_name,
                                                                           experiment_name=self.experiment_name,
                                                                           experiment_timestamp=experiment_timestamp,
                                                                           save_true_pred_labels=save_true_pred_labels,
                                                                           separate_files=separate_files,
                                                                           protect_existing_folder=protect_existing_folder)
        return cloud_model_path, cloud_results_path


class BaseFullExperimentS3Saver(BaseFullExperimentSaver):
    def __init__(self, model_saver, project_name, experiment_name,
                 bucket_name='model-result', cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            model_saver (AIToolbox.cloud.AWS.model_save.AbstractModelSaver):
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        results_saver = S3ResultsSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                       local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentSaver.__init__(self, model_saver, results_saver, project_name, experiment_name)


class FullKerasExperimentS3Saver(BaseFullExperimentS3Saver):
    def __init__(self, project_name, experiment_name,
                 bucket_name='model-result', cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        keras_model_saver = KerasS3ModelSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                              local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentS3Saver.__init__(self, keras_model_saver, project_name, experiment_name,
                                           bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                           local_model_result_folder_path=local_model_result_folder_path)
        
        
class FullTensorFlowExperimentS3Saver(BaseFullExperimentS3Saver):
    def __init__(self, project_name, experiment_name,
                 bucket_name='model-result', cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        tf_model_saver = TensorFlowS3ModelSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentS3Saver.__init__(self, tf_model_saver, project_name, experiment_name,
                                           bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                           local_model_result_folder_path=local_model_result_folder_path)
        
        raise NotImplementedError


class FullPyTorchExperimentS3Saver(BaseFullExperimentS3Saver):
    def __init__(self, project_name, experiment_name,
                 bucket_name='model-result', cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        pytorch_model_saver = PyTorchS3ModelSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                  local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentS3Saver.__init__(self, pytorch_model_saver, project_name, experiment_name,
                                           bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                           local_model_result_folder_path=local_model_result_folder_path)


class BaseFullExperimentGoogleStorageSaver(BaseFullExperimentSaver):
    def __init__(self, model_saver, project_name, experiment_name,
                 bucket_name='model-result', cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            model_saver (AIToolbox.cloud.AWS.model_save.AbstractModelSaver):
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        results_saver = GoogleStorageResultsSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                  local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentSaver.__init__(self, model_saver, results_saver, project_name, experiment_name)


class FullKerasExperimentGoogleStorageSaver(BaseFullExperimentGoogleStorageSaver):
    def __init__(self, project_name, experiment_name,
                 bucket_name='model-result',  cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        keras_model_saver = KerasGoogleStorageModelSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                         local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentGoogleStorageSaver.__init__(self, keras_model_saver, project_name, experiment_name,
                                                      bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                      local_model_result_folder_path=local_model_result_folder_path)


class FullTensorFlowExperimentGoogleStorageSaver(BaseFullExperimentGoogleStorageSaver):
    def __init__(self, project_name, experiment_name,
                 bucket_name='model-result',  cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        tf_model_saver = TensorFlowGoogleStorageModelSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                           local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentGoogleStorageSaver.__init__(self, tf_model_saver, project_name, experiment_name,
                                                      bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                      local_model_result_folder_path=local_model_result_folder_path)

        raise NotImplementedError


class FullPyTorchExperimentGoogleStorageSaver(BaseFullExperimentGoogleStorageSaver):
    def __init__(self, project_name, experiment_name,
                 bucket_name='model-result',  cloud_dir_prefix='',
                 local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str): root name of the project
            experiment_name (str): name of the particular experiment
            bucket_name (str): name of the bucket in the cloud storage
            cloud_dir_prefix (str): path to the folder inside the bucket where the experiments are going to be saved
            local_model_result_folder_path (str): root local path where project folder will be created
        """
        pytorch_model_saver = PyTorchGoogleStorageModelSaver(bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                             local_model_result_folder_path=local_model_result_folder_path)

        BaseFullExperimentGoogleStorageSaver.__init__(self, pytorch_model_saver, project_name, experiment_name,
                                                      bucket_name=bucket_name, cloud_dir_prefix=cloud_dir_prefix,
                                                      local_model_result_folder_path=local_model_result_folder_path)
