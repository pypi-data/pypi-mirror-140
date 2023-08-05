# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from github.com.metaprov.modelaapi.services.virtualcluster.v1 import virtualcluster_pb2 as github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2


class VirtualClusterServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListVirtualClusters = channel.unary_unary(
                '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/ListVirtualClusters',
                request_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.ListVirtualClustersRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.ListVirtualClustersResponse.FromString,
                )
        self.CreateVirtualCluster = channel.unary_unary(
                '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/CreateVirtualCluster',
                request_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.CreateVirtualClusterRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.CreateVirtualClusterResponse.FromString,
                )
        self.GetVirtualCluster = channel.unary_unary(
                '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/GetVirtualCluster',
                request_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.GetVirtualClusterRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.GetVirtualClusterResponse.FromString,
                )
        self.UpdateVirtualCluster = channel.unary_unary(
                '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/UpdateVirtualCluster',
                request_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.UpdateVirtualClusterRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.UpdateVirtualClusterResponse.FromString,
                )
        self.DeleteVirtualCluster = channel.unary_unary(
                '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/DeleteVirtualCluster',
                request_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.DeleteVirtualClusterRequest.SerializeToString,
                response_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.DeleteVirtualClusterResponse.FromString,
                )


class VirtualClusterServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ListVirtualClusters(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateVirtualCluster(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetVirtualCluster(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateVirtualCluster(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteVirtualCluster(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VirtualClusterServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ListVirtualClusters': grpc.unary_unary_rpc_method_handler(
                    servicer.ListVirtualClusters,
                    request_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.ListVirtualClustersRequest.FromString,
                    response_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.ListVirtualClustersResponse.SerializeToString,
            ),
            'CreateVirtualCluster': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateVirtualCluster,
                    request_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.CreateVirtualClusterRequest.FromString,
                    response_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.CreateVirtualClusterResponse.SerializeToString,
            ),
            'GetVirtualCluster': grpc.unary_unary_rpc_method_handler(
                    servicer.GetVirtualCluster,
                    request_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.GetVirtualClusterRequest.FromString,
                    response_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.GetVirtualClusterResponse.SerializeToString,
            ),
            'UpdateVirtualCluster': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateVirtualCluster,
                    request_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.UpdateVirtualClusterRequest.FromString,
                    response_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.UpdateVirtualClusterResponse.SerializeToString,
            ),
            'DeleteVirtualCluster': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteVirtualCluster,
                    request_deserializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.DeleteVirtualClusterRequest.FromString,
                    response_serializer=github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.DeleteVirtualClusterResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class VirtualClusterService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ListVirtualClusters(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/ListVirtualClusters',
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.ListVirtualClustersRequest.SerializeToString,
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.ListVirtualClustersResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateVirtualCluster(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/CreateVirtualCluster',
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.CreateVirtualClusterRequest.SerializeToString,
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.CreateVirtualClusterResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetVirtualCluster(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/GetVirtualCluster',
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.GetVirtualClusterRequest.SerializeToString,
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.GetVirtualClusterResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateVirtualCluster(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/UpdateVirtualCluster',
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.UpdateVirtualClusterRequest.SerializeToString,
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.UpdateVirtualClusterResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteVirtualCluster(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/github.com.metaprov.modelaapi.services.virtualcluster.v1.VirtualClusterService/DeleteVirtualCluster',
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.DeleteVirtualClusterRequest.SerializeToString,
            github_dot_com_dot_metaprov_dot_modelaapi_dot_services_dot_virtualcluster_dot_v1_dot_virtualcluster__pb2.DeleteVirtualClusterResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
