EPSILON = "ε"


def _unique(items):
    result = []

    for item in items:
        if item not in result:
            result.append(item)

    return result


def _normalize_right_side(right_side):
    if right_side is None:
        return []

    if isinstance(right_side, str):
        right_side = right_side.strip()

        if right_side in ("", EPSILON, "eps", "epsilon", "lambda", "λ"):
            return []

        return list(right_side.replace(" ", ""))

    cleaned = []

    for symbol in right_side:
        symbol = str(symbol).strip()

        if symbol not in ("", EPSILON, "eps", "epsilon", "lambda", "λ"):
            cleaned.append(symbol)

    return cleaned


def pda_uret(grammar_data):
    """
    CFG'den standart PDA üretir.
    Kullanılan temel mantığı aşagıdakı metinde acıkladım hocam :

    1. Başlangıçta yığına başlangıç değişkeni koyulur.
       δ(q_start, ε, $) → (q_loop, S)

    2. Her CFG üretimi için epsilon geçişi oluşturulur.
       A → xyz için:
       δ(q_loop, ε, A) → (q_loop, zyx)

    3. Her terminal için eşleştirme geçişi oluşturulur.
       δ(q_loop, a, a) → (q_loop, ε)

    4. Girdi bitince ve yığında sadece $ kalınca kabul durumuna geçilir.
    """

    states = ["q_start", "q_loop", "q_accept"]
    start_state = "q_start"
    loop_state = "q_loop"
    accept_state = "q_accept"
    accept_states = [accept_state]


    start_stack_symbol = "$"

    nonterminals = grammar_data["nonterminals"]
    terminals = grammar_data["terminals"]
    start_symbol = grammar_data["start_symbol"]
    productions = grammar_data["productions"]

    stack_symbols = _unique([start_stack_symbol] + nonterminals + terminals)

    transitions = []

    # Başlangıçta yığında $ vardır.
    # $ pop edilir, yerine $ ve başlangıç sembolü konur.
    # Liste sırası alt -> üst mantığıyla tutulur.
    # Bu yüzden ["$", "S"] yığında $S demektir.
    transitions.append({
        "from": start_state,
        "input": EPSILON,
        "pop": start_stack_symbol,
        "to": loop_state,
        "push": [start_stack_symbol, start_symbol],
        "label": f"Başlangıç: {start_stack_symbol} üstüne {start_symbol} koy"
    })


    for left_side, right_sides in productions.items():
        for right_side in right_sides:
            right_symbols = _normalize_right_side(right_side)

            push_list = list(reversed(right_symbols))

            rhs_text = "".join(right_symbols) if right_symbols else EPSILON

            transitions.append({
                "from": loop_state,
                "input": EPSILON,
                "pop": left_side,
                "to": loop_state,
                "push": push_list,
                "label": f"Üretim uygula: {left_side} → {rhs_text}"
            })


    for terminal in terminals:
        transitions.append({
            "from": loop_state,
            "input": terminal,
            "pop": terminal,
            "to": loop_state,
            "push": [],
            "label": f"Terminal eşleştir: {terminal} oku, yığından {terminal} sil"
        })


    transitions.append({
        "from": loop_state,
        "input": EPSILON,
        "pop": start_stack_symbol,
        "to": accept_state,
        "push": [],
        "label": f"Kabul: giriş bitti, yığındaki {start_stack_symbol} silindi",
        "require_input_end": True
    })

    return {
        "name": "CFG'den otomatik üretilen PDA",
        "states": states,
        "input_symbols": terminals,
        "stack_symbols": stack_symbols,
        "start_state": start_state,
        "start_stack_symbol": start_stack_symbol,
        "accept_states": accept_states,
        "transitions": transitions
    }