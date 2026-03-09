from api import create_embedding


def embedding_fn(text):

    response = create_embedding(text)

    return response["embedding"]