from src.api.openai import APIOpenAI


async def test_openai():
    api = APIOpenAI()
    response = await api.generate_response("привет")
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_openai())
