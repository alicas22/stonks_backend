try:
    from app import create_app
    from app.socket import init_sockets

    app, sock = create_app()
    init_sockets(sock)

    if __name__ == "__main__":
        app.run()
except ImportError as e:
    print(f"ImportError: {e}")
    raise
