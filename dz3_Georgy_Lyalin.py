import asyncio
import time

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

# Создайте FastAPI-приложение, которое показывает, как работает
# асинхронность в Python.
# Приложение должно реализовывать эндпоинт: POST /calculate/
# Что делает: принимает список чисел и задержек, считает квадраты этих чисел
# асинхронно.
#
# Пример проверки через curl.
# 1. Запустить сервер:
#      uv run uvicorn dz3_Georgy_Lyalin:app
# 2. Отправить запрос:
#      curl -X POST http://127.0.0.1:8000/calculate/ \
#           -H "Content-Type: application/json" \
#           -d '{"numbers": [5, 3, 10], "delays": [1, 2, 0.5]}'


class NumbersToGetSquared(BaseModel):
    numbers: list[float]
    delays: list[float]
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"numbers": [5, 3, 10], "delays": [1, 2, 0.5]}
            ]
        }
    )

class SquaredNumber(BaseModel):
    number: float
    square: float
    delay: float
    time: float

class Response(BaseModel):
    results: list[SquaredNumber]
    total_time: float
    potential_sequential_time: float
    is_parallel_faster_than_sequential: bool

app = FastAPI()

@app.post("/calculate/")
async def calculate_square(numbers: NumbersToGetSquared):
    start = time.perf_counter()
    coroutines = [get_single_square(n, d) for n, d in zip(numbers.numbers, numbers.delays)]
    results = await asyncio.gather(*coroutines)
    total_time = time.perf_counter() - start

    sequential_time = sum(item.time for item in results)

    return Response(
        results=results,
        total_time=round(total_time, 4),
        potential_sequential_time=round(sequential_time, 4),
        is_parallel_faster_than_sequential=total_time < sequential_time,
    )

async def get_single_square(number: float, delay: float):
    start = time.perf_counter()
    await asyncio.sleep(delay) 
    elapsed = time.perf_counter() - start
    return SquaredNumber(number=number, 
                         square=number * number, 
                         delay= delay, time=elapsed)