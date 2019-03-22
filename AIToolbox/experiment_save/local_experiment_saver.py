import datetime
import time

from AIToolbox.experiment_save.experiment_saver import AbstractExperimentSaver
from AIToolbox.experiment_save.local_model_save import PyTorchLocalModelSaver, KerasLocalModelSaver, AbstractLocalModelSaver
from AIToolbox.experiment_save.local_results_save import LocalResultsSaver


class BaseFullExperimentLocalSaver(AbstractExperimentSaver):
    def __init__(self, model_saver, project_name, experiment_name, local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            model_saver (AIToolbox.experiment_save.local_model_save.AbstractLocalModelSaver)
            project_name (str):
            experiment_name (str):
            local_model_result_folder_path (str):
        """
        if not isinstance(model_saver, AbstractLocalModelSaver):
            raise TypeError(f'model_saver must be inherited from AbstractLocalModelSaver. '
                            f'model_saver type is: {type(model_saver)}')

        self.project_name = project_name
        self.experiment_name = experiment_name

        self.model_saver = model_saver
        self.results_saver = LocalResultsSaver(local_model_result_folder_path)

    def save_experiment(self, model, result_package, experiment_timestamp=None,
                        save_true_pred_labels=False, separate_files=False,
                        protect_existing_folder=True):
        """

        Args:
            model (torch.nn.modules.Module):
            result_package (AIToolbox.ExperimentSave.result_package.AbstractResultPackage):
            experiment_timestamp (str):
            save_true_pred_labels (bool):
            separate_files (bool):
            protect_existing_folder (bool):

        Returns:
            list:
        """
        if experiment_timestamp is None:
            experiment_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

        _, _, model_local_path, model_weights_local_path = \
            self.model_saver.save_model(model=model,
                                        project_name=self.project_name,
                                        experiment_name=self.experiment_name,
                                        experiment_timestamp=experiment_timestamp,
                                        protect_existing_folder=protect_existing_folder)

        saved_paths = [model_local_path, model_weights_local_path]

        if not separate_files:
            _, results_file_local_path = \
                self.results_saver.save_experiment_results(result_package=result_package,
                                                           project_name=self.project_name,
                                                           experiment_name=self.experiment_name,
                                                           experiment_timestamp=experiment_timestamp,
                                                           save_true_pred_labels=save_true_pred_labels,
                                                           protect_existing_folder=protect_existing_folder)
            saved_paths.append(results_file_local_path)

        else:
            saved_results_paths = \
                self.results_saver.save_experiment_results_separate_files(result_package=result_package,
                                                                          project_name=self.project_name,
                                                                          experiment_name=self.experiment_name,
                                                                          experiment_timestamp=experiment_timestamp,
                                                                          save_true_pred_labels=save_true_pred_labels,
                                                                          protect_existing_folder=protect_existing_folder)
            saved_paths += [path for _, path in saved_results_paths]

        return saved_paths


class FullPyTorchExperimentLocalSaver(BaseFullExperimentLocalSaver):
    def __init__(self, project_name, experiment_name, local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str):
            experiment_name (str):
            local_model_result_folder_path (str):
        """
        BaseFullExperimentLocalSaver.__init__(self, PyTorchLocalModelSaver(local_model_result_folder_path),
                                              project_name, experiment_name,
                                              local_model_result_folder_path=local_model_result_folder_path)


class FullKerasExperimentLocalSaver(BaseFullExperimentLocalSaver):
    def __init__(self, project_name, experiment_name, local_model_result_folder_path='~/project/model_result'):
        """

        Args:
            project_name (str):
            experiment_name (str):
            local_model_result_folder_path (str):
        """
        BaseFullExperimentLocalSaver.__init__(self, KerasLocalModelSaver(local_model_result_folder_path),
                                              project_name, experiment_name,
                                              local_model_result_folder_path=local_model_result_folder_path)