import unittest
import os
import shutil

from tests.utils import *

from AIToolbox.experiment_save.local_experiment_saver import *
from AIToolbox.experiment_save.experiment_saver import AbstractExperimentSaver
from AIToolbox.experiment_save.result_package.abstract_result_packages import AbstractResultPackage
from AIToolbox.experiment_save.local_save.local_model_save import PyTorchLocalModelSaver, KerasLocalModelSaver
from AIToolbox.experiment_save.local_save.local_results_save import LocalResultsSaver
from AIToolbox.experiment_save.training_history import TrainingHistory


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class DummyFullResultPackage(AbstractResultPackage):
    def __init__(self, result_dict, hyper_params, train_hist):
        AbstractResultPackage.__init__(self, 'dummyFullPkg')
        self.result_dict = result_dict
        self.hyper_params = hyper_params
        self.training_history = TrainingHistory().wrap_pre_prepared_history(train_hist, [])
        self.y_true = [10.0] * 100
        self.y_predicted = [123.4] * 100

    def prepare_results_dict(self):
        return self.result_dict

    def get_results(self):
        return self.prepare_results_dict()

    def get_hyperparameters(self):
        return self.hyper_params

    def get_training_history(self):
        return self.get_training_history_object()


class TestFullPyTorchExperimentLocalSaver(unittest.TestCase):
    def test_init(self):
        project_dir_name = 'projectPyTorchLocalModelSaver'
        exp_dir_name = 'experimentSubDirPT'

        saver = FullPyTorchExperimentLocalSaver(project_name=project_dir_name, experiment_name=exp_dir_name,
                                                local_model_result_folder_path=THIS_DIR)
        self.assertIsInstance(saver, AbstractExperimentSaver)
        self.assertIsInstance(saver, BaseFullExperimentLocalSaver)
        self.assertEqual(type(saver.model_saver), PyTorchLocalModelSaver)
        self.assertEqual(type(saver.results_saver), LocalResultsSaver)

    def test_save_experiment(self):
        self.save_experiment_options(save_true_pred_labels=True, separate_files=True)
        self.save_experiment_options(save_true_pred_labels=True, separate_files=False)
        self.save_experiment_options(save_true_pred_labels=False, separate_files=True)
        self.save_experiment_options(save_true_pred_labels=False, separate_files=False)

    def save_experiment_options(self, save_true_pred_labels, separate_files):
        model = Net()
        project_dir_name = 'projectPyTorchLocalModelSaver'
        exp_dir_name = 'experimentSubDirPT'
        current_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

        project_path = os.path.join(THIS_DIR, project_dir_name)
        exp_path = os.path.join(project_path, f'{exp_dir_name}_{current_time}')
        model_path = os.path.join(exp_path, 'model')
        results_path = os.path.join(exp_path, 'results')

        result_pkg = DummyFullResultPackage({'metric1': 33434, 'acc1': 223.43, 'loss': 4455.6},
                                            {'epoch': 20, 'lr': 0.334}, {})

        saver = FullPyTorchExperimentLocalSaver(project_name=project_dir_name, experiment_name=exp_dir_name,
                                                local_model_result_folder_path=THIS_DIR)
        saved_paths = saver.save_experiment(model, result_pkg, current_time,
                                            save_true_pred_labels=save_true_pred_labels, separate_files=separate_files)

        model_file_path_true = os.path.join(model_path, f'model_{exp_dir_name}_{current_time}.pth')
        model_weights_file_path_true = os.path.join(model_path, f'modelWeights_{exp_dir_name}_{current_time}.pth')

        self.assertTrue(os.path.exists(model_file_path_true))
        self.assertTrue(os.path.exists(model_weights_file_path_true))

        if not separate_files:
            saved_paths_true = [model_file_path_true, model_weights_file_path_true,
                                os.path.join(results_path, f'results_hyperParams_hist_{exp_dir_name}_{current_time}.p')]
        else:
            saved_paths_true = [model_file_path_true, model_weights_file_path_true,
                                os.path.join(results_path, f'results_{exp_dir_name}_{current_time}.p'),
                                os.path.join(results_path, f'hyperparams_{exp_dir_name}_{current_time}.p'),
                                os.path.join(results_path, f'train_history_{exp_dir_name}_{current_time}.p')]
            
            if save_true_pred_labels:
                saved_paths_true.append(os.path.join(results_path, f'true_pred_labels_{exp_dir_name}_{current_time}.p'))

        self.assertEqual(sorted(saved_paths_true), sorted(saved_paths))

        if os.path.exists(project_path):
            shutil.rmtree(project_path)


class TestFullKerasExperimentLocalSaver(unittest.TestCase):
    def test_init(self):
        project_dir_name = 'projectPyTorchLocalModelSaver'
        exp_dir_name = 'experimentSubDirPT'

        saver = FullKerasExperimentLocalSaver(project_name=project_dir_name, experiment_name=exp_dir_name,
                                              local_model_result_folder_path=THIS_DIR)
        self.assertIsInstance(saver, AbstractExperimentSaver)
        self.assertIsInstance(saver, BaseFullExperimentLocalSaver)
        self.assertEqual(type(saver.model_saver), KerasLocalModelSaver)
        self.assertEqual(type(saver.results_saver), LocalResultsSaver)

    def test_save_experiment(self):
        self.save_experiment_options(save_true_pred_labels=True, separate_files=True)
        self.save_experiment_options(save_true_pred_labels=True, separate_files=False)
        self.save_experiment_options(save_true_pred_labels=False, separate_files=True)
        self.save_experiment_options(save_true_pred_labels=False, separate_files=False)

    def save_experiment_options(self, save_true_pred_labels, separate_files):
        model = keras_dummy_model()
        project_dir_name = 'projectKerasLocalModelSaver'
        exp_dir_name = 'experimentSubDirPT'
        current_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

        project_path = os.path.join(THIS_DIR, project_dir_name)
        exp_path = os.path.join(project_path, f'{exp_dir_name}_{current_time}')
        model_path = os.path.join(exp_path, 'model')
        results_path = os.path.join(exp_path, 'results')

        result_pkg = DummyFullResultPackage({'metric1': 33434, 'acc1': 223.43, 'loss': 4455.6},
                                            {'epoch': 20, 'lr': 0.334}, {})

        saver = FullKerasExperimentLocalSaver(project_name=project_dir_name, experiment_name=exp_dir_name,
                                              local_model_result_folder_path=THIS_DIR)
        saved_paths = saver.save_experiment(model, result_pkg, current_time,
                                            save_true_pred_labels=save_true_pred_labels, separate_files=separate_files)

        model_file_path_true = os.path.join(model_path, f'model_{exp_dir_name}_{current_time}.h5')
        model_weights_file_path_true = os.path.join(model_path, f'modelWeights_{exp_dir_name}_{current_time}.h5')

        self.assertTrue(os.path.exists(model_file_path_true))
        self.assertTrue(os.path.exists(model_weights_file_path_true))

        if not separate_files:
            saved_paths_true = [model_file_path_true, model_weights_file_path_true,
                                os.path.join(results_path, f'results_hyperParams_hist_{exp_dir_name}_{current_time}.p')]
        else:
            saved_paths_true = [model_file_path_true, model_weights_file_path_true,
                                os.path.join(results_path, f'results_{exp_dir_name}_{current_time}.p'),
                                os.path.join(results_path, f'hyperparams_{exp_dir_name}_{current_time}.p'),
                                os.path.join(results_path, f'train_history_{exp_dir_name}_{current_time}.p')]

            if save_true_pred_labels:
                saved_paths_true.append(os.path.join(results_path, f'true_pred_labels_{exp_dir_name}_{current_time}.p'))

        self.assertEqual(sorted(saved_paths_true), sorted(saved_paths))

        if os.path.exists(project_path):
            shutil.rmtree(project_path)