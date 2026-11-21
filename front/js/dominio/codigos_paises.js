// Lista de países para escolher o código de telefone (CA12, CA14). O backend só
// confere que o código tem de 1 a 3 dígitos; a lista serve à tela.

export const PAISES = [
  { nome: "Brasil", sigla: "BR", codigo: "55" },
  { nome: "Argentina", sigla: "AR", codigo: "54" },
  { nome: "Bolívia", sigla: "BO", codigo: "591" },
  { nome: "Chile", sigla: "CL", codigo: "56" },
  { nome: "Colômbia", sigla: "CO", codigo: "57" },
  { nome: "Equador", sigla: "EC", codigo: "593" },
  { nome: "Paraguai", sigla: "PY", codigo: "595" },
  { nome: "Peru", sigla: "PE", codigo: "51" },
  { nome: "Uruguai", sigla: "UY", codigo: "598" },
  { nome: "Venezuela", sigla: "VE", codigo: "58" },
  { nome: "Estados Unidos e Canadá", sigla: "US", codigo: "1" },
  { nome: "México", sigla: "MX", codigo: "52" },
  { nome: "Portugal", sigla: "PT", codigo: "351" },
  { nome: "Espanha", sigla: "ES", codigo: "34" },
  { nome: "França", sigla: "FR", codigo: "33" },
  { nome: "Itália", sigla: "IT", codigo: "39" },
  { nome: "Alemanha", sigla: "DE", codigo: "49" },
  { nome: "Reino Unido", sigla: "GB", codigo: "44" },
  { nome: "Irlanda", sigla: "IE", codigo: "353" },
  { nome: "Países Baixos", sigla: "NL", codigo: "31" },
  { nome: "Bélgica", sigla: "BE", codigo: "32" },
  { nome: "Suíça", sigla: "CH", codigo: "41" },
  { nome: "Suécia", sigla: "SE", codigo: "46" },
  { nome: "Angola", sigla: "AO", codigo: "244" },
  { nome: "Moçambique", sigla: "MZ", codigo: "258" },
  { nome: "Cabo Verde", sigla: "CV", codigo: "238" },
  { nome: "África do Sul", sigla: "ZA", codigo: "27" },
  { nome: "Egito", sigla: "EG", codigo: "20" },
  { nome: "Turquia", sigla: "TR", codigo: "90" },
  { nome: "Israel", sigla: "IL", codigo: "972" },
  { nome: "Emirados Árabes Unidos", sigla: "AE", codigo: "971" },
  { nome: "Rússia", sigla: "RU", codigo: "7" },
  { nome: "Índia", sigla: "IN", codigo: "91" },
  { nome: "China", sigla: "CN", codigo: "86" },
  { nome: "Japão", sigla: "JP", codigo: "81" },
  { nome: "Coreia do Sul", sigla: "KR", codigo: "82" },
  { nome: "Austrália", sigla: "AU", codigo: "61" },
];

export const PAIS_PADRAO = PAISES[0];
export const CODIGO_PAIS_PADRAO = PAIS_PADRAO.codigo;

export const textoDoPais = (pais) => `${pais.nome} (+${pais.codigo})`;
