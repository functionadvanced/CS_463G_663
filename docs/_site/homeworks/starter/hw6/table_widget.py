"""Small vector illustrations and animations for the Buckshot table."""

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap, QPolygonF, QRadialGradient, QTransform
from PySide6.QtWidgets import QPushButton, QToolButton, QWidget

from ai import BEER, CIGARETTE, HANDCUFFS, HANDSAW, MAGNIFYING_GLASS, SHOOT_OTHER, SHOOT_SELF
from buckshot import ITEM_NAMES, remaining_shells

GOLD = "#e8bd77"
LIVE = "#e47b60"
BLANK = "#92b6c4"
MUTED = "#a7b3ae"
HEAL = "#8ace9b"
SHOT_GRAB = 0.26
SHOT_FIRE = 0.50
SHOT_RETURN = 0.28
BEER_EJECT = 0.54
CUFFS_ATTACH = 0.75
CUT_BARREL = 59
JACKETS = ("#355967", "#624638")
GLOVE = "#c5a080"
PLAYER_POSITIONS = ((98, 121), (542, 121))
GUN_PARK_X = (222, 418)
GUN_Y = 116
ITEM_TRAY_X = (19, 485)
ITEM_SLOTS = 4
ITEM_Y = 242

ITEM_HINTS = {
    HANDSAW: "Double the damage of your next live shot.",
    MAGNIFYING_GLASS: "Privately inspect the chambered shell.",
    CIGARETTE: "Recover one health point.",
    BEER: "Eject the chambered shell.",
    HANDCUFFS: "Make the opponent skip their next turn.",
}


def box(painter, x, y, width, height, radius, color, outline=None):
    painter.setBrush(QColor(color))
    painter.setPen(QPen(QColor(outline), 1) if outline else Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRectF(x, y, width, height), radius, radius)


def line(painter, color, width, x1, y1, x2, y2):
    pen = QPen(QColor(color), width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def polygon(painter, color, points):
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))


def shell_art(painter, live):
    color = LIVE if live else BLANK
    box(painter, 8, 2, 16, 27, 4, color)
    box(painter, 10, 5, 3, 15, 1, "#efe4d7")
    box(painter, 7, 22, 18, 8, 2, "#c39a5f")
    line(painter, "#f0ce88", 2, 9, 28, 23, 28)


def item_art(painter, item):
    if item == HANDSAW:
        polygon(painter, "#c4d1cb", [(8, 8), (28, 8), (30, 15), (27, 14),
                                   (26, 18), (23, 16), (22, 20), (19, 18),
                                   (18, 22), (15, 20), (13, 24), (8, 23)])
        box(painter, 2, 10, 10, 15, 3, "#b87b49")
        box(painter, 5, 13, 4, 9, 2, "#302a23")
    elif item == MAGNIFYING_GLASS:
        line(painter, "#c08b55", 5, 19, 19, 27, 27)
        box(painter, 3, 3, 19, 19, 9, "#335a63", BLANK)
        line(painter, "#d1e2e7", 2, 7, 12, 11, 8)
    elif item == CIGARETTE:
        box(painter, 2, 16, 28, 7, 2, "#e8ddc4")
        box(painter, 2, 16, 8, 7, 2, "#b58655")
        box(painter, 26, 16, 4, 7, 1, LIVE)
        line(painter, "#9dafa7", 2, 27, 12, 23, 7)
    elif item == BEER:
        box(painter, 7, 4, 18, 24, 3, "#b49158")
        box(painter, 8, 5, 16, 3, 1, "#c9d2c8")
        box(painter, 8, 24, 16, 3, 1, "#c9d2c8")
        polygon(painter, "#e9d8a7", [(17, 10), (12, 17), (16, 17), (15, 22), (20, 15), (16, 15)])
    elif item == HANDCUFFS:
        line(painter, "#aebfbb", 3, 11, 14, 22, 16)
        box(painter, 2, 10, 12, 13, 5, "#536560", "#c4d1cb")
        box(painter, 18, 12, 12, 13, 5, "#536560", "#c4d1cb")
        box(painter, 5, 13, 6, 7, 3, "#202928")
        box(painter, 21, 15, 6, 7, 3, "#202928")


def icon(draw, value, size=32):
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size / 32, size / 32)
    draw(painter, value)
    painter.end()
    return pixmap


class HealthMeter(QWidget):
    def __init__(self, parent, player):
        super().__init__(parent)
        self.player = player
        self.hp = self.previous = 0
        self.maximum = 7
        self.progress = 1

    def show_health(self, hp, maximum):
        self.previous, self.hp, self.maximum = self.hp, max(0, hp), maximum
        self.setToolTip(f"{self.hp} / {maximum} health")
        self.setAccessibleName(f"Player {self.player + 1} · {self.toolTip()}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = painter.font()
        font.setPixelSize(round(self.height() * 0.7))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(MUTED))
        label_width = painter.fontMetrics().horizontalAdvance("HP") + 6
        painter.drawText(QRectF(0, 0, label_width, self.height()), Qt.AlignmentFlag.AlignVCenter, "HP")
        width = (self.width() - label_width) / self.maximum
        for point in range(self.maximum):
            color = self.segment_color(point)
            x = label_width + point * width
            box(painter, x + 1, 1, width - 3, self.height() - 2, 3, "#263332", "#485651")
            box(painter, x + 1, 1, width - 3, self.height() - 2, 3, color)

    def segment_color(self, point):
        if self.hp <= point < self.previous:
            lost = self.previous - self.hp
            # Drain from right to left, with one final beat to read the result.
            step = self.progress * (lost + 1) - (self.previous - 1 - point)
            color = QColor(HEAL if step < 0 else LIVE)
            color.setAlphaF(1 - min(1, max(0, step)))
            return color
        if self.previous <= point < self.hp:
            if self.progress < 0.48:
                return QColor("#263332")
            if self.progress < 0.84:
                return QColor("#dcf5bf")
        return QColor(HEAL if point < self.hp else "#263332")


def shotgun_art(painter, muzzle):
    polygon(painter, "#111916", [(-166, 28), (-164, 1), (-125, -11), (-56, 3),
                                 (muzzle - 9, -7), (muzzle + 2, 14), (78, 23), (-32, 22),
                                 (-60, 37), (-100, 41), (-164, 47)])
    polygon(painter, "#8f5e3c", [(-164, -7), (-130, -16), (-86, -9), (-55, -5),
                                 (-55, 14), (-78, 17), (-103, 30), (-164, 36)])
    polygon(painter, "#b88050", [(-163, -5), (-130, -13), (-65, -4), (-65, 3),
                                 (-122, 4), (-160, 17)])
    line(painter, "#4b3428", 4, -164, -5, -164, 34)
    box(painter, -64, -12, 75, 34, 6, "#667a77", "#9aaba3")
    box(painter, -28, -6, 26, 10, 2, "#283938")
    box(painter, -38, 18, 32, 13, 6, "#3e504e", "#748783")
    box(painter, -33, 21, 22, 6, 3, "#1c2926")
    box(painter, 8, -12, muzzle - 11, 13, 3, "#758b89", "#a4b4ab")
    box(painter, 18, 1, muzzle - 26, 10, 3, "#455654")
    box(painter, 18, -1, 77, 19, 4, "#966a46")
    for x in range(26, 91, 8):
        line(painter, "#634932", 2, x, 3, x, 13)
    box(painter, muzzle - 10, -14, 10, 18, 2, "#455654", "#91a29c")


def caption_text(painter, text, color, x, y, size, centered=False):
    font = QFont(painter.font())
    font.setPixelSize(size)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(color))
    if centered:
        x -= painter.fontMetrics().horizontalAdvance(text) / 2
    painter.drawText(QPointF(x, y), text)


def draw_player(painter, player, name, selected, damage, progress, reaching, cuffed, inspected):
    color = BLANK if player == 0 else GOLD
    hit = damage > 0 and 0 <= progress < 1
    painter.save()
    if hit:
        away = -1 if player == 0 else 1
        painter.translate(away * 12 * max(0, 1 - progress / 0.40), 0)

    # Two silhouettes with different jackets and visors identify the seats.
    box(painter, -48, 17, 96, 25, 12, "#1a2a25")
    box(painter, -39, -4, 78, 40, 19, JACKETS[player], color)
    box(painter, -22, -42, 44, 49, 17, "#24343b" if player == 0 else "#362c29", color)
    box(painter, -17, -30, 34, 16, 6, "#182523")
    line(painter, color, 3, -11, -23, -3, -23)
    line(painter, color, 3, 3, -23, 11, -23)
    if cuffed:
        box(painter, -26, 15, 20, 13, 5, GLOVE)
        box(painter, 6, 15, 20, 13, 5, GLOVE)
        draw_item(painter, HANDCUFFS, 0, 18, 1.4)
    else:
        if not reaching or player == 0:
            box(painter, -36, 15, 20, 13, 5, GLOVE)
        if not reaching or player == 1:
            box(painter, 16, 15, 20, 13, 5, GLOVE)

    if hit:
        flash = QColor(LIVE)
        flash.setAlphaF(0.64 * max(0, 1 - progress / 0.48))
        box(painter, -39, -4, 78, 40, 19, flash)
        box(painter, -22, -42, 44, 49, 17, flash)
    painter.restore()

    if selected:
        box(painter, -76, 46, 152, 21, 5, "#263a30", GOLD)
    caption_text(painter, name, color, 0, 61, 12, centered=True)
    if inspected:
        draw_item(painter, MAGNIFYING_GLASS, 37, -14, 0.58)
    if cuffed:
        caption_text(painter, "HANDCUFFED", "#e0ddd0", 0, 77, 10, centered=True)
    if hit:
        # Keep the damage readable after the brief impact flash has passed.
        painter.setOpacity(min(1, (1 - progress) * 4))
        y = -83 - 8 * progress
        box(painter, -31, y - 19, 62, 25, 9, "#622f27", LIVE)
        caption_text(painter, f"−{damage} HP", "#ffdfcb", 0, y - 2, 15, centered=True)
        painter.setOpacity(1)


def draw_item(painter, item, x, y, scale=1, angle=0):
    painter.save()
    painter.translate(x, y)
    painter.rotate(angle)
    painter.scale(scale, scale)
    painter.translate(-16, -16)
    item_art(painter, item)
    painter.restore()


class TableWidget(QWidget):
    def __init__(self, on_action):
        super().__init__()
        self.setMinimumSize(560, 237)
        self.shells = (0, 0)
        self.effect = None
        self.shell = None
        self.actor = None
        self.shooter = None
        self.cuffed = self.previous_cuffs = (False, False)
        self.short = self.previous_short = False
        self.target = None
        self.damage = 0
        self.progress = 1
        self.current = None
        self.highlighted = None
        self.modes = (None, None)
        self.inspected = (False, False)
        self.meters = [HealthMeter(self, player) for player in range(2)]
        self.portraits = []
        for player in range(2):
            portrait = QPushButton(self)
            portrait.setObjectName("portrait")
            portrait.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            portrait.setEnabled(False)
            portrait.clicked.connect(
                lambda checked=False, player=player:
                on_action(SHOOT_SELF if player == self.highlighted else SHOOT_OTHER)
            )
            self.portraits.append(portrait)
        self.reset_items()
        self.item_icons = {}
        for item in ITEM_NAMES:
            art = icon(item_art, item)
            item_icon = QIcon(art)
            item_icon.addPixmap(art, QIcon.Mode.Disabled)
            self.item_icons[item] = item_icon

        self.item_buttons = []
        for player in range(2):
            row = []
            for slot in range(ITEM_SLOTS):
                button = QToolButton(self)
                button.setObjectName("item")
                button.setEnabled(False)
                button.hide()
                button.clicked.connect(
                    lambda checked=False, player=player, slot=slot:
                    on_action(self.inventory[player][slot], slot)
                )
                row.append(button)
            self.item_buttons.append(row)

    def reset_items(self):
        self.inventory = [[None] * ITEM_SLOTS for _ in range(2)]
        self.dealt = []
        self.used_from = None

    def item_position(self, player, slot):
        return ITEM_TRAY_X[player] + 20 + 32 * slot, ITEM_Y

    def resizeEvent(self, event):
        super().resizeEvent(event)
        sx, sy = self.width() / 640, self.height() / 280
        for (x, y), meter, portrait in zip(PLAYER_POSITIONS, self.meters, self.portraits):
            meter.setGeometry(round((x - 66) * sx), round((y - 66) * sy),
                              round(132 * sx), round(14 * sy))
            portrait.setGeometry(round((x - 49) * sx), round((y - 45) * sy),
                                 round(98 * sx), round(87 * sy))
        for player, row in enumerate(self.item_buttons):
            for slot, button in enumerate(row):
                x, y = self.item_position(player, slot)
                button.setGeometry(round((x - 14) * sx), round((y - 14) * sy),
                                   round(28 * sx), round(28 * sy))
                size = round(23 * min(sx, sy))
                button.setIconSize(QSize(size, size))

    def set_legal_actions(self, player, legal):
        self.highlighted = player
        self.update()
        for index, portrait in enumerate(self.portraits):
            action = SHOOT_SELF if index == player else SHOOT_OTHER
            label = f"Shoot Player {index + 1}" + (" (yourself)" if index == player else "")
            portrait.setAccessibleName(label)
            portrait.setToolTip(label)
            portrait.setEnabled(action in legal)
            if portrait.isEnabled():
                portrait.setCursor(Qt.CursorShape.CrossCursor)
            else:
                portrait.unsetCursor()
        for index, row in enumerate(self.item_buttons):
            for slot, button in enumerate(row):
                button.setEnabled(index == player and self.inventory[index][slot] in legal)

    def set_progress(self, progress):
        self.progress = progress
        health_progress = 1 if self.effect == "reload" else progress
        if self.target is not None:
            health_progress = (progress - SHOT_FIRE) / (1 - SHOT_FIRE)
        for meter in self.meters:
            meter.progress = health_progress
            meter.update()
        arrived = int(progress * len(self.dealt))
        in_flight = {(player, slot) for player, slot, item in self.dealt[arrived:]}
        for player, row in enumerate(self.item_buttons):
            for slot, button in enumerate(row):
                visible = self.inventory[player][slot] is not None and (player, slot) not in in_flight
                button.setVisible(visible)
        self.update()

    def update_state(self, state, modes, effect, shell, player, target, damage, item_slot):
        remaining = remaining_shells(state)
        # Display counts only. Grouping by type keeps the actual order hidden.
        self.shells = (remaining.count(1), remaining.count(0))
        self.effect, self.shell = effect, shell
        self.actor = player
        self.current = state.current_player
        self.modes = modes
        self.inspected = tuple(shell != -1 for shell in state.knows_shell)
        for meter, hp in zip(self.meters, state.hp):
            meter.show_health(hp, state.max_hp)
        self.shooter = player if target is not None else None
        self.previous_cuffs, self.cuffed = self.cuffed, tuple(state.skip_next)
        self.previous_short = self.short
        self.short = state.saw_active[state.current_player]
        self.target, self.damage = target, damage
        self.update_items(state, item_slot)

    def update_items(self, state, item_slot):
        self.dealt = []
        self.used_from = None
        if self.effect in ITEM_NAMES:
            slots = self.inventory[self.actor]
            if item_slot is None:
                item_slot = slots.index(self.effect)
            self.used_from = self.item_position(self.actor, item_slot)
            slots[item_slot] = None

        for player, slots in enumerate(self.inventory):
            for item in ITEM_NAMES:
                received = state.inventory[player][item] - slots.count(item)
                for _ in range(received):
                    slot = slots.index(None)
                    slots[slot] = item
                    if self.effect == "reload":
                        self.dealt.append((player, slot, item))

            for item, button in zip(slots, self.item_buttons[player]):
                if item is not None:
                    name = ITEM_NAMES[item].capitalize()
                    button.setIcon(self.item_icons[item])
                    button.setToolTip(f"{name} · {ITEM_HINTS[item]}")
                    button.setAccessibleName(name)

        # Alternate seats while dealing to empty slots at the start.
        self.dealt.sort(key=lambda entry: (entry[1], entry[0]))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.scale(self.width() / 640, self.height() / 280)
        felt = QRadialGradient(320, 140, 390)
        felt.setColorAt(0, QColor("#345346"))
        felt.setColorAt(1, QColor("#1a2c26"))
        painter.setPen(QPen(QColor("#6d7d5f"), 1))
        painter.setBrush(felt)
        painter.drawRoundedRect(QRectF(1, 1, 638, 278), 13, 13)
        painter.setPen(QPen(QColor("#476354"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(8, 8, 624, 264), 9, 9)

        for player, x in enumerate(ITEM_TRAY_X):
            box(painter, x, 204, 136, 60, 8, "#182923", "#496253")
            color = BLANK if player == 0 else GOLD
            caption_text(painter, f"P{player + 1} ITEMS", color, x + 10, 222, 12)
        self.draw_shell_tray(painter)
        shot_progress = (self.progress - SHOT_FIRE) / (1 - SHOT_FIRE)
        for player, (x, y) in enumerate(PLAYER_POSITIONS):
            painter.save()
            painter.translate(x, y)
            hit = self.damage if player == self.target else 0
            reaching = player == self.shooter and self.progress < 1
            cuffed = self.cuffed[player]
            if self.effect == HANDCUFFS and self.progress < CUFFS_ATTACH:
                cuffed = self.previous_cuffs[player]
            if self.shooter is not None and self.progress < 0.80:
                cuffed = self.previous_cuffs[player]
            name = f"PLAYER {player + 1}"
            if self.modes[player]:
                name += f" · {self.modes[player]}"
            draw_player(painter, player, name, player == self.highlighted, hit,
                        shot_progress, reaching, cuffed, self.inspected[player])
            painter.restore()
        self.draw_shotgun(painter, shot_progress)
        if self.effect in ITEM_NAMES and self.progress < 1:
            self.draw_item_use(painter)
        if self.dealt and self.progress < 1:
            self.draw_deal(painter)

    def draw_shell_tray(self, painter):
        live, blank = self.shells
        firing = self.shooter is not None and self.progress < SHOT_FIRE
        ejecting = self.effect == BEER and self.progress < BEER_EJECT
        if firing or ejecting:
            live += self.shell == 1
            blank += self.shell == 0
        box(painter, 166, 204, 303, 60, 8, "#182923", "#496253")
        caption_text(painter, "SHELLS", MUTED, 178, 222, 12)
        caption_text(painter, f"{live} LIVE", LIVE, 334, 222, 12)
        caption_text(painter, f"{blank} BLANK", BLANK, 392, 222, 12)
        for slot in range(7):
            x = 190 + slot * 37
            box(painter, x, 229, 31, 29, 4, "#253d32")
            if slot < live + blank:
                painter.save()
                painter.translate(x + 3, 231)
                painter.scale(0.78, 0.80)
                if self.effect == "reload":
                    painter.setOpacity(self.progress)
                    painter.translate(0, -14 * (1 - self.progress))
                shell_art(painter, slot < live)
                painter.restore()

    def draw_shotgun(self, painter, shot_progress):
        progress = self.progress
        angle, recoil = -90, 0
        parked_x = GUN_PARK_X[self.current] if self.current is not None else 320
        gun_x = parked_x
        returning = 0
        holding = self.shooter is not None and progress < 1
        if holding:
            # Reach first, then bring the shotgun closer while turning it.
            aim = min(max(0, (progress - SHOT_GRAB) / (SHOT_FIRE - SHOT_GRAB)),
                      1, (1 - progress) / SHOT_RETURN)
            swing = math.sin(aim * math.pi / 2)
            angle += (-90 if self.target == 0 else 90) * swing
            returning = max(0, (progress - (1 - SHOT_RETURN)) / SHOT_RETURN)
            handoff = max(0, (returning - 0.40) / 0.60)
            shooter_x = GUN_PARK_X[self.shooter]
            gun_x = shooter_x + (parked_x - shooter_x) * handoff
            gun_x += (-18 if self.shooter == 0 else 18) * swing
            if shot_progress >= 0:
                recoil = 20 * max(0, 1 - shot_progress / 0.35)

        pose = QTransform()
        pose.translate(gun_x, GUN_Y)
        pose.rotate(angle)
        # A left-facing gun is mirrored so its trigger remains underneath.
        facing_left = self.target == 0 if holding else self.current == 1
        pose.scale(0.52, -0.52 if facing_left else 0.52)
        pose.translate(-recoil, 0)

        if holding:
            seat_x, seat_y = PLAYER_POSITIONS[self.shooter]
            hand_x = seat_x + (26 if self.shooter == 0 else -26)
            hand_y = seat_y + 21
            grip = pose.map(QPointF(-24, 14))
            reach = min(progress / SHOT_GRAB, max(0, 1 - returning / 0.40))
            glove_x = hand_x + (grip.x() - hand_x) * reach
            glove_y = hand_y + (grip.y() - hand_y) * reach
            elbow_x = (hand_x + glove_x) / 2
            elbow_y = (hand_y + glove_y) / 2 + 16 * reach
            sleeve = JACKETS[self.shooter]
            line(painter, sleeve, 17, hand_x, hand_y, elbow_x, elbow_y)
            line(painter, sleeve, 15, elbow_x, elbow_y, glove_x, glove_y)

        painter.save()
        painter.setWorldTransform(pose, True)
        muzzle = self.barrel_end()
        shotgun_art(painter, muzzle)
        if self.target is not None and 0 <= shot_progress < 0.32:
            flash = QColor("#ffd081" if self.shell else BLANK)
            flash.setAlphaF(1 - shot_progress / 0.32)
            painter.translate(muzzle - 173, 0)
            if self.shell:
                polygon(painter, flash, [(173, -10), (210, -28), (206, -11), (256, -4),
                                         (207, 5), (218, 19), (173, 4)])
            else:
                box(painter, 174 + 30 * shot_progress, -14, 25, 21, 10, flash)
        painter.restore()

        if holding:
            box(painter, glove_x - 10, glove_y - 6, 20, 13, 5, GLOVE, "#8c6b55")
            line(painter, "#8c6b55", 1, glove_x + 4, glove_y - 3, glove_x + 4, glove_y + 3)

        shell_progress = shot_progress
        if self.effect == BEER:
            shell_progress = (progress - BEER_EJECT) / (1 - BEER_EJECT)
        if self.shell is not None and 0 <= shell_progress < 1:
            painter.save()
            chamber = pose.map(QPointF(-15, -4))
            painter.translate(chamber.x() - 16 + 46 * shell_progress,
                              chamber.y() - 16 - 34 * math.sin(math.pi * shell_progress))
            painter.rotate(100 * shell_progress)
            painter.setOpacity(1 - shell_progress)
            shell_art(painter, self.shell)
            painter.restore()

    def barrel_end(self):
        if self.effect == HANDSAW and not self.previous_short:
            cut = max(0, min(1, (self.progress - 0.58) / 0.18))
            return 173 - CUT_BARREL * cut
        shortened = self.previous_short if self.shooter is not None and self.progress < 1 else self.short
        return 173 - CUT_BARREL if shortened else 173

    def draw_item_use(self, painter):
        item = self.effect
        progress = self.progress
        seat_x, seat_y = PLAYER_POSITIONS[self.actor]
        inward = 1 if self.actor == 0 else -1
        source_x, source_y = self.used_from
        gun_x = GUN_PARK_X[self.actor]

        if item == HANDCUFFS:
            if progress < CUFFS_ATTACH:
                travel = progress / CUFFS_ATTACH
                other_x, other_y = PLAYER_POSITIONS[1 - self.actor]
                x = source_x + (other_x - source_x) * travel
                y = source_y + (other_y + 18 - source_y) * travel - 38 * math.sin(math.pi * travel)
                draw_item(painter, item, x, y, 0.75 + 0.60 * travel)
            return

        painter.save()
        painter.setOpacity(min(1, (1 - progress) * 7))
        reach = min(1, progress / 0.34)
        scale = 0.75 + 0.60 * reach
        if item == HANDSAW:
            x = source_x + (gun_x - source_x) * reach
            cut_y = GUN_Y - 59
            y = source_y + (cut_y - source_y) * reach
            x += 15 * math.sin(32 * progress) * reach
            draw_item(painter, item, x, y, scale, 12 * reach)
            if 0.48 <= progress <= 0.78:
                for dx, dy in ((-13, -7), (9, -10), (12, 7)):
                    line(painter, GOLD, 2, gun_x + dx / 2, cut_y + dy / 2, gun_x + dx, cut_y + dy)
        elif item == MAGNIFYING_GLASS:
            x = source_x + (gun_x - source_x) * reach
            y = source_y + (GUN_Y - source_y) * reach
            draw_item(painter, item, x + 9 * reach, y + 9 * reach, scale)
            if reach == 1:
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(QColor(BLANK), 2))
                radius = 15 + 14 * (progress - 0.34)
                painter.drawEllipse(QPointF(x, y), radius, radius)
        else:
            # Bring the cigarette or beer up to the player's visor.
            x = source_x + (seat_x + 13 * inward - source_x) * reach
            y = source_y + (seat_y - 13 - source_y) * reach
            angle = (-58 * inward * reach) if item == BEER else 0
            draw_item(painter, item, x, y, 0.75 + 0.35 * reach, angle)
            if item == CIGARETTE and progress >= 0.38:
                smoke = (progress - 0.38) / 0.62
                painter.setOpacity(1 - smoke)
                for puff in range(3):
                    radius = 3 + 3 * smoke + puff
                    box(painter, x + 10 + 6 * puff * inward, y - 11 - 26 * smoke - 6 * puff,
                        2 * radius, 2 * radius, radius, "#c4d1cb")
        painter.restore()

    def draw_deal(self, painter):
        phase = self.progress * len(self.dealt)
        index = int(phase)
        player, slot, item = self.dealt[index]
        travel = phase - index
        x, y = self.item_position(player, slot)
        box(painter, 282, 20, 76, 30, 7, "#182923", "#496253")
        caption_text(painter, "DEALING", GOLD, 320, 39, 11, centered=True)
        draw_item(painter, item, 320 + (x - 320) * travel,
                  54 + (y - 54) * travel, 0.90 - 0.15 * travel)
