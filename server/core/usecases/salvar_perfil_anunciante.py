"""Create or update the advertiser profile, all or nothing (RN8)."""

from dataclasses import dataclass, replace

from server.core.entities.anunciante import Anunciante
from server.core.entities.contato import Contato
from server.core.entities.foto_de_perfil import FotoDePerfil
from server.core.interfaces.anunciante_repository_interface import (
    AnuncianteRepositoryInterface,
)
from server.core.interfaces.armazenamento_de_foto_interface import (
    ArmazenamentoDeFotoInterface,
)
from server.core.usecases.erros import DadosInvalidos, FotoInvalida


@dataclass(frozen=True)
class DadosDeContato:
    """Raw contact data, so controllers do not need the entities."""

    tipo: str
    valor: str
    codigo_pais: str | None = None
    rotulo: str | None = None


class SalvarPerfilAnunciante:

    def __init__(
        self,
        anunciantes: AnuncianteRepositoryInterface,
        fotos: ArmazenamentoDeFotoInterface,
    ) -> None:
        self._anunciantes = anunciantes
        self._fotos = fotos

    def executar(
        self,
        *,
        usuario_id: int,
        nome_exibicao: str,
        contatos: list[DadosDeContato],
        foto: bytes | None = None,
        remover_foto: bool = False,
    ) -> Anunciante:
        nova_foto = self._validar_foto(foto)
        contatos_validos = self._converter_contatos(contatos)
        atual = self._anunciantes.buscar_por_usuario_id(usuario_id)
        perfil = self._montar_perfil(
            atual, usuario_id, nome_exibicao, contatos_validos
        )

        foto_antiga = None if atual is None else atual.foto_url
        if nova_foto is not None:
            perfil = perfil.com_foto(self._fotos.salvar(nova_foto))
        elif remover_foto:
            perfil = perfil.sem_foto()

        try:
            salvo = self._anunciantes.salvar(perfil)
        except Exception:
            if nova_foto is not None:
                self._fotos.remover(perfil.foto_url)
            raise

        if foto_antiga is not None and salvo.foto_url != foto_antiga:
            self._fotos.remover(foto_antiga)
        return salvo

    @staticmethod
    def _validar_foto(foto: bytes | None) -> FotoDePerfil | None:
        if foto is None:
            return None
        try:
            return FotoDePerfil.de_bytes(foto)
        except ValueError as erro:
            raise FotoInvalida(str(erro)) from erro

    @staticmethod
    def _converter_contatos(contatos: list[DadosDeContato]) -> list[Contato]:
        convertidos = []
        for posicao, dados in enumerate(contatos, start=1):
            try:
                convertidos.append(
                    Contato.criar(
                        dados.tipo,
                        dados.valor,
                        dados.codigo_pais,
                        dados.rotulo,
                    )
                )
            except ValueError as erro:
                raise DadosInvalidos(f"Contato {posicao}: {erro}") from erro
        return convertidos

    @staticmethod
    def _montar_perfil(
        atual: Anunciante | None,
        usuario_id: int,
        nome_exibicao: str,
        contatos: list[Contato],
    ) -> Anunciante:
        try:
            if atual is None:
                return Anunciante(usuario_id, nome_exibicao, contatos)
            return replace(
                atual, nome_exibicao=nome_exibicao, contatos=tuple(contatos)
            )
        except ValueError as erro:
            raise DadosInvalidos(str(erro)) from erro
