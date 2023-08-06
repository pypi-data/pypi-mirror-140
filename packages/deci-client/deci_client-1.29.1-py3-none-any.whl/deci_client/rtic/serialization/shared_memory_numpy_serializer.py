"""
A class for numpy arrays serialization and deserialization over the sharec memory of the host OS.
The shared arrays are transferable between processes and containers on the same OS.
"""
from os import chmod
from typing import Union, List

from deci_client.rtic.serialization.numpy_serializer import AbstractSerializer

try:
    import multiprocessing.shared_memory
except ImportError:
    raise EnvironmentError('Please use Python in version 3.8 or later to enable shared memory usage.')

import numpy as np

TENSOR_FILENAME_DELIMITER = '_'
SHAPE_DELIMITER = '-'
TENSORS_NAMES_DELIMITER = ','
DECI_SHARED_MEMORY_MAX_INPUTS_PER_REQUEST = 1000


class SharedMemoryNumpySerializer(AbstractSerializer):
    """
    Serialized python numpy arrays into SharedMemory blocks.
    Each serialized numpy array has it's unique identifier.
    The numpy array(s) are stored in the following method:
        1. The data (tensor) region is communicated over a shared memory block - and it includes the numpy tensor.
        2. The metadata (dtype, tuple, input identifier, etc) is stored in a SharedList that holds a tuple of all the metadata we need.
    """

    @staticmethod
    def serialize(obj: Union[np.ndarray, List[np.ndarray]], request_transaction_id: str = None) -> str:
        """
        Serializes numpy array(s) by uploading them to the shared memory.
        """
        # To enable the same signature, checking the request_transaction_id here.
        assert request_transaction_id is not None, 'A shared memory name must be provided - Got None instead. Please specify a valid and short transaction id.'
        # assert TENSOR_FILENAME_DELIMITER not in request_transaction_id, f'Shared memory transaction ID cannot contain "{TENSOR_FILENAME_DELIMITER}"'

        # Writing the output tensor to a buffer using the same shared resource name.
        shared_outputs_names = []
        if obj is None:
            print('The model output is None.')
            return

        if isinstance(obj, np.ndarray):
            obj = [obj]

        for output_count, output in enumerate(obj):
            dtype = np.dtype(output.dtype).name
            shape = SHAPE_DELIMITER.join([str(d) for d in output.shape])
            data_name = TENSOR_FILENAME_DELIMITER.join([request_transaction_id, str(output_count)])
            metadata_name = data_name + '_metadata'

            # Cleaning up old shared memory blocks with the same name
            for shared_name in [data_name, metadata_name]:
                try:
                    existing_shared_block = multiprocessing.shared_memory.SharedMemory(shared_name,
                                                                                       create=False)
                    print(f'Found existing shared memory block with name "{shared_name}", unlinking.')
                    existing_shared_block.unlink()
                except:
                    continue

            # Creating a shareable list with the metadata of the current tensor.
            shared_metadata = multiprocessing.shared_memory.ShareableList(
                [request_transaction_id, output_count, dtype, shape], name=metadata_name)
            shared_metadata.shm.close()
            chmod(f'/dev/shm/{metadata_name}', 0o777)

            # Creating the shared memory buffer
            shared_output = multiprocessing.shared_memory.SharedMemory(data_name,
                                                                       create=True,
                                                                       size=output.nbytes)

            # Copying the buffer to the memory
            shared_np_array = np.ndarray(shape=output.shape, dtype=dtype, buffer=shared_output.buf)

            # SharedMemoryNumpySerializer.change_shm_file_ownership(output_shared_memory_name)
            shared_outputs_names.append(data_name)
            shared_np_array[:] = output

            # unlinking the pointer to release the memory from this process (but not delete it)
            # https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.shared_memory.SharedMemory
            shared_output.close()
            chmod(f'/dev/shm/{data_name}', 0o777)

        # print(f'Transaction ID: {request_transaction_id}; Created shared memory blocks: {shared_outputs_names}')
        shared_outputs_names = TENSORS_NAMES_DELIMITER.join(shared_outputs_names) or None
        return shared_outputs_names

    @staticmethod
    def deserialize(obj: str) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Deserializes the tensors from the object in the shared memory, by a given name.
        :param obj: The shared memory full paths, joined by TENSORS_NAMES_DELIMITER in this namespace.
        """

        # We need to make sure the host shared memory does not overlap (DOS).
        # There is a limit of inputs sizes for security (The IPC is shared with the Host sometimes).
        shared_memory_path = obj
        shared_array_names = shared_memory_path.split(TENSORS_NAMES_DELIMITER)
        assert DECI_SHARED_MEMORY_MAX_INPUTS_PER_REQUEST > len(
            shared_array_names), f'Exceeded the limit of inputs per IPC request: {DECI_SHARED_MEMORY_MAX_INPUTS_PER_REQUEST}'

        # Attaching each input
        tensors = []
        for tensor_name in shared_array_names:
            # Attaching the metadata
            metadata_name = tensor_name + '_metadata'

            # Parsing the fields of the tensor from the metadata
            shared_metadata = multiprocessing.shared_memory.ShareableList(
                name=metadata_name)
            request_transaction_id, output_count, dtype, shape = shared_metadata
            shape = tuple([int(d) for d in shape.split(SHAPE_DELIMITER)])
            dtype = np.dtype(dtype)
            shared_metadata.shm.close()

            # Binding a numpy memory to the shared memory
            shared_memory_block = multiprocessing.shared_memory.SharedMemory(tensor_name, create=False)
            numpy_tensor = np.ndarray(shape=shape, dtype=dtype)
            numpy_tensor[:] = np.ndarray(shape=shape, dtype=dtype, buffer=shared_memory_block.buf)
            shared_memory_block.close()
            tensors.append(numpy_tensor)
        # Correcting the array input - single input will pass the model a single np.ndarray instead of a list
        if len(tensors) == 1:
            tensors = tensors[0]
        return tensors

    @staticmethod
    def cleanup_transaction_from_shared_memory(request_transaction_id: str):
        tensor_name = request_transaction_id
        metadata_name = tensor_name + '_metadata'

        # Unlinking
        multiprocessing.shared_memory.SharedMemory(request_transaction_id).unlink()
        multiprocessing.shared_memory.SharedMemory(metadata_name).unlink()

    @staticmethod
    def is_ipc_supported():
        try:
            from multiprocessing import shared_memory
            return True
        except ImportError:
            return False
