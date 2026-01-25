from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence


@dataclass
class VerificadorCitacoes:
    """Valida se as citacoes mencionadas aparecem nas fontes fornecidas."""

    regex_citacao: re.Pattern = field(default_factory=lambda: re.compile(r"\[([^\]]+)\]"))

    def extrair_citacoes(self, resposta: str) -> List[str]:
        citacoes: List[str] = []
        for bloco in self.regex_citacao.findall(resposta):
            for parte in bloco.split(","):
                citacao = parte.strip()
                if citacao:
                    citacoes.append(citacao)
        return citacoes

    def validar(self, resposta: str, fontes: Sequence[str]) -> List[str]:
        fontes_normalizadas = {self._normalizar(fonte) for fonte in fontes}
        alertas: List[str] = []
        vistos = set()
        for citacao in self.extrair_citacoes(resposta):
            citacao_normalizada = self._normalizar(citacao)
            if citacao_normalizada in vistos:
                continue
            vistos.add(citacao_normalizada)
            if citacao_normalizada not in fontes_normalizadas:
                alertas.append(citacao)
        return alertas

    @staticmethod
    def _normalizar(texto: str) -> str:
        return texto.strip().casefold()


class AgenteJuridicoRAG:
    """Agente jurídico com verificação de citações na etapa de resposta."""

    def __init__(self, verificador: VerificadorCitacoes | None = None) -> None:
        self.verificador = verificador or VerificadorCitacoes()

    def gerar_resposta(self, consulta: str, fontes: Iterable[str]) -> dict:
        resposta = self._montar_resposta(consulta, fontes)
        alertas = self.verificador.validar(resposta["resposta"], resposta.get("fontes", []))
        if alertas:
            resposta["alertas"] = alertas
        return resposta

    def _montar_resposta(self, consulta: str, fontes: Iterable[str]) -> dict:
        fontes_lista = list(fontes)
        return {
            "consulta": consulta,
            "resposta": f"Resumo jurídico para: {consulta}",
            "fontes": fontes_lista,
        }
