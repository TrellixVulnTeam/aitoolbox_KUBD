import numpy as np
from typing import Optional


class AbstractCallback:
    def __init__(self, callback_name, execution_order=0):
        """Abstract callback class that all actual callback classes have to inherit from

        In the inherited callback classes the callback methods should be overwritten and used to implement desired
        callback functionality at specific points of the train loop.

        Args:
            callback_name (str): name of the callback
            execution_order (int): order of the callback execution. If all the used callbacks have the orders set to 0,
                than the callbacks are executed in the order they were registered.
        """
        from AIToolbox.torchtrain.train_loop import TrainLoop

        self.callback_name = callback_name
        self.execution_order = execution_order
        self.train_loop_obj: Optional[TrainLoop] = None

    def register_train_loop_object(self, train_loop_obj):
        """Introduce the reference to the encapsulating trainloop so that the callback has access to the
            low level functionality of the trainloop

        The registration is normally handled by the callback handler found inside the train loops. The handler is
        responsible for all the callback orchestration of the callbacks inside the trainloops.

        Args:
            train_loop_obj (AIToolbox.torchtrain.train_loop.TrainLoop): reference to the encapsulating trainloop

        Returns:
            AbstractCallback: return the reference to the callback after it is registered
        """
        self.train_loop_obj = train_loop_obj
        self.on_train_loop_registration()
        return self

    def on_train_loop_registration(self):
        """Execute callback initialization / preparation after the train_loop_object becomes available

        Returns:

        """
        pass

    def on_epoch_begin(self):
        pass

    def on_epoch_end(self):
        pass

    def on_train_begin(self):
        pass

    def on_train_end(self):
        pass

    def on_batch_begin(self):
        pass

    def on_batch_end(self):
        pass


class ListRegisteredCallbacks(AbstractCallback):
    def __init__(self):
        AbstractCallback.__init__(self, 'Print the list of registered callbacks')

    def on_train_begin(self):
        self.train_loop_obj.callbacks_handler.print_registered_callback_names()


class EarlyStopping(AbstractCallback):
    def __init__(self, monitor='val_loss', min_delta=0., patience=0):
        """Early stopping of the training if the performance stops improving

        Args:
            monitor (str): performance measure that is tracked to decide if performance is improving during training
            min_delta (float): by how much the performance has to improve to still keep training the model
            patience (int): how many epochs the early stopper waits after the performance stopped improving
        """
        # execution_order=99 makes sure that any performance calculation callbacks are executed before and the most
        # recent results can already be found in the train_history
        AbstractCallback.__init__(self, 'EarlyStopping', execution_order=99)
        self.monitor = monitor
        self.min_delta = min_delta
        self.patience = patience

        self.patience_count = self.patience
        self.best_performance = None
        self.best_epoch = 0

    def on_epoch_end(self):
        history_data = self.train_loop_obj.train_history[self.monitor]
        current_performance = history_data[-1]

        if self.best_performance is None:
            self.best_performance = current_performance
            self.best_epoch = self.train_loop_obj.epoch
        else:
            if 'loss' in self.monitor.lower() or 'error' in self.monitor.lower():
                if current_performance < self.best_performance - self.min_delta:
                    self.best_performance = current_performance
                    self.best_epoch = self.train_loop_obj.epoch
                    self.patience_count = self.patience
                else:
                    self.patience_count -= 1
            else:
                if current_performance > self.best_performance + self.min_delta:
                    self.best_performance = current_performance
                    self.best_epoch = self.train_loop_obj.epoch
                    self.patience_count = self.patience
                else:
                    self.patience_count -= 1

            if self.patience_count < 0:
                self.train_loop_obj.early_stop = True
                print(f'Early stopping at epoch: {self.train_loop_obj.epoch}. Best recorded epoch: {self.best_epoch}.')


class TerminateOnNaN(AbstractCallback):
    def __init__(self, monitor='loss'):
        """

        Args:
            monitor (str): performance measure that is tracked to decide if performance is improving during training
        """
        AbstractCallback.__init__(self, 'TerminateOnNaN', execution_order=98)
        self.monitor = monitor

    def on_epoch_end(self):
        last_measure = self.train_loop_obj.train_history[self.monitor][-1]

        if last_measure is not None:
            if np.isnan(last_measure) or np.isinf(last_measure):
                self.train_loop_obj.early_stop = True
                print(f'Terminating on {self.monitor} = {last_measure} at epoch: {self.train_loop_obj.epoch}.')


class AllPredictionsSame(AbstractCallback):
    def __init__(self, value=0., stop_training=False, verbose=True):
        """

        Args:
            value (float): all predictions are the same as this value
            stop_training (bool): if all predictions match the specified value, should the training be (early) stopped
            verbose (bool): output messages
        """
        AbstractCallback.__init__(self, 'All predictions have the same value')
        self.value = value
        self.stop_training = stop_training
        self.verbose = verbose

    def on_epoch_end(self):
        _, predictions, _ = self.train_loop_obj.predict_on_validation_set()

        all_values_same = all(el == self.value for el in predictions)

        if all_values_same:
            if self.verbose:
                print(f'All the predicted values are of the same value: {self.value}')

            if self.stop_training:
                print('Executing early stopping')
                self.train_loop_obj.early_stop = True
