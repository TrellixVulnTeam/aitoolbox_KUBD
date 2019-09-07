import torch

from AIToolbox.torchtrain.callbacks.callbacks import AbstractCallback


class GradNormClipCallback(AbstractCallback):
    def __init__(self, max_norm, **kwargs):
        """Gradient norm clipping

        Args:
            max_norm (int or float): gradient clipping
            **kwargs:
        """
        AbstractCallback.__init__(self, 'Gradient clipping')
        self.max_norm = max_norm
        self.kwargs = kwargs

    def on_gradient_update(self):
        torch.nn.utils.clip_grad_norm_(self.train_loop_obj.model.parameters(), self.max_norm, **self.kwargs)