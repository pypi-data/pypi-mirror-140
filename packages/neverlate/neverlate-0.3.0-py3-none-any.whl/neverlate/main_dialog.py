# pylint: disable=no-name-in-module
"""Main dialog with the Table view of events."""
from __future__ import annotations

import typing
import webbrowser
from datetime import timedelta

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QCursor, QFont
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from neverlate.utils import get_icon, now_datetime, pretty_datetime

if typing.TYPE_CHECKING:
    from PySide6.QtCore import QEvent

    from neverlate.event_alerter import EventAlerter

# Table columns
TABLE_SUMMARY = 0
TABLE_TIME_TILL_ALERT = 1
TABLE_EVENT_TIMES = 2
TABLE_CALENDAR = 3

# Colors
BLACK = QColor(*(3 * [0]))
DARK_GREY = QColor(*(3 * [50]))
LIGHT_GREY = QColor(*(3 * [200]))
LIGHT_GREEN = QColor(200, 255, 200)
LIGHT_RED = QColor(255, 200, 200)
LIGHT_YELLOW = QColor(255, 255, 200)
WHITE = QColor(*(3 * [255]))


class MainDialog(QDialog):
    """Main dialog to show general info."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NeverLate")
        self.setWindowIcon(get_icon("tray_icon.png"))

        # Right click menu for the QTable
        self.table_menu = QMenu(self)
        self.label_section = self.table_menu.addAction(
            "<Event Summary>"
        )  # type: QAction
        self.label_section.setEnabled(False)
        font = self.label_section.font()
        font.setBold(True)
        self.label_section.setFont(font)
        self.table_menu.addSeparator()

        self.join_meeting_action = self.table_menu.addAction("Join Meeting")
        self.join_meeting_action.setIcon(get_icon("video.png"))
        self.trigger_alert_action = self.table_menu.addAction("Reset/Retrigger Alert")
        self.trigger_alert_action.setIcon(get_icon("alarm.png"))

        self.update_now_button = QPushButton("Update Now")
        self.time_to_update_label = QLabel()
        self.row_to_event_alerter = {}  # type: dict[int, EventAlerter]

        self.event_table = QTableWidget(0, 4)
        self.event_table.setHorizontalHeaderItem(
            TABLE_SUMMARY, QTableWidgetItem("Event")
        )
        self.event_table.setHorizontalHeaderItem(
            TABLE_EVENT_TIMES, QTableWidgetItem("Time")
        )
        self.event_table.setHorizontalHeaderItem(
            TABLE_TIME_TILL_ALERT, QTableWidgetItem("Tim Till Alert")
        )
        self.event_table.setHorizontalHeaderItem(
            TABLE_CALENDAR, QTableWidgetItem("Calendar")
        )

        # self.event_table.horizontalHeader().hide()
        self.event_table.verticalHeader().hide()
        self.event_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.event_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.event_table.horizontalHeader().setStretchLastSection(True)
        self.event_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.event_table.setSelectionMode(QTableWidget.NoSelection)
        self.event_table.setFocusPolicy(Qt.NoFocus)
        self.event_table.contextMenuEvent = self.table_context_menu
        # table->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.event_table)
        # main_layout.addStretch()

        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.time_to_update_label)
        layout.addWidget(self.update_now_button)

        main_layout.addLayout(layout)
        self.setLayout(main_layout)

    def join_meeting(self, alerter: EventAlerter):
        """Join a meeting - opening a browser to the given URL"""
        url = alerter.time_event.get_video_url()
        if url:
            webbrowser.open(url, autoraise=True)

            # Dismiss alert dialogs
            if alerter.has_alerted:
                alerter.close_pop_up()

    def table_context_menu(self, event: QEvent):
        """
        Display the right-click context menu - letting a user join a meeting directly,
        or re-trigger an alert.

        Args:
            event (QEvent): Event triggered
        """
        row = self.event_table.rowAt(event.pos().y())
        alerter = self.row_to_event_alerter.get(row)
        if alerter is None:
            # This should not happen...
            return

        self.label_section.setText(alerter.time_event.summary)

        # Trigger alert
        self.trigger_alert_action.setEnabled(alerter.has_alerted)
        self.trigger_alert_action.triggered.connect(alerter.reset_alert)

        # Join meeting
        url = alerter.time_event.get_video_url()
        self.join_meeting_action.setEnabled(bool(url))
        self.join_meeting_action.setText(
            "Join Meeting (Google Meet)" if "meet.google" in url else "Join Meeting"
        )
        self.join_meeting_action.triggered.connect(lambda: self.join_meeting(alerter))

        self.table_menu.popup(QCursor.pos())

    def update_table_with_events(self, alerters: list[EventAlerter]):
        """Update the table with the specified alerter events."""
        # TODO: break this function up
        orig_row_count = self.event_table.rowCount()
        self.event_table.setRowCount(len(alerters))
        alerters.sort(key=lambda a: a.time_event.start_time)
        now = now_datetime()
        self.row_to_event_alerter.clear()
        for idx, alerter in enumerate(alerters):
            self.row_to_event_alerter[idx] = alerter

            self.event_table.setItem(
                idx, TABLE_SUMMARY, QTableWidgetItem(alerter.time_event.summary)
            )

            # Start time
            start_label = pretty_datetime(alerter.time_event.start_time).split()[0]
            end_label = pretty_datetime(alerter.time_event.end_time)
            self.event_table.setItem(
                idx,
                TABLE_EVENT_TIMES,
                QTableWidgetItem(f"{start_label} - {end_label}"),
            )

            # Time till alert
            time_till_alert = alerter.time_till_alert()
            if time_till_alert <= 0:
                time_till_alert = "---"
            else:
                min_, secs = divmod(time_till_alert, 60)
                hours, min_ = divmod(min_, 60)
                if hours:
                    secs = str(secs).zfill(2)
                    min_ = str(min_).zfill(2)
                    time_till_alert = f"{hours}:{min_}:{secs}"
                else:
                    secs = str(secs).zfill(2)
                    time_till_alert = f"{min_}:{secs}"

                time_till_alert = str(time_till_alert)

            # Set the base text
            self.event_table.setItem(
                idx, TABLE_TIME_TILL_ALERT, QTableWidgetItem(time_till_alert)
            )

            # Calendar
            self.event_table.setItem(
                idx,
                TABLE_CALENDAR,
                QTableWidgetItem(alerter.time_event.calendar.summary),
            )

            # =================== Styles =====================
            if alerter.time_event.has_declined():
                # User declined. Set strikethrough font & italic
                # for column in range(self.event_table.columnCount()):
                item = self.event_table.item(idx, TABLE_SUMMARY)
                font = QFont()
                font.setItalic(True)
                font.setStrikeOut(True)
                item.setFont(font)
            if now > alerter.time_event.end_time:
                # Meeting is over. 'Disable' it.
                for column in range(self.event_table.columnCount()):
                    item = self.event_table.item(idx, column)
                    background = item.background()
                    background.setColor(LIGHT_GREY)
                    foreground = item.foreground()
                    foreground.setColor(DARK_GREY)
                    background.setStyle(Qt.BrushStyle.SolidPattern)
                    foreground.setStyle(Qt.BrushStyle.SolidPattern)
                    item.setBackground(background)
                    item.setForeground(foreground)
            elif alerter.time_event.start_time < now < alerter.time_event.end_time:
                # Meeting is happening
                for column in range(self.event_table.columnCount()):
                    if alerter.dismissed_alerts:  # User is in the meeting (in theory)
                        bg_color = LIGHT_GREEN  # Light green
                    else:  # User should be in th emeeting
                        bg_color = LIGHT_RED
                    item = self.event_table.item(idx, column)
                    background = item.background()
                    foreground = item.foreground()
                    foreground.setColor(BLACK)
                    background.setColor(bg_color)
                    background.setStyle(Qt.BrushStyle.SolidPattern)
                    foreground.setStyle(Qt.BrushStyle.SolidPattern)
                    item.setBackground(background)
                    item.setForeground(foreground)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            elif now + timedelta(minutes=30) > alerter.time_event.start_time:
                # Meeting is coming up soon
                for column in range(self.event_table.columnCount()):
                    item = self.event_table.item(idx, column)
                    background = item.background()
                    background.setColor(LIGHT_YELLOW)
                    foreground = item.foreground()
                    foreground.setColor(BLACK)
                    background.setStyle(Qt.BrushStyle.SolidPattern)
                    foreground.setStyle(Qt.BrushStyle.SolidPattern)
                    item.setBackground(background)
                    item.setForeground(foreground)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            else:
                # Future event
                for column in range(self.event_table.columnCount()):
                    item = self.event_table.item(idx, column)
                    background = item.background()
                    background.setColor(WHITE)
                    foreground = item.foreground()
                    foreground.setColor(BLACK)
                    background.setStyle(Qt.BrushStyle.SolidPattern)
                    foreground.setStyle(Qt.BrushStyle.SolidPattern)
                    item.setBackground(background)
                    item.setForeground(foreground)
                    font = item.font()
                    item.setFont(font)

        # self.event_table.resizeColumnsToContents()
        if orig_row_count != len(alerters):
            self.adjustSize()
