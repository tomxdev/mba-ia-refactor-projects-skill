"""Composition root — cria o app, carrega config, injeta dependências e sobe."""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from controllers.pedido_controller import PedidoController
from controllers.produto_controller import ProdutoController
from controllers.system_controller import SystemController
from controllers.usuario_controller import UsuarioController
from database import create_connection, init_db
from middlewares.error_handler import register_error_handlers
from models.pedido_model import PedidoModel
from models.produto_model import ProdutoModel
from models.usuario_model import UsuarioModel
from services.notification_service import NotificationService
from services.relatorio_service import RelatorioService
from views.routes import build_blueprint


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config.from_object(Settings)
    CORS(app)

    # Recurso criado uma vez e injetado nos models (sem singleton global mutável).
    db = create_connection(Settings.DB_PATH)
    init_db(db)

    produto_c = ProdutoController(ProdutoModel(db))
    usuario_c = UsuarioController(UsuarioModel(db))
    pedido_c = PedidoController(
        PedidoModel(db), RelatorioService(db), NotificationService()
    )
    system_c = SystemController(db, Settings.ADMIN_TOKEN)

    app.register_blueprint(build_blueprint(produto_c, usuario_c, pedido_c, system_c))
    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{Settings.PORT}")
    print("=" * 50)
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
