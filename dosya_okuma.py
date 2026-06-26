import json
from pathlib import Path

EPSILON = "ε"


def _normalize_epsilon(value):
    if value is None:
        return EPSILON

    value = str(value).strip()

    if value in ("", "eps", "epsilon", "lambda", "Λ", "λ"):
        return EPSILON

    return value


def oku_json(dosya_yolu):
    path = Path(dosya_yolu)

    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def oku_gramer(dosya_yolu="gramer.json"):
    data = oku_json(dosya_yolu)

    gerekli_alanlar = [
        "nonterminals",
        "terminals",
        "start_symbol",
        "productions"
    ]

    for alan in gerekli_alanlar:
        if alan not in data:
            raise ValueError(f"gramer.json içinde '{alan}' alanı eksik.")

    uretimler = {}

    for sol, saglar in data["productions"].items():
        yeni_saglar = []

        for sag in saglar:
            if isinstance(sag, str):
                if sag == EPSILON:
                    yeni_saglar.append([])
                else:
                    yeni_saglar.append(list(sag.replace(" ", "")))
            else:
                yeni_saglar.append([
                    _normalize_epsilon(x)
                    for x in sag
                    if _normalize_epsilon(x) != EPSILON
                ])

        uretimler[sol] = yeni_saglar

    data["productions"] = uretimler

    return data


def oku_pda(dosya_yolu="pda.json"):
    data = oku_json(dosya_yolu)

    gerekli_alanlar = [
        "states",
        "input_symbols",
        "stack_symbols",
        "start_state",
        "start_stack_symbol",
        "accept_states",
        "transitions",
    ]

    for alan in gerekli_alanlar:
        if alan not in data:
            raise ValueError(f"pda.json içinde '{alan}' alanı eksik.")

    gecisler = []

    for index, gecis in enumerate(data["transitions"], start=1):
        for alan in ["from", "input", "pop", "to", "push"]:
            if alan not in gecis:
                raise ValueError(
                    f"pda.json geçiş #{index} içinde '{alan}' alanı eksik."
                )

        push = gecis["push"]

        if isinstance(push, str):
            push = [] if _normalize_epsilon(push) == EPSILON else [push]
        else:
            push = [_normalize_epsilon(x) for x in push]
            push = [x for x in push if x != EPSILON]

        gecisler.append({
            "from": str(gecis["from"]),
            "input": _normalize_epsilon(gecis["input"]),
            "pop": _normalize_epsilon(gecis["pop"]),
            "to": str(gecis["to"]),
            "push": push,
            "label": gecis.get("label", ""),
            "require_input_end": bool(gecis.get("require_input_end", False)),
        })

    data["transitions"] = gecisler

    return data


def oku_girdiler(dosya_yolu="girdiler.txt"):
    path = Path(dosya_yolu)

    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {path}")

    girdiler = []

    with path.open("r", encoding="utf-8") as file:
        for satir in file:
            satir = satir.strip()

            if not satir or satir.startswith("#"):
                continue

            girdiler.append("" if satir == EPSILON else satir)

    return girdiler