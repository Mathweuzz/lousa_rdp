# LousaRDP

Lousa de desenho com correção de formas (Ramer-Douglas-Peucker + detecção de primiticas).

## Passo 1

Este estágio do projeto implementa

- Janela pygame 1280x720.
- Loop principal com alvo de 60 FPS.
- Grid leve de fundo.
- HUD com:
    - FPS.
    - Modo atual (MODE: desenho).
    - Valor de epsilon (placeholder).
    - Contador de "limpar" (teclas C).
    - Atalhos básicos (Q e C).

## Como rodar (Passo 1)

Com o ambiente virtual ativado:

```bash
python3 app/main.py
```
---

## Controles:

- Q: sair da aplicação.

- C: limpar estado (incrementa contador e redesenha, útil como placeholder).

---

