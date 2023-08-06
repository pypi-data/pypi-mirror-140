from __future__ import print_function

import hashlib
import struct
import sys
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from multiprocessing import cpu_count
from time import time
from uuid import uuid4

import grpc
import numpy as np
import pyarrow
import requests
import urllib3

from deci_client.rtic import InferencerApi, DefaultApi
from deci_client.rtic import __version__ as RTIC_CLIENT_VERSION
from deci_client.rtic.api_client import ApiClient
from deci_client.rtic.configuration import Configuration
from deci_client.rtic.exceptions import ApiException
from deci_client.rtic.serialization.protobuf.rtic_server_pb2_grpc import RTiCStub
from deci_client.rtic.serialization.protobuf_serializer import NumpyProtobufSerializer
from deci_client.rtic.serialization.shared_memory_numpy_serializer import SharedMemoryNumpySerializer, TENSORS_NAMES_DELIMITER

BENCHMARK_TRANSPORT_ITERATIONS = 300
BENCHMARK_TRANSPORT_WARMUP_CALLS = 300
BENCHMARK_TRANSPORT_DEFAULT_BATCH_SIZES = [1, 4, 8, 16, 32, 64]
CPU_COUNT = cpu_count()


class BenchmarkMode(str, Enum):
    THROUGHPUT = 'throughput'
    LATENCY = 'latency'


def get_docstring_from(original_function):
    """
    A decorator that attaches the docstring one function to another function in real time (for transparent auto completion).
    """

    def doc_wrapper(target):
        target.__doc__ = original_function.__doc__
        return target

    return doc_wrapper


def md5(value):
    encoded_utf_8_val = value.encode('utf-8')
    h = hashlib.md5(encoded_utf_8_val).hexdigest()
    return h[:8]


def get_random_input_tensor(batch_size: int, dummy_input_dims: tuple):
    """
    Returns a float32 numpy.ndarray with random values.
    """
    dummy_batch = np.random.rand(batch_size, *dummy_input_dims)
    dummy_batch = dummy_batch.astype(np.float32)
    return dummy_batch


class InferenceResponse(object):
    def __init__(self, model_forward_pass_time_ms, server_process_time_ms, data):
        """
        An inference response.
        :param model_forward_pass_time_ms: The time it took for the model forward pass.
        :type model_forward_pass_time_ms: str
        :param server_process_time_ms: The time it took for the http server to process, analyze and return the response (EXCLUDING network latency).
        :type server_process_time_ms: str
        :param data: A list of the model outputs.
        :type data: list
        """
        self.model_forward_pass_time_ms = model_forward_pass_time_ms
        self.server_process_time_ms = server_process_time_ms
        self.data = data


class DeciRTICClient:
    """
    A wrapper for OpenAPI's generated client http library to deci's API.
    Extends the functionality of generated clients and eases their use.
    """

    def __init__(self, api_host='localhost', api_port=8000, grpc_port=8001, https=False, max_workers=None,
                 shared_tensor_provider=None):
        """
        :param api_host: The host of deci's inferencer HTTP API.
        :type api_host: str
        :param api_host: The port of deci's inferencer HTTP API.
        :type api_port: int
        :param https: Whether to use https instead of HTTP. Using https Will add latency.
        :type https: bool
        :param max_workers: The maximum amount of workers for the predict thread pool.
                            Larger numbers will allow more asynchronous predict requests to be sent to the server.
                            The requests are queued, and by that we to reduce network latency and keep the GPUs closer 100% capacity.
        """
        assert isinstance(api_port, int), 'The api_port must be an int object'
        endpoint_host = '{api_host}:{api_port}'.format(api_host=api_host, api_port=api_port)
        self._api_host = api_host
        self._endpoint_host = endpoint_host
        if https:
            base_url = 'https://{endpoint}'.format(endpoint=endpoint_host)
        else:
            base_url = 'http://{endpoint}'.format(endpoint=endpoint_host)

        self._base_url = base_url
        client_config = ApiClient(configuration=Configuration(host=base_url))
        self.__api = InferencerApi(client_config)

        # Checking the client version
        self._assert_server_version(client_config)
        self._inference_session = requests.Session()

        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)

        # IPC Shared Memory tensors for predict async thread safety
        self._thread_pool_size = self._thread_pool._max_workers
        self._shared_tensors_provider: SharedMemoryNumpySerializer = shared_tensor_provider or SharedMemoryNumpySerializer

        # GRPC Initialization
        max_message_size = 2 ** (struct.Struct('i').size * 8 - 1) - 1
        channel_options = [('grpc.max_receive_message_length',
                            max_message_size),
                           ('grpc.max_send_message_length', max_message_size)]
        channel = grpc.insecure_channel(f'{api_host}:{grpc_port}', options=channel_options)
        stub = RTiCStub(channel)
        self._grpc_stub = stub

        # A cache for the chosen transport for inference (str), per model name (str, key);
        self._transport_mapping = {}

        # A dictionary that holds a method for inference (predict), per transport type (key).
        self._transport_inference_methods = {'http': self._run_predict_http,
                                             'ipc': self._run_predict_ipc,
                                             'grpc': self._run_predict_grpc}

    @get_docstring_from(DefaultApi().get_rtic_version_version_get)
    def _assert_server_version(self, client_config):
        """
        Checks the server version.
        If the server version is not compatible with the current client version, a warning will be logged.
        Major verisons are not backwards-compatible, and Minor versions are backwards-compatible for the same Major version.
        For instance, if the server version is 0.1.3 and the client version is v0.1.1, they are compatible.
        For instance, if the server version is 1.0.0 and the client version is 0.9.8, they are compatible.
        """
        try:
            rtic_version = DefaultApi(client_config).get_rtic_version_version_get().data
            rtic_major = rtic_version.split('.')[0]
            client_major = RTIC_CLIENT_VERSION.split('.')[0]
            supported_client_versions = '{0}.x.x'.format(rtic_major)
            if rtic_major != client_major:
                print(RuntimeWarning(
                    'The RTiC Server API Version: {rtic_version} is not compatible with the current client version: {RTIC_CLIENT_VERSION}. Please use a matching client version ({supported_client_versions}, prefferbly {rtic_version}) in order to experience consistent results.'.format(
                        rtic_version=rtic_version, RTIC_CLIENT_VERSION=RTIC_CLIENT_VERSION,
                        supported_client_versions=supported_client_versions
                    )))
        except urllib3.exceptions.HTTPError as e:
            print(RuntimeWarning(
                'The RTiC Server is not running, or it is unreachable: {base_url}: {e}'.format(base_url=self._base_url,
                                                                                               e=e)))

    @get_docstring_from(InferencerApi().register_model)
    def register_model(self,
                       model_name,
                       framework_type,
                       inference_hardware,
                       model_weights_source,
                       weights_path,
                       tensorflow_input_layer_name='',
                       tensorflow_output_layer_name='',
                       transport='http',
                       **kwargs):
        """

        :param model_name: The name to give to the model.
        :type model_name: str
        :param framework_type: The framework type. To find which frameworks are supported on your inferencer, Please visit it's live documentation via http://<inference_host>:<inference_port>/redoc .
        :type framework_type: str
        :param inference_hardware: The Inference Hardware.
        :type framework_type: str
        :param model_weights_source: The source of the model weights.
        :type model_weights_source: str
        :param weights_path: The path (or link) to the weights.
        :type weights_path: str
        :param tensorflow_input_layer_name: The input layer name in tensorflow. Must be speficied only when using tensorflow as framework type. Must be None otherwise.
        :type tensorflow_input_layer_name: str
        :param tensorflow_output_layer_name: The output layer name in tensorflow. Must be speficied only when using tensorflow as framework type. Must be None otherwise.
        :type tensorflow_output_layer_name: str
        :param transport: The transport protocol that will be used for inference. For non-localhost deployments, The default is IPC. Otherwise the default is HTTP. Consider using IPC (Inner-Process-Communication using shared memory) for big batch sizes, to prevent network (TCP) overhead.
        :type transport: str
        :return: APIResponse
        :raises ApiException: If anything went wrong during the model registration.
        """
        if transport == 'ipc':
            if not self._shared_tensors_provider.is_ipc_supported():
                print(
                    'IPC transport will probably not work, because /dev/shm is not readable/writabl, or because '
                    'shared memory is not available programmatically.')
        response = self.__api.register_model(model_name=model_name,
                                             framework_type=framework_type,
                                             inference_hardware=inference_hardware,
                                             model_weights_source=model_weights_source,
                                             weights_path=weights_path,
                                             tensorflow_input_layer_name=tensorflow_input_layer_name,
                                             tensorflow_output_layer_name=tensorflow_output_layer_name,
                                             transport=transport,
                                             **kwargs)

        return response

    @get_docstring_from(InferencerApi().register_model_from_repository)
    def register_model_from_repository(self,
                                       model_name,
                                       model_id,
                                       **kwargs):
        response = self.__api.register_model_from_repository(model_id=model_id,
                                                             model_name=model_name,
                                                             **kwargs)
        return response

    @get_docstring_from(InferencerApi().de_register_model)
    def deregister_model(self, model_name, **kwargs):
        return self.__api.de_register_model(model_name=model_name, **kwargs)

    @get_docstring_from(InferencerApi().list_registered_models)
    def get_all_models(self, **kwargs):
        return self.__api.list_registered_models(**kwargs)

    @get_docstring_from(InferencerApi().get_model)
    def get_model(self, model_name, **kwargs):
        return self.__api.get_model(model_name=model_name, **kwargs)

    @get_docstring_from(InferencerApi().measure)
    def measure(self, model_name, batch_size, input_dims, **kwargs):
        return self.__api.measure(model_name=model_name, batch_size=batch_size,
                                  input_dims=input_dims, **kwargs)

    def _run_predict_http(self, predict_endpoint_url, model_input, headers, **kwargs) -> InferenceResponse:
        try:
            # serialized_input = ClientNumpySerializer.serialize(model_input)
            # serialized_input = pyarrow.serialize(model_input).to_buffer()
            serialized_input = memoryview(
                pyarrow.serialize(model_input).to_buffer(nthreads=CPU_COUNT)).tobytes()  # LEADER
            http_response = self._inference_session.post(predict_endpoint_url,
                                                         headers=headers,
                                                         data=serialized_input)
            http_response.raise_for_status()
            model_output = pyarrow.deserialize(http_response.content)  # LEADER
            # model_output = ClientNumpySerializer.deserialize(http_response.content)
            server_process_time_ms = http_response.headers['deci-server-process-time-ms']
            model_forward_pass_time_ms = http_response.headers['model-forward-pass-time-ms']
            inference_response = InferenceResponse(data=model_output,
                                                   model_forward_pass_time_ms=model_forward_pass_time_ms,
                                                   server_process_time_ms=server_process_time_ms)
            return inference_response
        except struct.error:
            # Numpy De-Serialization failed, therefore, the server sent a json response.
            print('Failed to deserialize output array - decoding as JSON')
            model_output = http_response.json()
            raise ApiException(status=http_response.status_code,
                               reason=model_output['message'],
                               http_resp=http_response)
        except requests.HTTPError:
            # Other HTTP Error codes (400, 404, 422, 500):
            # Converting the request response to ApiException (should be raised by the original unwrapped predict() function).
            raise ApiException(status=http_response.status_code, reason=http_response.reason, http_resp=http_response)

    def _run_predict_ipc(self, predict_endpoint_url, model_name, model_input, headers, **kwargs) -> InferenceResponse:
        shared_input_tensors_paths = None
        shared_output_tensors_paths = None
        try:
            if sys.platform == 'darwin':
                print('[WARNING] - IPC is not officially supported on Mac OS clients.')

            transaction_id = str(uuid4())[:8]
            # Uploads the tensors to the shared memory
            shared_inputs_names = SharedMemoryNumpySerializer.serialize(model_input,
                                                                        request_transaction_id=transaction_id)
            shared_input_tensors_paths = shared_inputs_names.split(TENSORS_NAMES_DELIMITER)
            headers['x-shared-memory-path'] = shared_inputs_names

            # Running the http call with the shared tensors paths in the headers.
            http_response = self._inference_session.post(predict_endpoint_url,
                                                         headers=headers,
                                                         data=None)
            http_response.raise_for_status()

            # Getting the shared memory tensors names from the HTTP response header
            shared_outputs_names: str = http_response.headers.get('x-shared-memory-path')
            shared_output_tensors_paths = shared_outputs_names.split(TENSORS_NAMES_DELIMITER)
            model_outputs = SharedMemoryNumpySerializer.deserialize(shared_outputs_names)

            # Creating the response model
            server_process_time_ms = http_response.headers['deci-server-process-time-ms']
            model_forward_pass_time_ms = http_response.headers['model-forward-pass-time-ms']
            inference_response = InferenceResponse(data=model_outputs,
                                                   model_forward_pass_time_ms=model_forward_pass_time_ms,
                                                   server_process_time_ms=server_process_time_ms)
            return inference_response
        except requests.HTTPError:
            # Other HTTP Error codes (400, 404, 422, 500):
            # Converting the request response to ApiException (should be raised by the original unwrapped predict() function).
            raise ApiException(status=http_response.status_code, reason=http_response.reason, http_resp=http_response)
        finally:
            for _shared_tensors in [shared_input_tensors_paths, shared_output_tensors_paths]:
                if _shared_tensors is not None:
                    [SharedMemoryNumpySerializer.cleanup_transaction_from_shared_memory(p) for p in _shared_tensors]

    def _run_predict_grpc(self, model_name, model_input, **kwargs) -> InferenceResponse:
        predict_request = NumpyProtobufSerializer.serialize_request(model_name=model_name,
                                                                    inputs=model_input)
        grpc_response = self._grpc_stub.predict(predict_request)
        model_output = NumpyProtobufSerializer.deserialize_from_response(message=grpc_response)
        model_forward_pass_time_ms = str(grpc_response.model_forward_pass_time_ms)
        server_process_time_ms = str(grpc_response.server_process_time_ms)
        inference_response = InferenceResponse(data=model_output,
                                               model_forward_pass_time_ms=model_forward_pass_time_ms,
                                               server_process_time_ms=server_process_time_ms)
        return inference_response

    def predict(self, model_name,
                model_input,
                transport=None,
                api_version='v1',
                **kwargs):
        """
        Predict - Performs inference on a loaded model with a given name.
        Predict - Classify (Infer) input tensors. The input is serialized and sent in different serializers/protocols, depending on the transport.
         Please use this endpoint for maximum results.
        :param model_name: The unique name of the model, that was specified in "register" api call.
        :type model_name: str
        :param model_input: In the shape of the model's input layer. For example, a numpy ndarray with shape (1, 3, 224, 224).
        :type model_input: np.ndarray
        :param transport: The transport protocol that will be used for inference. For non-localhost deployments, The default is IPC. Otherwise the default is HTTP. Consider using IPC (Inner-Process-Communication using shared memory) for big batch sizes, to prevent network (TCP) overhead.
        :type transport: str
        :param api_version: The api version to use.
        :raises ApiError: If the predict API Failed for any reason.
        """
        if not isinstance(model_input, np.ndarray):
            raise ValueError('Error - Model input must be a numpy ndarray')

        transport = self._choose_transport_protocol(model_name, transport)
        predict_endpoint_url = self.__api.api_client.configuration.host + '/{api_version}/predict/{model_name}'.format(
            api_version=api_version, model_name=model_name)
        headers = {'x-deci-transport': transport}

        # Invoking the inference request, depending on the pre-defined transport
        predict_method = self._transport_inference_methods.get(transport)
        if not predict_method:
            raise ValueError('Unsupported transport: {}'.format(transport))

        # Passing keyword arguments to the functions, to every function can define arguments that it really uses.
        inference_response = predict_method(predict_endpoint_url=predict_endpoint_url,
                                            model_name=model_name,
                                            model_input=model_input,
                                            headers=headers)
        return inference_response

    def _choose_transport_protocol(self, model_name, transport):
        """
        Assigns the DataTransportProtocol - If self._api_host is localhost, assigns IPC as default.
        :param transport: The pre-defined DataTransportProtocol Protocol
        :type transport: str
        :return:
        """
        if transport is None:
            if self._api_host in ['localhost', '127.0.0.1', '0.0.0.0']:
                transport = 'ipc'
            else:
                transport = self._transport_mapping.get(model_name)
                if not transport:
                    # Getting the transport from the model registration,
                    # and caching it as default when 'transport' is not specified.
                    model_metadata = self.get_model(model_name=model_name)
                    transport = model_metadata.data.transport
                    self._transport_mapping[model_name] = transport
        return transport

    def predict_async(self, model_name, model_input, transport=None, api_version='v1'):
        """
        Preforms a predict operation using async event loop, for concurrent execution.
        Classify (Infer) input tensors asynchronously. The HTTP request body sends the input tensor, serialized with deci's custom serialization.
        Please use this endpoint when working with asyncio, python3 async/await or other concurrent client libraries.

        :param model_name: The unique name of the model, that was specified in "register" api call.
        :type model_name: str
        :param model_input: A np.ndarray In the shape of the model's input layer. For example, a numpy ndarray with shape (1, 3, 224, 224).
        :type model_input: np.ndarray
        :param transport: The transport protocol that will be used for inference. For non-localhost deployments, The default is IPC. Otherwise the default is HTTP. Consider using IPC (Inner-Process-Communication using shared memory) for big batch sizes, to prevent network (TCP) overhead.
        :type transport: str
        :param api_version: The api version to use.
        :type api_version: str

        :returns: A concurrent.Future object of with the predict() operation. The result of the Future is an InferenceResponse object.
        :trype: InferenceResponse
        :example:
        >>> predict_job = client.predict_async(model_name='my_model', model_input=np.ones((3,224,224), dtype=np.float32, **kwargs)
        >>> prediction = predict_job.result(timeout=5)
        """
        predict_job = self._thread_pool.submit(self.predict,
                                               model_name=model_name,
                                               model_input=model_input,
                                               transport=transport,
                                               api_version=api_version)

        return predict_job

    @get_docstring_from(InferencerApi().set_platform_api_key)
    def set_platform_api_key(self, api_key):
        response = self.__api.set_platform_api_key(token=api_key)
        return response

    def benchmark_model_transports(self, model_name: str, input_dims: tuple, mode: BenchmarkMode, **kwargs):
        """
        Runs end to end benchmarks on the speficied model in the specified inference mode.
        :param model_name: The name of the loaded model in RTiC
        :type model_name: str
        :param input_dims: The input dimensions of the input tensors, that will be used during benchmarks.
        :type input_dims: tuple
        :param mode: The kind of benchmark to perform.
                     "Latency" will measure SYNCHRONOUS inference, to find the parameters with lowest latency.
                     "Throughput" will measure ASYNCHRONOUS inference to find the parameters with highest throughput.
        :type mode: BenchmarkMode
        """
        try:
            mode = BenchmarkMode(mode)
        except Exception as e:
            raise ValueError(f"Invalid Mode: {mode}; valid values are: 'throughput','latency'")

        if mode == BenchmarkMode.THROUGHPUT:
            run_async = True
        elif mode == BenchmarkMode.LATENCY:
            run_async = False
        else:
            raise NotImplementedError(f"Non implemented mode: {mode}; valid values are: 'throughput','latency'")

        transports_throughputs = {}

        # TODO: Use the transport enum and enulerate it's values into a list, instead of hard-coded like this
        for transport in ['http', 'ipc', 'grpc']:
            print(f'--- Benchmarking via {transport} ---')
            throughputs = self._benchmark_rtic_deployed_model_throughput(
                model_name=model_name,
                transport=transport,
                run_async_predict=run_async,
                input_dims=input_dims,
                **kwargs)
            print(f'--- DONE: {transport} ---')
            transports_throughputs[transport] = throughputs
        return transports_throughputs

    def _benchmark_rtic_deployed_model_throughput(
            self,
            model_name: str,
            transport: str,
            run_async_predict: bool,
            input_dims: tuple,

            # Optional
            iterations=BENCHMARK_TRANSPORT_ITERATIONS,
            warmup_calls=BENCHMARK_TRANSPORT_WARMUP_CALLS,
            batch_sizes=None,
    ):
        """
        benchmarks the RTiC server End-to-End over the specified transport (communication protocol).

        """
        batch_sizes = batch_sizes or BENCHMARK_TRANSPORT_DEFAULT_BATCH_SIZES
        throughputs = {}
        for batch_size in batch_sizes:
            # Defining the results
            warmup_results = []
            results = []
            async_results = []

            warmup_input = get_random_input_tensor(batch_size, input_dims)
            for i in range(warmup_calls):
                warmup_results.append(self.predict_async(model_name,
                                                         warmup_input,
                                                         transport=transport))

            # Computing the async results without assigning value
            [res.result() for res in warmup_results]

            # Preparing the inputs ahead
            inputs = [get_random_input_tensor(batch_size, input_dims)] * iterations

            # Starting the E2E benchmarks
            print("Benchmarking {} times using batch size {} over {}...".format(iterations, batch_size, transport))
            batch_size_e2e_start_time = time()
            for _input in inputs:
                if run_async_predict:
                    async_results.append(self.predict_async(model_name,
                                                            _input,
                                                            transport=transport))
                else:
                    _ = self.predict(model_name,
                                     _input,
                                     transport=transport)

            if run_async_predict:
                _ = [res.result() for res in async_results]

            # Computing the benchmarks
            batch_size_e2e_end_time = time()
            e2e_batch_size_time_ms = (batch_size_e2e_end_time - batch_size_e2e_start_time) * 1000
            sample_latency = (e2e_batch_size_time_ms / iterations / batch_size)
            if run_async_predict:
                throughput = 1000 / sample_latency
                print("Throughput: ", throughput)
                throughputs[batch_size] = throughput
            else:
                print("Latency: ", sample_latency)
                throughputs[batch_size] = sample_latency
        return throughputs

    def plot_model_e2e_benchmarks(self, model_name: str, input_dims: tuple,
                                  mode: BenchmarkMode = BenchmarkMode.THROUGHPUT,
                                  **kwargs):
        """
        Benchmarks the E2E latency of the model over different transport protocols and plots the result using matplotlib.
        The graph can be used to determine the best parameters for production.

        :param model_name: The name of the loaded model in RTiC
        :type model_name: str
        :param input_dims: The input dimensions of the input tensors, that will be used during benchmarks.
        :type input_dims: tuple
        :param mode: The kind of benchmark to perform.
                     "Latency" will measure SYNCHRONOUS inference, to find the parameters with lowest latency.
                     "Throughput" will measure ASYNCHRONOUS inference to find the parameters with highest throughput.
        :type mode: BenchmarkMode
        """
        mode = BenchmarkMode(mode)
        e2e_latency_benchmarks = self.benchmark_model_transports(model_name=model_name,
                                                                 input_dims=input_dims,
                                                                 mode=mode,
                                                                 **kwargs)

        try:
            import pandas as pd
        except:
            raise ImportError("pandas is required for plotting.")

        try:
            import matplotlib.pyplot as plt
        except:
            raise ImportError("matplotlib is required for plotting.")

        e2e_latency_benchmarks_df = pd.DataFrame(e2e_latency_benchmarks)
        e2e_latency_benchmarks_df.plot(kind='bar', ylabel=mode, xlabel='Transport & Batch Size',
                                       title=f'{model_name} end-to-end benchmarks for mode {mode}')
        plt.show()
