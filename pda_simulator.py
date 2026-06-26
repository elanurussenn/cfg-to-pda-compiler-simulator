from collections import deque
from dataclasses import dataclass

EPSILON = "ε"
EMPTY_STACK = "∅"


@dataclass(frozen=True)
class Configuration:
    state: str
    position: int
    stack: tuple


class PDASimulator:
    def __init__(self, pda_data, grammar_data=None):
        self.pda = pda_data
        self.grammar = grammar_data or {}

        self.states = pda_data["states"]
        self.input_symbols = set(pda_data["input_symbols"])
        self.stack_symbols = set(pda_data["stack_symbols"])
        self.start_state = pda_data["start_state"]
        self.start_stack_symbol = pda_data["start_stack_symbol"]
        self.accept_states = set(pda_data["accept_states"])
        self.transitions = pda_data["transitions"]

    def tokenize_input(self, input_text):
        input_text = input_text.strip()

        if input_text in ("", EPSILON):
            return []

        if " " in input_text:
            return input_text.split()

        return list(input_text)

    def _transition_text(self, transition):
        push = "".join(transition["push"]) if transition["push"] else EPSILON

        return (
            f"δ({transition['from']}, {transition['input']}, {transition['pop']}) "
            f"→ ({transition['to']}, {push})"
        )

    def _applicable_transitions(self, config, tokens):
        if not config.stack:
            return []

        top = config.stack[-1]
        uygun = []

        for transition in self.transitions:
            if transition["from"] != config.state:
                continue

            if transition.get("require_input_end") and config.position != len(tokens):
                continue

            if transition["pop"] != top:
                continue

            giris = transition["input"]

            if giris == EPSILON:
                uygun.append(transition)
            elif config.position < len(tokens) and tokens[config.position] == giris:
                uygun.append(transition)

        return uygun

    def _apply_transition(self, config, transition):
        yeni_stack = list(config.stack[:-1])

        for symbol in transition["push"]:
            if symbol != EPSILON:
                yeni_stack.append(symbol)

        yeni_position = config.position

        if transition["input"] != EPSILON:
            yeni_position += 1

        return Configuration(
            state=transition["to"],
            position=yeni_position,
            stack=tuple(yeni_stack),
        )

    def _is_accepting(self, config, tokens):
        return config.state in self.accept_states and config.position == len(tokens)

    def _terminal_count_in_stack(self, stack):
        return sum(1 for symbol in stack if symbol in self.input_symbols)

    def _make_snapshot(self, step_no, action, config, tokens, detail):
        okunan = "".join(tokens[:config.position]) if tokens[:config.position] else EPSILON
        kalan = "".join(tokens[config.position:]) if tokens[config.position:] else EPSILON

        yigin = list(config.stack)

        yigin_alt_ust = " ".join(yigin) if yigin else EMPTY_STACK
        yigin_ust_alt = " ".join(reversed(yigin)) if yigin else EMPTY_STACK

        return {
            "step": step_no,
            "state": config.state,
            "read_input": okunan,
            "remaining_input": kalan,
            "stack": yigin,
            "stack_bottom_to_top": yigin_alt_ust,
            "stack_top_to_bottom": yigin_ust_alt,
            "action": action,
            "detail": detail,
        }

    def _trace_to_snapshots(self, trace, tokens):
        snapshots = []

        for index, (action, config, detail) in enumerate(trace):
            snapshots.append(
                self._make_snapshot(index, action, config, tokens, detail)
            )

        return snapshots

    def simulate(self, input_text, max_configs=20000, max_steps=80, max_stack_size=80):
        tokens = self.tokenize_input(input_text)

        start_config = Configuration(
            state=self.start_state,
            position=0,
            stack=(self.start_stack_symbol,),
        )

        start_trace = [
            (
                "Başlangıç konfigürasyonu",
                start_config,
                "Yığında başlangıç sembolü var."
            )
        ]

        queue = deque([(start_config, start_trace)])
        visited = {start_config}

        explored = 0
        last_trace = start_trace

        while queue and explored < max_configs:
            config, trace = queue.popleft()
            explored += 1
            last_trace = trace

            if self._is_accepting(config, tokens):
                return {
                    "accepted": True,
                    "message": "Girdi kabul edildi.",
                    "trace": self._trace_to_snapshots(trace, tokens),
                    "explored": explored,
                }

            if len(trace) >= max_steps:
                continue

            for transition in self._applicable_transitions(config, tokens):
                yeni_config = self._apply_transition(config, transition)

                if len(yeni_config.stack) > max_stack_size:
                    continue

                kalan_input_sayisi = len(tokens) - yeni_config.position

                if self._terminal_count_in_stack(yeni_config.stack) > kalan_input_sayisi:
                    continue

                if yeni_config in visited:
                    continue

                visited.add(yeni_config)

                label = transition.get("label") or self._transition_text(transition)
                detail = self._transition_text(transition)

                queue.append(
                    (
                        yeni_config,
                        trace + [(label, yeni_config, detail)]
                    )
                )

        return {
            "accepted": False,
            "message": "Girdi reddedildi. Kabul durumuna ulaşan geçerli yol bulunamadı.",
            "trace": self._trace_to_snapshots(last_trace, tokens),
            "explored": explored,
        }