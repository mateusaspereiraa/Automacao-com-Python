"""Cadastro automático de produtos (versão melhorada de codigo.py).

Melhorias: login por variáveis de ambiente (nada de senha no código), posições
dos cliques em config.json, validação do CSV, modo teste (--teste), limite de
linhas, log com progresso e parada de emergência (mover o mouse ao canto da tela).
Uso:  python codigo_melhorado.py --teste      (simula, sem mexer no computador)
      python codigo_melhorado.py              (executa de verdade)
"""
import argparse, csv, json, os, sys, time

CAMPOS = ["codigo", "marca", "tipo", "categoria", "preco_unitario", "custo", "obs"]


def carregar_produtos(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    faltando = [c for c in CAMPOS if c not in (linhas[0] if linhas else {})]
    if faltando:
        sys.exit(f"CSV sem as colunas: {', '.join(faltando)}")
    validos = [l for l in linhas if l["codigo"].strip()]
    print(f"{len(validos)} produtos válidos ({len(linhas) - len(validos)} ignorados sem código)")
    return validos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="produtos.csv")
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--limite", type=int, default=0, help="cadastra só as N primeiras linhas")
    ap.add_argument("--teste", action="store_true", help="simula sem controlar mouse e teclado")
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding="utf-8"))
    produtos = carregar_produtos(a.csv)[: a.limite or None]

    if a.teste:
        gui = None
    else:
        import pyautogui, pyperclip
        pyautogui.PAUSE, pyautogui.FAILSAFE = cfg.get("pausa", 0.3), True
        gui = (pyautogui, pyperclip)

    def escrever(texto):
        if gui:
            gui[1].copy(str(texto)); gui[0].hotkey("ctrl", "v")  # aceita acentos

    if gui:
        email, senha = os.environ.get("SISTEMA_EMAIL"), os.environ.get("SISTEMA_SENHA")
        if not (email and senha):
            sys.exit("Defina SISTEMA_EMAIL e SISTEMA_SENHA antes de rodar.")
        gui[0].press("win"); escrever("chrome"); gui[0].press("enter"); time.sleep(3)
        escrever(cfg["url"]); gui[0].press("enter"); time.sleep(cfg.get("espera_site", 5))
        gui[0].click(*cfg["campo_email"]); escrever(email)
        gui[0].press("tab"); escrever(senha); gui[0].press("enter"); time.sleep(3)

    t0 = time.time()
    for n, p in enumerate(produtos, 1):
        if gui:
            gui[0].click(*cfg["campo_codigo"])
            for i, campo in enumerate(CAMPOS):
                escrever(p[campo]) if p[campo] else None
                if i < len(CAMPOS) - 1:
                    gui[0].press("tab")
            gui[0].press("enter"); gui[0].scroll(cfg.get("scroll", 5000))
        print(f"[{n}/{len(produtos)}] {p['codigo']} - {p['marca']} {p['tipo']}")
    print(f"Concluído em {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
