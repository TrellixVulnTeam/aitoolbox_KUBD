import unittest

from tests.utils import *

from AIToolbox.experiment_save.model_rerun import PyTorchModelReRunner


class TestAbstractModelReRunner(unittest.TestCase):
    def test_if_has_abstractmethod(self):
        model = Net()
        dummy_val_loader = list(range(2))
        batch_loader = DeactivateModelFeedDefinition()
        re_runner = PyTorchModelReRunner(model, dummy_val_loader, batch_loader)

        self.assertTrue(function_exists(re_runner, 'model_predict'))
        self.assertTrue(function_exists(re_runner, 'model_get_loss'))
        self.assertTrue(function_exists(re_runner, 'evaluate_result_package'))

    def test_predict(self):
        model = Net()
        dummy_val_loader = list(range(2))
        batch_loader = DeactivateModelFeedDefinition()
        re_runner = PyTorchModelReRunner(model, dummy_val_loader, batch_loader)

        y_test, y_pred, metadata = re_runner.model_predict()

        r = []
        for i in range(1, len(dummy_val_loader) + 1):
            r += [i] * 64
        r2 = []
        for i in range(1, len(dummy_val_loader) + 1):
            r2 += [i + 100] * 64
        self.assertEqual(y_test.tolist(), r)
        self.assertEqual(y_pred.tolist(), r2)

        d = {'bla': []}
        for i in range(1, len(dummy_val_loader) + 1):
            d['bla'] += [i + 200] * 64
        self.assertEqual(metadata, d)

    def test_get_loss(self):
        model = Net()
        dummy_val_loader = list(range(2))
        batch_loader = DeactivateModelFeedDefinition()
        re_runner = PyTorchModelReRunner(model, dummy_val_loader, batch_loader)

        loss = re_runner.model_get_loss()

        self.assertEqual(loss, 1.0)
        self.assertEqual(batch_loader.dummy_batch.item_ctr, 2)
        self.assertEqual(batch_loader.dummy_batch.back_ctr, 0)
        
    def test_evaluate_result_package(self):
        model = Net()
        dummy_val_loader = list(range(2))
        batch_loader = DeactivateModelFeedDefinition()
        re_runner = PyTorchModelReRunner(model, dummy_val_loader, batch_loader)

        result_pkg = DummyResultPackageExtend()
        result_pkg_return = re_runner.evaluate_result_package(result_package=result_pkg, return_result_package=True)

        self.assertEqual(result_pkg, result_pkg_return)
        self.assertEqual(result_pkg_return.results_dict, {'dummy': 111, 'extended_dummy': 1323123.44})
        self.assertEqual(result_pkg_return.get_results(), {'dummy': 111, 'extended_dummy': 1323123.44})
        self.assertEqual(result_pkg_return.ctr, 12.)

        y_test = result_pkg_return.y_true
        y_pred = result_pkg_return.y_predicted
        metadata = result_pkg_return.additional_results['additional_results']

        r = []
        for i in range(1, len(dummy_val_loader) + 1):
            r += [i] * 64
        r2 = []
        for i in range(1, len(dummy_val_loader) + 1):
            r2 += [i + 100] * 64
        self.assertEqual(y_test.tolist(), r)
        self.assertEqual(y_pred.tolist(), r2)

        d = {'bla': []}
        for i in range(1, len(dummy_val_loader) + 1):
            d['bla'] += [i + 200] * 64
        self.assertEqual(metadata, d)

    def test_evaluate_result_package_get_results(self):
        model = Net()
        dummy_val_loader = list(range(2))
        batch_loader = DeactivateModelFeedDefinition()
        re_runner = PyTorchModelReRunner(model, dummy_val_loader, batch_loader)

        result_pkg = DummyResultPackageExtend()
        result_dict = re_runner.evaluate_result_package(result_package=result_pkg, return_result_package=False)

        self.assertEqual(result_dict, {'dummy': 111, 'extended_dummy': 1323123.44})