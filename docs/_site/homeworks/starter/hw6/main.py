import random
import sys
from pathlib import Path

import torch

from PySide6.QtCore import Qt, QTimer, QVariantAnimation
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ai import BEER, MAGNIFYING_GLASS, RLAgent, RandomAgent, SHOOT_OTHER, SHOOT_SELF
from buckshot import (
    ITEM_NAMES,
    State,
    apply_action,
    current_shell,
    legal_actions,
    needs_reload,
    observation,
    reload_shotgun,
    remaining_shells,
)
from table_widget import TableWidget, icon, shell_art

ACTION_NAMES = {
    **{item: name.capitalize() for item, name in ITEM_NAMES.items()},
    SHOOT_SELF: "Shoot self",
    SHOOT_OTHER: "Shoot opponent",
}
PLAYER_TYPES = {"Human": None, "Random": RandomAgent, "Actor-Critic": RLAgent}

STYLE = """
QWidget { background: #121917; color: #eae5d5; font-size: 13px; }
QLabel, QToolButton { background: transparent; }
QLabel#eyebrow { color: #b3bfb6; font-size: 11px; font-weight: bold; }
QLabel#turn { color: #f0ce88; font-size: 15px; font-weight: bold; }
QFrame#log { background: #1b2622; border: 1px solid #394b43; border-radius: 9px; }
QPushButton, QToolButton#item {
    background: #26342e; border: 1px solid #506158; border-radius: 7px; padding: 6px 12px;
}
QToolButton#item { padding: 0; border-color: #8b7953; }
QPushButton:hover, QToolButton#item:hover {
    background: #394940; border-color: #e8bd77;
}
QPushButton:focus, QToolButton#item:focus { border-color: #e8bd77; }
QPushButton:disabled, QToolButton#item:disabled {
    background: #1c2723; border-color: #364640; color: #a7b3ae;
}
QPushButton#portrait {
    background: transparent; border: 1px solid transparent; border-radius: 10px; padding: 0;
}
QPushButton#portrait:enabled:hover, QPushButton#portrait:enabled:focus {
    border-color: #e8bd77;
}
QPlainTextEdit {
    background: #1b2622; border: 0; padding: 4px; font-size: 12px;
    selection-background-color: #3c5045; selection-color: #fff4db;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HW6 Game")
        self.resize(1020, 550)
        self.setStyleSheet(STYLE)
        self.finished = True
        self.after_animation = None

        self.timer = QTimer(self, interval=320, singleShot=True)
        self.timer.timeout.connect(self.play_ai)
        self.animation = QVariantAnimation(self, startValue=0.0, endValue=1.0)
        self.animation.finished.connect(self.animation_done)

        menu = self.menuBar().addMenu("Game")
        self.new_action = menu.addAction("New Game", self.new_game)
        self.new_action.setShortcut("Ctrl+N")

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(18, 14, 18, 16)
        outer.setSpacing(12)

        layout = QHBoxLayout()
        layout.setSpacing(12)
        outer.addLayout(layout, 1)
        game = QVBoxLayout()
        game.setSpacing(8)
        layout.addLayout(game, 1)
        self.table = TableWidget(self.play)
        self.animation.valueChanged.connect(self.table.set_progress)
        game.addWidget(self.table, 1)

        controls = QHBoxLayout()
        self.turn = self.add_label(controls, "Choose New Game to start", "turn")
        controls.addStretch()
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about)
        controls.addWidget(self.about_button)
        self.new_button = QPushButton("New Game")
        self.new_button.clicked.connect(self.new_game)
        controls.addWidget(self.new_button)
        game.addLayout(controls)

        log = QFrame()
        log.setObjectName("log")
        log.setFixedWidth(226)
        log_layout = QVBoxLayout(log)
        self.add_label(log_layout, "MOVE LOG", "eyebrow")
        self.history = QPlainTextEdit()
        self.history.setAccessibleName("Full move log")
        self.history.setReadOnly(True)
        self.history.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        log_layout.addWidget(self.history)
        layout.addWidget(log)

    def add_label(self, layout, text, name):
        label = QLabel(text)
        label.setObjectName(name)
        layout.addWidget(label)
        return label

    def show_about(self):
        resume_ai = self.timer.isActive()
        self.timer.stop()
        about = QMessageBox(self)
        about.setWindowTitle("About HW6 Game")
        about.setTextFormat(Qt.TextFormat.RichText)
        about.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        about.setText(
            "<p>This game is for educational use only.</p>"
            "<p>Course version by Peizhong Ju, with assistance from OpenAI Codex.</p>"
            '<p>Inspired by <a href="https://store.steampowered.com/app/2835570/BuckshotRoulette/">'
            "Buckshot Roulette on Steam</a>, developed by Mike Klubnika "
            "and published by CRITICAL REFLEX.</p>"
        )
        about.exec()
        about.deleteLater()
        if resume_ai:
            self.timer.start()

    def new_game(self):
        self.timer.stop()
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        form = QFormLayout(dialog)
        selectors = [QComboBox(), QComboBox()]
        for player, selector in enumerate(selectors, start=1):
            selector.addItems(PLAYER_TYPES.keys())
            form.addRow(f"Player {player}", selector)
        selectors[1].setCurrentText("Random")
        save = QPushButton("Save Settings")
        save.clicked.connect(dialog.accept)
        form.addRow(save)
        if not dialog.exec():
            if not self.finished:
                self.ready()
            return

        modes = [selector.currentText() for selector in selectors]
        try:
            weights = None
            if "Actor-Critic" in modes:
                checkpoint = Path("agent.pt")
                if not checkpoint.is_file():
                    raise FileNotFoundError("Complete ai.py and run python train.py in this folder first.")
                weights = torch.load(checkpoint, map_location="cpu", weights_only=True)
            agents = [None if mode == "Human" else PLAYER_TYPES[mode]() for mode in modes]
            for mode, agent in zip(modes, agents):
                if mode == "Actor-Critic":
                    agent.actor.load_state_dict(weights["actor"])
                    agent.critic.load_state_dict(weights["critic"])
                    agent.actor.eval()
                    agent.critic.eval()
        except Exception as error:
            QMessageBox.warning(self, "Could not start game", str(error))
            if not self.finished:
                self.ready()
            return

        self.agents = agents
        self.modes = modes
        self.table.reset_items()
        self.state = State(max_hp=7, rng=random.Random())
        self.finished = False
        self.decisions = 0
        self.history.clear()
        self.log(f"Player 1 ({modes[0]}) vs. Player 2 ({modes[1]})")
        self.ready()

    def log(self, message):
        if not self.history.document().isEmpty():
            message = "\n" + message
        self.history.appendPlainText(message)

    def ready(self):
        state = self.state
        player = state.current_player
        if needs_reload(state):
            reload_shotgun(state)
            shells = remaining_shells(state)
            self.log(f"Reload · {shells.count(1)} live, {shells.count(0)} blank · Items dealt")
            self.turn.setText("Reloading…")
            self.present("reload", None, self.ready)
            return

        self.set_navigation_enabled(True)
        human = self.agents[player] is None
        turn = f"Player {player + 1}'s turn"
        self.turn.setText(f"{turn} · Click a portrait to shoot" if human else turn)
        self.set_controls(legal_actions(state, player) if human else ())
        if not human:
            self.timer.start()

    def set_controls(self, legal, player=None):
        if player is None and not self.finished:
            player = self.state.current_player
        self.table.set_legal_actions(player, legal)

    def set_navigation_enabled(self, enabled):
        self.new_action.setEnabled(enabled)
        self.new_button.setEnabled(enabled)
        self.about_button.setEnabled(enabled)

    def present(self, effect, shell, after, *, player=None, target=None, damage=0, item_slot=None):
        self.after_animation = after
        self.set_controls((), player)
        self.set_navigation_enabled(False)
        self.table.update_state(self.state, self.modes, effect, shell, player, target, damage, item_slot)
        if target is not None:
            duration = 1050 + 200 * damage
        elif effect in ITEM_NAMES:
            duration = 1000
        else:
            duration = max(360, 310 * len(self.table.dealt))
        self.animation.setDuration(duration)
        self.table.set_progress(0.0)
        self.animation.start()

    def animation_done(self):
        # Let Qt finish this animation tick before opening a dialog or starting another move.
        QTimer.singleShot(0, self.finish_animation)

    def finish_animation(self):
        after = self.after_animation
        self.after_animation = None
        after()

    def end_game(self, message):
        self.finished = True
        self.timer.stop()
        self.set_controls(())
        self.set_navigation_enabled(True)
        self.turn.setText(message)
        self.log(message)

    def play_ai(self):
        player = self.state.current_player
        try:
            action = self.agents[player].choose_action(observation(self.state, player))
            self.play(action)
        except Exception as error:
            self.end_game(f"Player {player + 1} ({self.modes[player]}): {error}")

    def play(self, action, item_slot=None):
        if self.finished or self.after_animation is not None:
            return
        state = self.state
        player = state.current_player
        other = 1 - player
        agent = self.agents[player]
        hp_before = state.hp.copy()
        cuffs_before = state.skip_next[other]
        target = None
        if action in (SHOOT_SELF, SHOOT_OTHER):
            target = player if action == SHOOT_SELF else other
        shell = current_shell(state) if target is not None or action == BEER else None
        reward = apply_action(state, action)
        self.decisions += 1

        message = f"{self.decisions:03d} · P{player + 1} · {ACTION_NAMES[action]}"
        if shell is not None:
            message += " · Live shell" if shell else " · Blank shell"
        for index, old_hp in enumerate(hp_before):
            change = state.hp[index] - old_hp
            if change:
                message += f" · P{index + 1} {change:+} HP"
        if cuffs_before and not state.skip_next[other]:
            message += f" · P{other + 1} skips turn"
        if agent is not None:
            agent.see_result(reward, observation(state, player), False)
        if reward and self.agents[other] is not None:
            self.agents[other].see_result(-reward, observation(state, other), False)

        def finish_move():
            self.log(message)
            if reward:
                winner = player if reward == 1 else other
                self.end_game(f"Player {winner + 1} wins!")
                self.table.set_legal_actions(winner, ())
            elif self.decisions >= 500:
                self.end_game("Game ended after 500 decisions.")
            elif action == MAGNIFYING_GLASS and agent is None:
                self.show_shell(player, state.knows_shell[player] == 1)
            else:
                self.ready()

        self.turn.setText(f"P{player + 1} · {ACTION_NAMES[action]}")
        damage = hp_before[target] - state.hp[target] if target is not None else 0
        self.present(action, shell, finish_move, player=player, target=target, damage=damage, item_slot=item_slot)

    def show_shell(self, player, live):
        reveal = QMessageBox(self)
        reveal.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        reveal.setWindowTitle(f"Player {player + 1} · Magnifying glass")
        reveal.setText("Live shell" if live else "Blank shell")
        reveal.setIconPixmap(icon(shell_art, live, 56))
        reveal.setStandardButtons(QMessageBox.StandardButton.Ok)
        reveal.finished.connect(lambda _result: QTimer.singleShot(0, self.ready))
        reveal.open()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.new_game()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
