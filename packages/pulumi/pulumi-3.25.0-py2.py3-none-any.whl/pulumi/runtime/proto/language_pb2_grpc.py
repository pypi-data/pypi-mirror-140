# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import language_pb2 as language__pb2
from . import plugin_pb2 as plugin__pb2


class LanguageRuntimeStub(object):
    """LanguageRuntime is the interface that the planning monitor uses to drive execution of an interpreter responsible
    for confguring and creating resource objects.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
          channel: A grpc.Channel.
        """
        self.GetRequiredPlugins = channel.unary_unary(
            "/pulumirpc.LanguageRuntime/GetRequiredPlugins",
            request_serializer=language__pb2.GetRequiredPluginsRequest.SerializeToString,
            response_deserializer=language__pb2.GetRequiredPluginsResponse.FromString,
        )
        self.Run = channel.unary_unary(
            "/pulumirpc.LanguageRuntime/Run",
            request_serializer=language__pb2.RunRequest.SerializeToString,
            response_deserializer=language__pb2.RunResponse.FromString,
        )
        self.GetPluginInfo = channel.unary_unary(
            "/pulumirpc.LanguageRuntime/GetPluginInfo",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=plugin__pb2.PluginInfo.FromString,
        )


class LanguageRuntimeServicer(object):
    """LanguageRuntime is the interface that the planning monitor uses to drive execution of an interpreter responsible
    for confguring and creating resource objects.
    """

    def GetRequiredPlugins(self, request, context):
        """GetRequiredPlugins computes the complete set of anticipated plugins required by a program."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Run(self, request, context):
        """Run executes a program and returns its result."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetPluginInfo(self, request, context):
        """GetPluginInfo returns generic information about this plugin, like its version."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_LanguageRuntimeServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetRequiredPlugins": grpc.unary_unary_rpc_method_handler(
            servicer.GetRequiredPlugins,
            request_deserializer=language__pb2.GetRequiredPluginsRequest.FromString,
            response_serializer=language__pb2.GetRequiredPluginsResponse.SerializeToString,
        ),
        "Run": grpc.unary_unary_rpc_method_handler(
            servicer.Run,
            request_deserializer=language__pb2.RunRequest.FromString,
            response_serializer=language__pb2.RunResponse.SerializeToString,
        ),
        "GetPluginInfo": grpc.unary_unary_rpc_method_handler(
            servicer.GetPluginInfo,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=plugin__pb2.PluginInfo.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "pulumirpc.LanguageRuntime", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
