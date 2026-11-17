"""Serviço de inferência: assina escola/sala1/aluno/+/sinais, mantém um buffer
de 60 s por aluno, calibra nos primeiros 5 min, calcula os 18 indicadores a
cada 30 s, roda o modelo e publica em escola/sala1/aluno/<id>/agitacao (retida)
e, pela regra de 2 janelas seguidas >= 0,5, em escola/sala1/alertas (QoS 1).
Contrato das mensagens: Seção 2.3 do relatório.

Cronograma: dia 13
"""


def main() -> None:
    raise NotImplementedError("A implementar: dia 13")


if __name__ == "__main__":
    main()
