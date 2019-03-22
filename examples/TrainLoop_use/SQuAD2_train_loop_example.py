from torch.utils.data import DataLoader
from torch import optim
import torch
from torch import nn

from AIToolbox.NLP.dataset.SQuAD2.SQuAD2DataReader import SQuAD2ConcatContextDatasetReader
from AIToolbox.NLP.dataset.torch_dataset import BasicDataset as SQuAD2Dataset
from AIToolbox.NLP.dataset.torch_collate_fns import qa_concat_ctx_span_collate_fn

from AIToolbox.torchtrain.train_loop import TrainLoopModelCheckpointEndSave
from AIToolbox.torchtrain.batch_model_feed_defs import QASpanSQuADModelFeedDefinition

from AIToolbox.torchtrain.callbacks.performance_eval_callbacks import ModelPerformanceEvaluationCallback, ModelPerformancePrintReportCallback
from AIToolbox.torchtrain.callbacks.train_schedule_callbacks import ReduceLROnPlateauScheduler
from AIToolbox.NLP.evaluation.NLP_result_package import QuestionAnswerResultPackage

from memo_net.model_def.basic_qa_net import *


USE_CUDA = torch.cuda.is_available()
device = torch.device("cuda" if USE_CUDA else "cpu")


reader_train = SQuAD2ConcatContextDatasetReader('<PATH>',
                                                is_train=True, dev_mode_size=2)
reader_dev = SQuAD2ConcatContextDatasetReader('<PATH>',
                                              is_train=False, dev_mode_size=2)
data_train, vocab = reader_train.read()
data_dev, _ = reader_dev.read()

data_train2idx = [(torch.Tensor(vocab.convert_sent2idx_sent(paragraph_tokens)),
                   torch.Tensor(vocab.convert_sent2idx_sent(question_tokens)),
                   span_tuple)
                  for paragraph_tokens, question_tokens, span_tuple, _ in data_train]

data_dev2idx = [(torch.Tensor(vocab.convert_sent2idx_sent(paragraph_tokens)),
                 torch.Tensor(vocab.convert_sent2idx_sent(question_tokens)),
                 span_tuple)
                for paragraph_tokens, question_tokens, span_tuple, _ in data_dev]

train_ds = SQuAD2Dataset(data_train2idx)
dev_ds = SQuAD2Dataset(data_dev2idx)
train_loader = DataLoader(train_ds, batch_size=100, collate_fn=qa_concat_ctx_span_collate_fn)
dev_loader = DataLoader(dev_ds, batch_size=100, collate_fn=qa_concat_ctx_span_collate_fn)

output_size = max([max([len(el[0]) for el in data_train]), max([len(el2[0]) for el2 in data_dev])])

model = QABasicRNN(hidden_size=50,
                   output_size=output_size,
                   embedding_dim=50, vocab_size=vocab.num_words,
                   ctx_n_layers=1, qus_n_layers=1, dropout=0.2)

optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()


used_args = {'batch_size': 100, 'hidden_size': 50, 'ctx_n_layers': 1, 'qus_n_layers': 1, 'dropout': 0.2,
             'dev_mode_size': 2, 'lr': 0.001, 'num_epoch': 2}


qa_result_pkg_cp = QuestionAnswerResultPackage([paragraph_tokens for paragraph_tokens, _, _, _ in data_dev],
                                               target_actual_text=[paragraph_text for _, _, _, paragraph_text in data_dev],
                                               output_text_dir='<PATH>'
                                               )

callbacks = [ModelPerformanceEvaluationCallback(qa_result_pkg_cp, used_args,
                                                on_each_epoch=True,
                                                on_train_data=False, on_val_data=True),
             ModelPerformancePrintReportCallback(['val_ROGUE'],
                                                 on_each_epoch=True, list_tracked_metrics=True),
             ReduceLROnPlateauScheduler(threshold=0.1, patience=2, verbose=True)
             ]


print('Starting train loop')

qa_result_pkg_final = QuestionAnswerResultPackage([paragraph_tokens for paragraph_tokens, _, _, _ in data_dev],
                                                  target_actual_text=[paragraph_text for _, _, _, paragraph_text in data_dev],
                                                  output_text_dir='<PATH>')

TrainLoopModelCheckpointEndSave(model, train_loader, dev_loader, QASpanSQuADModelFeedDefinition(), optimizer, criterion,
                                project_name='fullQAModelRunTest',
                                experiment_name='MemoryNetPytorchTest',
                                local_model_result_folder_path='<PATH>',
                                args=used_args,
                                result_package=qa_result_pkg_final)(num_epoch=2, callbacks=callbacks)