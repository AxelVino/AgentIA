from api import send_message


def use_agent(msg):

    """Aplica logica para enviar el mensaje y como mostrar la respuesta"""
    response = send_message(msg)
    print("\n🤖 response del agente:\n", response)
