# Copyright Exafunction, Inc.

"""Client for the Exafunction module repository."""

import base64
import hashlib
import io
import os
import pathlib
import stat
import tempfile
from typing import BinaryIO, Dict, List, Optional, Set, Tuple
import zipfile

import grpc

import exa
from exa.module_repository_pb import module_repository_pb2
from exa.module_repository_pb import module_repository_pb2_grpc

RUNNER_IMAGE_TAG_NAME = "exafunction_runner_image"
REGISTER_BLOB_CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB
GET_ALL_TAGS_WITH_OBJECT_IDS_LIMIT = 1000


class ModuleRepository:
    """Client for the Exafunction module repository."""

    def __init__(self, repository_address):
        """
        Creates a connection to the Exafunction module repository.

        :param repository_address: The address of the module repository.
        """
        self.channel = grpc.insecure_channel(repository_address)
        self.stub = module_repository_pb2_grpc.ModuleRepositoryStub(self.channel)
        self._default_runner_image_id = None
        self._ignore_runner_image = False

    def __enter__(self):
        return self

    def close(self):
        """Closes the connection to the module repository."""
        self.channel.close()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def set_default_runner_image(self, runner_image):
        """
        Sets the default runner image for future module registrations by this object.

        :param runner_image: The runner image to use for future module registrations.
        """
        runner_image_id = self._id_from_tag_or_id(runner_image)
        if not self.object_id_exists(runner_image_id):
            raise ValueError(f"Invalid ID {runner_image_id} passed for runner_image_id")
        self._default_runner_image_id = runner_image_id

    def ignore_runner_image(self):
        """
        Allows registering modules without a runner image.

        Generally this should not be used outside of local testing.
        """
        self._ignore_runner_image = True

    def get_all_tags_with_object_ids(self) -> Dict[str, str]:
        """
        :return: A map from all tags to their corresponding object id
        """
        start_tag = ""
        tags_with_object_ids = {}
        while True:
            req = module_repository_pb2.GetAllTagsWithObjectIdsRequest()
            req.start_tag = start_tag
            req.limit = GET_ALL_TAGS_WITH_OBJECT_IDS_LIMIT
            resp = self.stub.GetAllTagsWithObjectIds(req)
            num_tags = len(resp.sorted_tags)
            if num_tags > 0:
                start_tag = resp.sorted_tags[-1]
            for tag, object_id in zip(resp.sorted_tags, resp.object_ids):
                tags_with_object_ids[tag] = object_id
            if num_tags < req.limit:
                break
        return tags_with_object_ids

    def get_object_id_from_tag(self, tag: str) -> str:
        """
        Gets an object id from a tag.

        :param tag: The tag to get the object id for
        :return: The object id
        """
        name, version = _parse_tag(tag)
        req = module_repository_pb2.GetObjectIdFromTagRequest()
        req.tag = _generate_tag(name, version)
        try:
            resp = self.stub.GetObjectIdFromTag(req)
        except grpc.RpcError as e:
            raise ValueError(f"Could not get object ID from tag {req.tag}") from e

        return resp.object_id

    def add_tag(self, tag: str, object_id: str) -> None:
        """
        Adds or overwrites a tag to point to an object id.

        :param tag: The tag to add or overwrite
        :param object_id: The object id that the tag should point to
        """
        name, version = _parse_tag(tag)
        if not object_id.startswith("@"):
            raise ValueError(f"Invalid object id {object_id}")
        if not self.object_id_exists(object_id):
            raise ValueError(f"Object id {object_id} does not exist")
        add_tag_req = module_repository_pb2.AddTagForObjectIdRequest()
        add_tag_req.tag = _generate_tag(name, version)
        add_tag_req.object_id = object_id
        self.stub.AddTagForObjectId(add_tag_req)

    def tag_exists(self, tag: str) -> bool:
        """
        Returns whether a tag exists.

        :param tag: The tag to check
        :return: Whether the tag exists
        """
        name, version = _parse_tag(tag)
        req = module_repository_pb2.GetObjectIdFromTagRequest()
        req.tag = _generate_tag(name, version)
        try:
            self.stub.GetObjectIdFromTag(req)
        except grpc.RpcError:
            return False
        return True

    def object_id_exists(self, object_id):
        """
        Returns whether an object id exists.

        :param object_id: The object id to check
        :return: Whether the object id exists
        """
        req = module_repository_pb2.GetObjectMetadataRequest()
        req.object_id = object_id
        try:
            self.stub.GetObjectMetadata(req)
            return True
        except grpc.RpcError:
            return False

    def register_shared_object(
        self,
        filename: str,
        tag: Optional[str] = None,
        so_name: Optional[str] = None,
    ) -> str:
        """
        Registers a shared object.

        :param filename: The filename of the shared object
        :param tag: Optional; the tag to use for the shared object
        :param so_name: Optional; the SONAME to use for the shared object
        :return: The object id of the shared object
        """
        metadata = module_repository_pb2.Metadata()

        if so_name is None:
            so_name = os.path.basename(filename)
        metadata.shared_object.so_name = so_name

        with open(filename, "rb") as f:
            data = f.read()

        blob_id = self._register_blob(data)
        metadata.shared_object.blob_id = blob_id

        return self._register_object(metadata, tag)

    def register_module_plugin(
        self,
        shared_object: str,
        tag: Optional[str] = None,
        dependent_shared_objects: Optional[List[str]] = None,
    ) -> str:
        """
        DEPRECATED: Registers a module plugin containing one or more native modules.

        Use register_hermetic_module_plugin instead.

        :param shared_object: The shared object id that contains the plugin
        :param tag: Optional; the tag to use for the plugin
        :param dependent_shared_objects: Optional; the list of shared object ids
            that the plugin depends on
        :return: The object id of the plugin
        """
        shared_object_id = self._id_from_tag_or_id(shared_object)
        if not self.object_id_exists(shared_object_id):
            raise ValueError(
                f"Invalid ID {shared_object_id} passed for shared_object_id"
            )

        metadata = module_repository_pb2.Metadata()
        metadata.module_plugin.shared_object_id = shared_object_id
        if dependent_shared_objects is not None:
            for dependent in dependent_shared_objects:
                dependent_id = self._id_from_tag_or_id(dependent)
                if not self.object_id_exists(dependent_id):
                    raise ValueError(
                        f"Invalid ID {dependent_id} passed for "
                        + "dependent_shared_object_ids"
                    )
                metadata.module_plugin.dependent_shared_object_ids.append(dependent_id)

        return self._register_object(metadata, tag)

    # pylint: disable=too-many-arguments
    def register_runfiles(
        self,
        runfiles_dir: str,
        runfiles_env_var_name: Optional[str] = None,
        glob_list: Optional[List[str]] = None,
        tag: Optional[str] = None,
    ) -> str:
        """
        Registers a directory of runfiles that may be loaded with a module
        and exposed through an environment variable.

        Can specify an optional glob list with respect to the runfiles directory.
        The format of the glob list is the one used by pathlib.Path.glob.
        The globbing can also be tested manually with exa.module_repository.glob.

        :param runfiles_dir: The path to the runfiles directory
        :param runfiles_env_var_name: Optional; the name of the environment
            variable to expose the runfiles; defaults to EXAFUNCTION_RUNFILES
        :param glob_list: Optional; the list of globs to use to filter the runfiles
        :param tag: Optional; the tag to use for the runfiles
        :return: The object id of the runfiles
        """
        metadata = module_repository_pb2.Metadata()
        runfiles_buffer = _zip_directory(runfiles_dir, glob_list=glob_list)
        blob_id = self._register_blob(runfiles_buffer)
        metadata.runfiles.blob_id = blob_id
        if runfiles_env_var_name is not None:
            metadata.runfiles.runfiles_env_var_name = runfiles_env_var_name
        return self._register_object(metadata, tag)

    def register_runner_image(
        self,
        image_hash: str,
        tag: Optional[str] = None,
    ) -> None:
        """
        Registers a Docker image for the runner.

        :param image_hash: The hash of the image
        :param tag: Optional; the tag to use for the image
        """
        metadata = module_repository_pb2.Metadata()
        metadata.runner_image.image_hash = image_hash
        return self._register_object(metadata, tag)

    # pylint: disable=too-many-arguments
    def register_hermetic_module_plugin(
        self,
        runfiles_dir: str,
        shared_object_path: str,
        tag: Optional[str] = None,
        runner_image: Optional[str] = None,
        runfiles_env_var_names: Optional[List[str]] = None,
    ) -> str:
        """
        Registers a hermetic module plugin containing one or more native
        modules.  The hermetic module plugin contains a runfiles directory
        created from a build system like Bazel.

        :param runfiles_dir: The runfiles directory containing the module plugin.
        :param shared_object_path: The shared object path.
            This path should be relative to the runfiles directory that
            implements the module plugin.
        :param tag: Optional; the tag to use for the module plugin
        :param runner_image: Optional; the runner image tag or id.
            If not specified, the default runner image is used.
        :param runfiles_env_var_names: Optional; a list of environment variables
            to to expose the runfiles; defaults to ["EXAFUNCTION_RUNFILES"]
        """

        metadata = module_repository_pb2.Metadata()
        plugin = metadata.hermetic_module_plugin

        if os.path.isabs(shared_object_path):
            raise ValueError("shared_object_path must be a relative path")
        joined_path = os.path.join(runfiles_dir, shared_object_path)
        if not os.path.exists(joined_path):
            raise ValueError(f"{joined_path} does not exist")

        plugin.shared_object_path = shared_object_path

        if runfiles_env_var_names is None:
            runfiles_env_var_names = ["EXAFUNCTION_RUNFILES"]
        assert runfiles_env_var_names is not None
        plugin.runfiles_env_var_names.extend(runfiles_env_var_names)

        if not self._ignore_runner_image:
            if runner_image is None:
                if self._default_runner_image_id is None:
                    raise ValueError(
                        "No runner image id was provided, and "
                        + "set_default_runner_image was not called"
                    )
                runner_image = self._default_runner_image_id
            assert runner_image is not None
            plugin.runner_image_id = runner_image

        runfiles_packs = self._generate_runfiles_packs(runfiles_dir)
        plugin.runfiles_packs.extend(runfiles_packs)

        return self._register_object(metadata, tag)

    def _generate_runfiles_packs(
        self, directory: str, glob_list: Optional[List[str]] = None
    ) -> List[str]:
        packs: List[module_repository_pb2.RunfilesPack] = []
        small_files: List[Tuple[pathlib.Path, int]] = []
        small_file_threshold = 262144  # 256 KiB

        for path in glob(directory, glob_list):
            if not os.path.isfile(path):
                continue
            file_size = path.stat().st_size
            if file_size <= small_file_threshold:
                small_files.append((path, file_size))
                continue

            pack = module_repository_pb2.RunfilesPack()
            pack.filenames.append(path.relative_to(directory).as_posix().encode())
            pack.offsets.append(0)
            with open(path, "rb") as f:
                pack.blob_id = self._register_blob_from_stream(f)
            packs.append(pack)

        if len(small_files) == 0:
            return packs

        pack = module_repository_pb2.RunfilesPack()
        offset = 0
        # Create a temporary file with all the small files concatenated
        with tempfile.TemporaryFile("r+b") as tmp_pack:
            for path, file_size in sorted(small_files):
                pack.filenames.append(path.relative_to(directory).as_posix().encode())
                pack.offsets.append(offset)
                offset += file_size
                with open(path, "rb") as f:
                    tmp_pack.write(f.read())
            pack.blob_id = self._register_blob_from_stream(tmp_pack)  # type: ignore

        packs.append(pack)
        return packs

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    def register_native_module(
        self,
        module_tag: str,
        module_class: str,
        context_data: bytes = bytes(),
        module_plugin: Optional[str] = None,
        shared_objects: Optional[List[str]] = None,
        runfiles: Optional[str] = None,
        hermetic_module_plugin: Optional[str] = None,
        config: Optional[Dict[str, bytes]] = None,
    ):
        """
        Registers a native (C/C++) module.

        :param module_tag: The tag to use for the module
        :param module_class: The class name of the module
        :param context_data: Optional; the module context data to use for the module
        :param module_plugin: Optional; the module plugin id that the module depends on
        :param shared_objects: Optional; the list of shared object ids that the
            module depends on
        :param runfiles: Optional; the runfiles id that the module depends on
        :param config: Optional; the module configuration to use for the module
        :return: The object id of the module
        """

        module_name, _ = _parse_tag(module_tag)

        metadata = module_repository_pb2.Metadata()
        metadata.module.module_name = module_name
        metadata.module.module_class = module_class
        if module_plugin:
            module_plugin_id = self._id_from_tag_or_id(module_plugin)
            if not self.object_id_exists(module_plugin_id):
                raise ValueError(
                    f"Invalid ID {module_plugin_id} passed for module_plugin_id"
                )
            metadata.module.module_plugin_id = module_plugin_id
        if shared_objects is not None:
            for shared_object in shared_objects:
                shared_object_id = self._id_from_tag_or_id(shared_object)
                if not self.object_id_exists(shared_object_id):
                    raise ValueError(
                        f"Invalid ID {shared_object_id} passed for shared_object_id"
                    )
                metadata.module.shared_object_ids.append(shared_object_id)
        if runfiles is not None:
            runfiles_id = self._id_from_tag_or_id(runfiles)
            if not self.object_id_exists(runfiles_id):
                raise ValueError(f"Invalid ID {runfiles_id} passed for runfiles_id")
            metadata.module.runfiles_id = runfiles_id
        if hermetic_module_plugin is not None:
            if module_plugin is not None:
                raise ValueError(
                    "If hermetic_module_plugin is set, module_plugin should not be set"
                )
            if runfiles is not None:
                raise ValueError(
                    "If hermetic_module_plugin is set, runfiles should not be set"
                )
            hermetic_module_plugin_id = self._id_from_tag_or_id(hermetic_module_plugin)
            if not self.object_id_exists(hermetic_module_plugin_id):
                raise ValueError(
                    f"Invalid ID {hermetic_module_plugin_id} passed for hermetic_module_plugin_id"
                )
            metadata.module.hermetic_module_plugin_id = hermetic_module_plugin_id

        if config is not None:
            metadata.module.config.update(config)

        blob_id = self._register_blob(context_data)
        metadata.module.blob_id = blob_id

        return self._register_object(metadata, module_tag)

    # pylint: disable=too-many-arguments
    def register_py_module(
        self,
        module_tag: str,
        module_class: str,
        module_import: str,
        module_context_class: str = "BaseModuleContext",
        module_context_import: str = "exa",
        context_data: bytes = bytes(),
        config: Optional[Dict[str, bytes]] = None,
        **kwargs,
    ) -> str:
        """
        Registers a Python module.

        For internal use only.
        """

        full_config = {
            "_py_module_type": b"builtin",
            "_py_module_context_import": module_context_import.encode(),
            "_py_module_context_class": module_context_class.encode(),
            "_py_module_import": module_import.encode(),
            "_py_module_class": module_class.encode(),
        }

        if config is not None:
            for k, v in config.items():
                if k in full_config:
                    raise ValueError(
                        f"Configuration key {k} is not allowed in register_py_module"
                    )
                full_config[k] = v

        return self.register_native_module(
            module_tag,
            "PyModule",
            context_data=context_data,
            config=full_config,
            **kwargs,
        )

    # pylint: disable=too-many-arguments
    def register_tf_savedmodel(
        self,
        module_tag: str,
        savedmodel_dir: str,
        use_tensorflow_cc: bool = True,
        signature: Optional[str] = None,
        tags: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Registers a TensorFlow SavedModel.

        :param module_tag: The tag to use for the module
        :param savedmodel_dir: The directory containing the TensorFlow SavedModel
        :param use_tensorflow_cc: Whether to use the C++ TensorFlow implementation
        :param signature: Optional; the SavedModel serving signature to use
        :param tags: Optional; the set of SavedModel serving tags to use
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        savedmodel_buffer = _zip_directory(savedmodel_dir)

        config = {}
        if signature is not None:
            config["_tf_signature"] = signature.encode()
        if tags is not None:
            config["_tf_tags"] = tags.encode()

        if not use_tensorflow_cc:
            raise ValueError("use_tensorflow_cc must be set to True")
        return self.register_native_module(
            module_tag,
            "TensorFlowModule",
            context_data=savedmodel_buffer,
            config=config,
            **kwargs,
        )

    def register_torchscript(
        self,
        module_tag: str,
        torchscript_file: str,
        input_names: List[str],
        output_names: List[str],
        **kwargs,
    ) -> str:
        """
        Registers a TorchScript model.

        :param module_tag: The tag to use for the module
        :param torchscript_file: The file containing the TorchScript model
        :param input_names: The names of the input tensors. Must match the
            TorchScript model.
        :param output_names: The names of the output tensors. Must match the
            TorchScript model.
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        if any("," in x for x in input_names):
            raise ValueError("TorchScript input names may not contain commas")
        if any("," in x for x in output_names):
            raise ValueError("TorchScript output names may not contain commas")

        config = {
            "_torchscript_input_names": ",".join(input_names).encode(),
            "_torchscript_output_names": ",".join(output_names).encode(),
        }

        with open(torchscript_file, "rb") as f:
            data = f.read()

        return self.register_py_module(
            module_tag,
            "TorchModule",
            "exa.py_torch_module",
            "TorchModuleContext",
            "exa.py_torch_module",
            context_data=data,
            config=config,
            **kwargs,
        )

    def register_tensorrt_engine(
        self,
        module_tag: str,
        engine_path: str,
        plugin_v1_factory_symbol: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Registers a serialized TensorRT engine.

        :param module_tag: The tag to use for the module
        :param engine_path: The path to the serialized TensorRT engine
        :param plugin_v1_factory_symbol: Optional; the symbol of the plugin
            factory function
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        with open(engine_path, "rb") as f:
            data = f.read()

        config = {}
        if plugin_v1_factory_symbol is not None:
            config["_trt_plugin_v1_factory_symbol"] = plugin_v1_factory_symbol.encode()

        return self.register_native_module(
            module_tag,
            "TensorRTModule",
            context_data=data,
            config=config,
            **kwargs,
        )

    def register_onnx(
        self,
        module_tag: str,
        onnx_file: str,
        **kwargs,
    ) -> str:
        """
        Registers an ONNX model.

        :param module_tag: The tag to use for the module
        :param onnx_file: The file containing the ONNX model
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        with open(onnx_file, "rb") as f:
            data = f.read()

        return self.register_py_module(
            module_tag,
            "OnnxModule",
            "exa.py_onnx_module",
            "OnnxModuleContext",
            "exa.py_onnx_module",
            context_data=data,
            **kwargs,
        )

    def register_function_wrapper_module(
        self,
        module_tag: str,
        module_class: str,
        shared_object_path: str,
        dependent_shared_object_paths: Optional[List[str]] = None,
        **kwargs,
    ) -> str:
        """
        DEPRECATED: Registers a function wrapper shared object as a module.

        Use register_hermetic_function_wrapper_module instead.

        :param module_tag: The tag to use for the module
        :param module_class: The class name of the module
        :param shared_object_path: The path to the function wrapper shared object
        :param dependent_shared_object_paths: Optional; the paths to the
            dependent shared objects
        :param kwargs: Additional arguments to pass to register_native_module
        :return: The object id of the module
        """
        so_id = self.register_shared_object(shared_object_path)
        dependent_so_ids = []
        if dependent_shared_object_paths is not None:
            dependent_so_ids = [
                self.register_shared_object(x) for x in dependent_shared_object_paths
            ]
        plugin_id = self.register_module_plugin(
            so_id, dependent_shared_objects=dependent_so_ids
        )
        return self.register_native_module(
            module_tag,
            module_class=module_class,
            module_plugin=plugin_id,
            **kwargs,
        )

    def register_hermetic_function_wrapper_module(
        self,
        module_tag: str,
        module_class: str,
        runfiles_dir: str,
        shared_object_path: str,
        runner_image: Optional[str] = None,
        runfiles_env_var_names: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Registers a function wrapper shared object and runfiles directory as a
        module.

        :param module_tag: The tag to use for the module
        :param module_class: The class name of the module
        :param runfiles_dir: The runfiles directory
            This directory should contain the function wrapper shared object.
        :param shared_object_path: The path to the function wrapper shared object.
            This path should be relative to the runfiles directory.
        :param runner_image: Optional; the runner image tag or id.
            If not specified, the default runner image is used.
        :param runfiles_env_var_names: Optional; a list of environment variables
            to to expose the runfiles; defaults to ["EXAFUNCTION_RUNFILES"]
        :return: The object id of the module
        """
        plugin_id = self.register_hermetic_module_plugin(
            runfiles_dir,
            shared_object_path,
            runner_image=runner_image,
            runfiles_env_var_names=runfiles_env_var_names,
        )
        return self.register_native_module(
            module_tag,
            module_class=module_class,
            module_plugin=plugin_id,
            **kwargs,
        )

    def clear(self):
        """
        Clears the module repository.

        Do not use.
        """
        if not exa._module_repository_clear_allowed:  # pylint: disable=protected-access
            raise PermissionError("Can't clear module repository")
        req = module_repository_pb2.ClearDataRequest()
        self.stub.ClearData(req)

    def _blob_id_exists(self, blob_id):
        req = module_repository_pb2.ExistsBlobRequest()
        req.blob_id = blob_id
        resp = self.stub.ExistsBlob(req)
        return resp.exists

    def _id_from_tag_or_id(self, tag_or_id: str):
        if tag_or_id.startswith("@"):
            return tag_or_id  # Is an ID
        return self.get_object_id_from_tag(tag_or_id)

    def _register_blob_from_stream(self, stream: BinaryIO) -> str:
        stream.seek(0)
        blob_id = _generate_data_id(stream)
        # See if this blob already exists, if so we can skip pushing
        if self._blob_id_exists(blob_id):
            return blob_id

        stream.seek(0)

        def generate_data_chunks():
            while True:
                req = module_repository_pb2.RegisterBlobStreamingRequest()
                req.data_chunk = stream.read(REGISTER_BLOB_CHUNK_SIZE)
                if len(req.data_chunk) == 0:
                    return
                yield req

        data_chunk_iterator = generate_data_chunks()
        resp = self.stub.RegisterBlobStreaming(data_chunk_iterator)
        if blob_id != resp.blob_id:
            raise AssertionError(
                "Returned blob id does not match locally computed value"
            )
        return resp.blob_id

    def _register_blob(self, data_bytes: bytes) -> str:
        return self._register_blob_from_stream(io.BytesIO(data_bytes))

    def _register_object(
        self, metadata: module_repository_pb2.Metadata, tag: Optional[str] = None
    ) -> str:
        serialized_metadata = metadata.SerializeToString(deterministic=True)
        object_id = _generate_data_id(io.BytesIO(serialized_metadata))
        # See if this object already exists, if so we can skip pushing
        if not self.object_id_exists(object_id):
            req = module_repository_pb2.RegisterObjectRequest()
            req.serialized_metadata = serialized_metadata
            resp = self.stub.RegisterObject(req)
            if object_id != resp.object_id:
                raise AssertionError(
                    "Returned object id does not match locally computed value"
                )
        if tag is not None:
            self.add_tag(tag, object_id)
        return object_id

    def _ping(self):
        try:
            resp = self.stub.HealthCheck(module_repository_pb2.HealthCheckRequest())
        except grpc.RpcError:
            return False
        return resp.healthy


def _parse_tag(tag: str) -> Tuple[str, str]:
    for c in tag:
        char_idx = ord(c)
        if char_idx < 0x20 or char_idx > 0x7E:
            raise ValueError(
                "Module tag contains non-printable or non-ASCII characters"
            )

    if ":" in tag:
        name_and_version = tag.split(":")
        if len(name_and_version) != 2:
            raise ValueError(f"Invalid module tag {tag}")
        name = name_and_version[0]
        version = name_and_version[1]
    else:
        name = tag
        version = "latest"
    return name, version


def _generate_tag(name: str, version: Optional[str] = None) -> str:
    if version is None:
        return name + "latest"
    return f"{name}:{version}"


def _generate_data_id(stream: BinaryIO) -> str:
    m = hashlib.sha256()
    while True:
        chunk = stream.read(REGISTER_BLOB_CHUNK_SIZE)
        if len(chunk) == 0:
            break
        m.update(chunk)
    digest = m.digest()[:15]  # Keep only 120 bits
    return "@" + base64.urlsafe_b64encode(digest).decode("utf-8")


def _make_zip_info(filename, arcname=None):
    """Construct a ZipInfo, but without reading the file timestamp"""
    if isinstance(filename, os.PathLike):
        filename = os.fspath(filename)
    st = os.stat(filename)
    isdir = stat.S_ISDIR(st.st_mode)
    date_time = (1980, 1, 1, 0, 0, 0)

    # Create ZipInfo instance to store file information
    if arcname is None:
        arcname = filename
    arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
    while arcname[0] in (os.sep, os.altsep):
        arcname = arcname[1:]
    if isdir:
        arcname += "/"
    zinfo = zipfile.ZipInfo(arcname, date_time)
    zinfo.external_attr = (st.st_mode & 0xFFFF) << 16  # Unix attributes
    if isdir:
        zinfo.file_size = 0
        zinfo.external_attr |= 0x10  # MS-DOS directory flag
    else:
        zinfo.file_size = st.st_size

    return zinfo


def glob(directory: str, glob_list: Optional[List[str]] = None) -> List[pathlib.Path]:
    """
    Returns a list of file and directory paths in the given directory,
    optionally using the list of glob patterns. If the list is not provided then
    all files and directories are returned.

    :param directory: The directory to search
    :param glob_list: A list of glob patterns to use
    :return: A list of file and directory paths matching the glob patterns
    """

    # Walk directories to make sure we have permissions to read them
    # Otherwise we may miss files when globbing
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"Cannot access {directory}")
    for dirpath, dirnames, _ in os.walk(directory):
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            if not os.access(path, os.R_OK):
                raise PermissionError(f"Cannot access {path}")

    if glob_list is None:
        glob_list = ["**/*"]  # Include everything

    directory_path = pathlib.Path(directory)
    glob_files_set: Set[pathlib.Path] = set()
    for glob_pattern in glob_list:
        files = directory_path.glob(glob_pattern)
        glob_files_set.update(files)

    return list(sorted(glob_files_set))  # Ensure file order is deterministic


def _zip_directory(directory: str, glob_list: Optional[List[str]] = None) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a") as zipf:
        for path in glob(directory, glob_list):
            if not os.path.isfile(path):
                continue
            arcname = os.path.relpath(path, directory)
            zinfo = _make_zip_info(path, arcname)
            with open(path, "rb") as f:
                zipf.writestr(zinfo, f.read(), zipfile.ZIP_STORED)
    return zip_buffer.getvalue()


def get_bazel_runfiles_root():
    """Get the Bazel runfiles directory root"""
    runfiles_root = os.environ.get("RUNFILES_DIR")
    if runfiles_root is None:
        runfiles_manifest = os.environ.get("RUNFILES_MANIFEST_FILE")
        assert runfiles_manifest.endswith("_manifest")
        runfiles_root = runfiles_manifest[: -len("_manifest")]
    assert runfiles_root is not None
    return runfiles_root
