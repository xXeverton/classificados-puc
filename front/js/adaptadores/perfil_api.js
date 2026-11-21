export function criarPerfilApi(cliente) {
  return {
    obter: () => cliente.requisitar("GET", "/perfil-anunciante"),
    // `formData` leva nome_exibicao, contatos (JSON), foto e remover_foto.
    salvar: (formData) => cliente.requisitar("PUT", "/perfil-anunciante", formData),
    // `caminho` é o foto_url do perfil (/fotos-perfil/<arquivo>).
    foto: (caminho) => cliente.baixar(caminho),
  };
}
