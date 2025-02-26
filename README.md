# Учебный сервис на основе gRPC на Python 

## Содержание

- [Описание](#описание)
- [Зависимости и установка](#зависимости-и-установка)
- [Запуск сервиса](#запуск-сервиса)
- [Ссылки](#ссылки)

## Описание
____
Сервис на основе `gRPC` написанный на `Python`. Минималистичен и абстрактен. Реализован в виде `CRUD`
над условными "Пользователями" (сущности с которыми работает сервис - `user`). Включает 4 метода, 
каждый из которых является примером одного из возможных `gRPC` взаимодействий:
- Unary
- Server streaming
- Client streaming
- Bidirectional streaming

## Зависимости и установка
____
Сервис реализовывался на `Python 3.12.0`.

Перед тем как приступить к установке зависимостей рекомендуется настроить 
виртуальное окружение `venv` с соответствующей версией интерпретатора.

В активированном виртуальном окружении:
```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

Далее генерируем код из `.proto`. В корне проекта:
```bash
python -m grpc_tools.protoc -I ./proto --python_out=./src/ --grpc_python_out=./src/ ./proto/GrpcExampleService.proto
```

## Запуск сервиса
____
В корне проекта:
```bash
cd src && python grpc_example_service.py
```

При старте сервиса будет создана БД `SQLite` в папке `database` если её там ещё нет.

Также самый простой способ очистить БД - это просто удалить её файл и при повторном запуске сервиса
БД создастся снова.

## Ссылки
____
- [Описание методов](https://github.com/ritchiesinger/grpc_example_service/wiki/gRPC-Example-Service)