"""Пример gRPC сервиса на Python."""

from concurrent import futures

from grpc import server
from grpc_reflection.v1alpha import reflection

from db_helper import DBHelper
import GrpcExampleService_pb2, GrpcExampleService_pb2_grpc


class GrpcExampleService(GrpcExampleService_pb2_grpc.GrpcExampleService):
    """Класс имплементирующий методы из .proto файла."""

    def __init__(self, db_helper: DBHelper):
        self.dbhelper = db_helper

    def AddUsers(self, request_iterator, context):
        """Добавление новых пользователей. Client Streaming."""
        return self.dbhelper.add_users(request_iterator)

    def GetUsers(self, request, context):
        """Получение данных всех пользователей. Server Streaming."""
        return self.dbhelper.get_users()

    def GetUserByLogin(self, request, context):
        """Получение данных пользователя по логину. Unary."""
        return self.dbhelper.get_user_by_login(request.login)

    def DeleteUsers(self, request_iterator, context):
        """Удаление клиентов. Bidirectional Streaming."""
        return self.dbhelper.delete_users(request_iterator)


def init_service(address: str):
    """Инициализация и старт сервиса."""
    grpc_server = server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
    GrpcExampleService_pb2_grpc.add_GrpcExampleServiceServicer_to_server(
        servicer=GrpcExampleService(db_helper=DBHelper(path_to_db="../database/mydatabase.db")),
        server=grpc_server
    )
    service_names = (
        GrpcExampleService_pb2.DESCRIPTOR.services_by_name['GrpcExampleService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, grpc_server)
    grpc_server.add_insecure_port(address=address)
    grpc_server.start()
    grpc_server.wait_for_termination()


if __name__ == '__main__':
    service_address = '[::]:50051'
    print(f'GrpcExampleService starts on {service_address} ...')
    init_service(address=service_address)
