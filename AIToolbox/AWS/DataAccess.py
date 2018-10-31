from abc import ABC, abstractmethod
import boto3
import botocore
import os
import shutil


class AbstractDatasetFetcher(ABC):
    @abstractmethod
    def fetch_dataset(self, protect_local_folder=True):
        pass


class SmartDatasetFetcher:
    def __init__(self, bucket_name='dataset-store', local_dataset_folder_path='~/project/data'):
        """

        Args:
            bucket_name (str):
            local_dataset_folder_path (str):
        """
        self.bucket_name = bucket_name
        self.s3 = boto3.resource('s3')

        self.local_dataset_folder_path = os.path.expanduser(local_dataset_folder_path)

        self.available_prepocessed_datasets = []

    def fetch_file(self, s3_file_path, local_file_path):
        """

        Args:
            s3_file_path (str):
            local_file_path (str):

        Returns:
            None

        """
        local_file_path = os.path.expanduser(local_file_path)

        if os.path.isfile(local_file_path):
            print('File already exists on local disk. Not downloading from S3')
        else:
            print('Local file does not exist on the local disk. Downloading from S3')
            try:
                self.s3.Bucket(self.bucket_name).download_file(s3_file_path, local_file_path)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist on S3.")
                else:
                    raise

    def exists_local_dataset_folder(self, dataset_name, protect_local_folder=True):
        """

        Args:
            dataset_name (str):
            protect_local_folder (bool):

        Returns:
            bool

        """
        if os.path.exists(os.path.join(self.local_dataset_folder_path, dataset_name)) and protect_local_folder:
            print('Local folder exists and protect_local_folder in True: leaving local folder as it is.')
            return True

        if os.path.exists(os.path.join(self.local_dataset_folder_path, dataset_name)) and not protect_local_folder:
            print('Local folder exists and protect_local_folder in False: deleting local folder copy')
            shutil.rmtree(os.path.join(self.local_dataset_folder_path, dataset_name))

        os.mkdir(os.path.join(self.local_dataset_folder_path, dataset_name))
        return False

    def preproc_dataset_available(self, preproc_dataset_name):
        return preproc_dataset_name in self.available_prepocessed_datasets


class SQuAD2DatasetFetcher(AbstractDatasetFetcher, SmartDatasetFetcher):
    def __init__(self, bucket_name='dataset-store', local_dataset_folder_path='~/project/data'):
        """

        Args:
            bucket_name (str):
            local_dataset_folder_path (str):
        """
        SmartDatasetFetcher.__init__(self, bucket_name, local_dataset_folder_path)

    def fetch_dataset(self, protect_local_folder=True):
        """

        Args:
            protect_local_folder (bool):

        Returns:
            None

        """
        if not self.exists_local_dataset_folder('SQuAD2', protect_local_folder):
            self.fetch_file(s3_file_path='SQuAD2/train-v2.0.json',
                            local_file_path=os.path.join(self.local_dataset_folder_path, 'SQuAD2', 'train-v2.0.json'))
            self.fetch_file(s3_file_path='SQuAD2/dev-v2.0.json',
                            local_file_path=os.path.join(self.local_dataset_folder_path, 'SQuAD2', 'dev-v2.0.json'))


class QAngarooDSDatasetFetcher(AbstractDatasetFetcher, SmartDatasetFetcher):
    def __init__(self, bucket_name='dataset-store', local_dataset_folder_path='~/project/data'):
        """

        Args:
            bucket_name (str):
            local_dataset_folder_path (str):
        """
        SmartDatasetFetcher.__init__(self, bucket_name, local_dataset_folder_path)

    def fetch_dataset(self, protect_local_folder=True):
        """

        Args:
            protect_local_folder (bool):

        Returns:
            None

        """
        if not self.exists_local_dataset_folder('qangaroo_v1', protect_local_folder):
            self.fetch_file(s3_file_path='qangaroo_v1/medhop.zip',
                            local_file_path=os.path.join(self.local_dataset_folder_path, 'qangaroo_v1', 'medhop.zip'))
            self.fetch_file(s3_file_path='qangaroo_v1/wikihop.zip',
                            local_file_path=os.path.join(self.local_dataset_folder_path, 'qangaroo_v1', 'wikihop.zip'))


class CNNDailyMailDSDatasetFetcher(AbstractDatasetFetcher, SmartDatasetFetcher):
    def __init__(self, bucket_name='dataset-store', local_dataset_folder_path='~/project/data'):
        """

        Args:
            bucket_name (str):
            local_dataset_folder_path (str):
        """
        SmartDatasetFetcher.__init__(self, bucket_name, local_dataset_folder_path)
        self.available_prepocessed_datasets = ['abisee', 'danqi']

    def fetch_dataset(self, protect_local_folder=True):
        """

        Args:
            protect_local_folder (bool):

        Returns:
            None

        """
        raise NotImplementedError('Currently the original CNN/DailyMail dataset is not stored on S3. '
                                  'Rather use one of the preprocessed datasets.')

    def fetch_preprocessed_dataset(self, preprocess_name, protect_local_folder=True):
        """

        Args:
            preprocess_name (str):
            protect_local_folder (bool):

        Returns:
            None

        """
        if not self.preproc_dataset_available(preprocess_name):
            raise ValueError('Preprocessing name not available. Select: abisee / danqi')

        if not self.exists_local_dataset_folder('cnn_dailymail', protect_local_folder):

            if preprocess_name == 'abisee':
                self.fetch_file(s3_file_path='cnn-dailymail/preproc/abisee/cnn_stories_tokenized.zip',
                                local_file_path=os.path.join(self.local_dataset_folder_path, 'cnn_dailymail', 'cnn_stories_tokenized.zip'))
                self.fetch_file(s3_file_path='cnn-dailymail/preproc/abisee/dm_stories_tokenized.zip',
                                local_file_path=os.path.join(self.local_dataset_folder_path, 'cnn_dailymail', 'dm_stories_tokenized.zip'))

                # TODO: add unzip

            elif preprocess_name == 'danqi':
                self.fetch_file(s3_file_path='cnn-dailymail/preproc/danqi/cnn.tar.gz',
                                local_file_path=os.path.join(self.local_dataset_folder_path, 'cnn_dailymail', 'cnn.tar.gz'))
                self.fetch_file(s3_file_path='cnn-dailymail/preproc/danqi/dailymail.tar.gz',
                                local_file_path=os.path.join(self.local_dataset_folder_path, 'cnn_dailymail', 'dailymail.tar.gz'))

                # TODO: add unzip
