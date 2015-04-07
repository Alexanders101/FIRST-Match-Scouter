__author__ = 'alex'

import sys
import os
import webbrowser as web
from urllib.error import URLError
from time import sleep

import joblib
import numpy as np
from PySide.QtGui import *
from PySide.QtCore import *

import main_window
import start_window
import add_window
from utils import *
import Blue_Alliance_API


if getattr(sys, 'frozen', False):
    # frozen
    FILE_PATH = os.path.dirname(sys.executable)
else:
    # unfrozen
    FILE_PATH = os.path.dirname(os.path.realpath(__file__))

DATABASE_FILE = FILE_PATH + '/scouting_database.db'
SAVED = os.path.isfile(DATABASE_FILE)


class MainWindow(QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, database=None, parent=None):
        super(MainWindow, self).__init__(parent)  # Exit Point

        if database is None:
            start = StartWindow()
            good = bool(start.exec_())
            if good:
                key = start.give_back()
            else:
                sys.exit()
            self.API = Blue_Alliance_API.BlueAllianceAPI(key)
        else:
            self.API = database

        self.setupUi(self)

        self.file_thread = FileThread()
        self.network_thread = NetworkThread()
        self.waiting_threat = WaitingThread()

        self.team_selection.addItems(np.sort(self.API.get_teams()[:, 0]).astype(str).tolist())
        self.team_selection.currentIndexChanged[int].connect(self._update_ui)
        self.matches_list.itemSelectionChanged.connect(self.update_matches)
        self.pushButton.pressed.connect(self.launch_add_window)
        self.scouting_list.itemSelectionChanged.connect(self.update_scouting)
        self.save_button.pressed.connect(self.save_database)
        self.update_button.pressed.connect(self.update_database)
        self.change_event_button.pressed.connect(self.change_event)
        self.link_button.pressed.connect(self.link_event)
        self.link_button_2.pressed.connect(self.link_team)
        self.network_thread.thread_done.connect(self.finish_update)
        self.waiting_threat.thread_done.connect(self._finish_update)
        self.delete_button.pressed.connect(self.delete_scout)
        self.edit_button.pressed.connect(self.edit_scout)
        self.setup_scouting_table()
        self.update_ui(True)
        self.save_database(False, False)

    def launch_add_window(self):
        diag = AddWindow(int(self.team_selection.currentText()))
        if diag.exec_():
            data = diag.give_back()
            self.API.add_scout_data(self.curr_team, data[1], data[2:], data[0])
            self.update_ui()
            self.save_database(False, False)

    def edit_scout(self):
        curr_match = self.scouting_list.currentItem().text().split(' ')
        num = int(curr_match[-1])
        match_type = ' '.join(curr_match[:-1])

        curr_data = np.array(self.API.get_scout_data(self.curr_team)[1], np.object)
        curr_data = curr_data[curr_data[:, 0] == num][0]

        diag = AddWindow(int(self.team_selection.currentText()), curr_data, match_type)
        if diag.exec_():
            data = diag.give_back()
            self.API.edit_scout_data(self.curr_team, data[1], data[2:], data[0])
            self.save_database(False, False)
            self.update_ui()

    def update_ui(self, reset=False):

        current_matches_list = self.matches_list.currentRow()
        current_scouting_list = self.scouting_list.currentRow()
        team = int(self.team_selection.currentText())

        # if not reset:
        #     self.update_ui(True)

        self.matches_list.clear()
        self.scouting_list.clear()
        self.reset_scouting_table()

        self.curr_team = team
        rankings = self.API.get_team_rankings(team)
        stats = self.API.get_team_stats(team)

        names = ['Qual Avg', 'Auto', 'Container', 'Coopertition', 'Litter', 'Tote']
        self.clear_layout(self.graph_area)
        self.graph_area.addWidget(self.API.plot_skill(self.API.get_z_scores(rankings), names))
        self.team_qm_matches = self.API.get_team_matches(team)
        self.team_qf_matches = self.API.get_team_matches(team, 'qf')
        self.team_sf_matches = self.API.get_team_matches(team, 'sf')
        self.team_f_matches = self.API.get_team_matches(team, 'f')

        self.team_qm_scouting = np.array(self.API.get_scout_data(team, 'qm')[1], np.object)
        self.team_qf_scouting = np.array(self.API.get_scout_data(team, 'qf')[1], np.object)
        self.team_sf_scouting = np.array(self.API.get_scout_data(team, 'sf')[1], np.object)
        self.team_f_scouting = np.array(self.API.get_scout_data(team, 'f')[1], np.object)
        self.match_strings = self.__make_match_list(self.team_qm_matches,
                                                    self.team_qf_matches, self.team_sf_matches, self.team_f_matches)

        num_matches = rankings[8]

        self.team_number.setText(str(team))
        self.team_name.setText(self.API.get_teams(team)[1])
        self.rank.setText(str(rankings[0]))
        self.matches_played.setText(str(num_matches))
        self.opr.setText('%.2f' % (stats[1]))
        self.dpr.setText('%.2f' % (stats[2]))
        self.ccwm.setText('%.2f' % (stats[3]))
        self.gen_score.setText('%.2f' % (rankings[2]))
        self.gen_auto.setText('%.2f' % (rankings[3] / num_matches))
        self.gen_cont.setText('%.2f' % (rankings[4] / num_matches))
        self.gen_coop.setText('%.2f' % (rankings[5] / num_matches))
        self.gen_litter.setText('%.2f' % (rankings[6] / num_matches))
        self.gen_tote.setText('%.2f' % (rankings[7] / num_matches))

        self.matches_list.addItems(self.match_strings)

        for match_type, scouted_matches in [['qm', self.team_qm_scouting], ['qf', self.team_qf_scouting],
                                            ['sf', self.team_sf_scouting], ['f', self.team_f_scouting]]:
            if len(scouted_matches) is not 0:
                for match_num in scouted_matches[:, 0]:
                    self.scouting_list.addItem('%s %i' % (match_type, match_num))
        if reset:
            self.matches_list.setCurrentRow(0)
            if self.scouting_list.count() is not 0:
                self.scouting_list.setCurrentRow(0)
            else:
                self.set_blank_scouting()

        else:
            self.matches_list.setCurrentRow(current_matches_list)
            if self.scouting_list.count() is not 0:
                print('13')
                self.scouting_list.setCurrentRow(current_scouting_list)
                print('14')
            else:
                self.set_blank_scouting()
                # self.scouting_list.addItems(self.match_strings)


    def _update_ui(self):
        self.update_ui(True)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())

    @staticmethod
    def __make_match_list(qm, qf, sf, f):
        qms = []
        qfs = []
        sfs = []
        fs = []

        if len(qm) is not 0:
            qms = ['Qual %i' % ma for ma in qm[:, 0]]
        if len(qf) is not 0:
            qfs = ['Quart. Final %i' % ma for ma in qf[:, 0]]
        if len(sf) is not 0:
            sfs = ['Semi Final %i' % ma for ma in sf[:, 0]]
        if len(f) is not 0:
            fs = ['Final %i' % ma for ma in f[:, 0]]

        return qms + qfs + sfs + fs

    def update_matches(self):
        # self.scouting_list.setCurrentRow(self.matches_list.currentRow())
        curr_match = self.match_strings[self.matches_list.currentRow()].split(' ')
        num = curr_match[-1]
        match_type = ' '.join(curr_match[:-1])
        if match_type == 'Qual':
            matches = self.team_qm_matches
        elif match_type == 'Quart. Final':
            matches = self.team_qf_matches
        elif match_type == 'Semi Final':
            matches = self.team_sf_matches
        elif match_type == 'Final':
            matches = self.team_f_matches

        curr_match = matches[matches[:, 0] == int(num)][0]

        self.matches_red_1.setText(str(curr_match[1][0]))
        self.matches_red_2.setText(str(curr_match[1][1]))
        self.matches_red_3.setText(str(curr_match[1][2]))
        self.matches_blue_1.setText(str(curr_match[2][0]))
        self.matches_blue_2.setText(str(curr_match[2][1]))
        self.matches_blue_3.setText(str(curr_match[2][2]))
        self.matches_r_score.setText(str(curr_match[3][0]))
        self.matches_r_auto.setText(str(curr_match[3][1]))
        self.matches_r_foul.setText(str(curr_match[3][2]))
        self.matches_r_tele.setText(str(curr_match[3][0] - curr_match[3][1] - curr_match[3][2]))
        self.matches_b_score.setText(str(curr_match[4][0]))
        self.matches_b_auto.setText(str(curr_match[4][1]))
        self.matches_b_foul.setText(str(curr_match[4][2]))
        self.matches_b_tele.setText(str(curr_match[4][0] - curr_match[4][1] - curr_match[4][2]))

    def update_scouting(self):
        curr_match = self.scouting_list.currentItem().text().split(' ')
        num = curr_match[-1]
        match_type = ' '.join(curr_match[:-1])
        if match_type == 'qm':
            matches = self.team_qm_scouting
        elif match_type == 'qf':
            matches = self.team_qf_scouting
        elif match_type == 'sf':
            matches = self.team_sf_scouting
        elif match_type == 'f':
            matches = self.team_f_scouting

        curr_match = matches[matches[:, 0] == int(num)][0][1]

        print('21')
        self.scout_auto_set.setText(str(curr_match[0]))
        self.scout_tote_set.setText(str(curr_match[1]))
        print('22')
        self.scout_cont_set.setText(str(curr_match[2]))
        self.scout_stack_set.setText(str(curr_match[3]))
        print('23')
        self.scout_human.setText(str(curr_match[4]))
        self.scout_landfill.setText(str(curr_match[5]))
        print('24')
        self.scout_litter.setText(str(curr_match[6]))
        self.scout_coop.setText(str(curr_match[7]))
        print('25')
        self.scouting_comments.setText(str(curr_match[8]))
        print('26')
        self.draw_scouting_table(curr_match[9])
        print('27')

    def set_blank_scouting(self):

        self.scout_auto_set.setText('-')
        self.scout_tote_set.setText('-')
        self.scout_cont_set.setText('-')
        self.scout_stack_set.setText('-')
        self.scout_human.setText('-')
        self.scout_landfill.setText('-')
        self.scout_litter.setText('-')
        self.scout_coop.setText('-')
        self.scouting_comments.setText('-')

    def save_database(self, question=True, notification=True):
        ret = QMessageBox.Save

        if SAVED and question:
            confirm = QMessageBox()
            confirm.setText('<b>Database Already Exists</b>')
            confirm.setInformativeText('Do you wish to overwrite')
            confirm.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
            ret = confirm.exec_()

        if ret == QMessageBox.Save:
            # self.file_thread.set_api(self.API)
            # self.file_thread.start()
            joblib.dump(self.API, DATABASE_FILE, True)
            if notification:
                message = QMessageBox()
                message.setText('Successfully Saved')
                message.exec_()

    @staticmethod
    def __bool_dummy():
        return False

    def update_database(self):
        if check_internet(self.__bool_dummy):
            self.update_button.setText('Updating...')
            self.network_thread.set_api(self.API)
            self.network_thread.start()
            # self.API.update_all()
            # self.update_ui()

    def finish_update(self):
        self.save_database(False, False)
        self.update_ui()
        self.update_button.setText('Updated')
        self.waiting_threat.set_time(2)
        self.waiting_threat.start()

    def _finish_update(self):
        self.update_button.setText('Update')

    def setup_scouting_table(self):
        for j in range(self.scouting_table.rowCount()):
            for i in range(self.scouting_table.columnCount()):
                self.scouting_table.setItem(j, i, QTableWidgetItem(''))

    def reset_scouting_table(self):
        for row in range(self.scouting_table.rowCount()):
            for col in range(self.scouting_table.columnCount()):
                self.scouting_table.item(row, col).setText('')

    def draw_scouting_table(self, data):
        for row in range(self.scouting_table.rowCount()):
            for col in range(self.scouting_table.columnCount()):
                self.scouting_table.item(row, col).setText(data[row][col])

    def change_event(self):
        if check_internet(self.__bool_dummy):

            confirm = QMessageBox()
            confirm.setText('<b>Warning</b>')
            confirm.setInformativeText('This will overwrite all scouting and matches. Please backup database.')
            confirm.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = confirm.exec_()

            if ret == QMessageBox.Ok:
                start = StartWindow()
                good = bool(start.exec_())
                if good:
                    key = start.give_back()
                    self.API = Blue_Alliance_API.BlueAllianceAPI(key)
                    self.team_selection.clear()
                    self.team_selection.addItems(np.sort(self.API.get_teams()[:, 0]).astype(str).tolist())
                    self.update_ui()

    def delete_scout(self, ask=True):

        ret = QMessageBox.Ok

        if ask:
            confirm = QMessageBox()
            confirm.setText('<b>Deleting Scout Data</b>')
            confirm.setInformativeText('Are you sure you want to delete this data')
            confirm.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = confirm.exec_()

        if ret == QMessageBox.Ok:
            curr_match = self.scouting_list.currentItem().text().split(' ')
            num = int(curr_match[-1])
            match_type = ' '.join(curr_match[:-1])

            self.API.delete_scout_data(self.curr_team, num, match_type)
            self.update_ui()
            self.save_database(False, False)

    def link_event(self):
        web.open('http://www.thebluealliance.com/event/%s' % self.API.EVENT_KEY, autoraise=True)

    def link_team(self):
        web.open('http://www.thebluealliance.com/team/%i/%s' % (self.curr_team, self.API.EVENT_KEY[:4]), autoraise=True)


class AddWindow(QDialog, add_window.Ui_Add_match):
    def __init__(self, team, start_data=None, init_type='qm', parent=None):
        super(AddWindow, self).__init__(parent)

        self.setupUi(self)

        self.team_number.setText(str(team))

        self.pushButton.pressed.connect(self.accept)
        self.scouting_table.itemPressed.connect(self.scoring)

        # self.scouting_table.setFocusPolicy(Qt.NoFocus)
        self.scouting_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # pal = self.scouting_table.palette()
        # pal.setBrush(QPalette.Highlight, QBrush(Qt.white))
        # pal.setBrush(QPalette.HighlightedText, QBrush(Qt.black))
        # self.scouting_table.setPalette(pal)
        self.setup_table()

        if start_data is not None:
            type = ['qm', 'qf', 'sf', 'f']
            self.match_type.setCurrentIndex(type.index(init_type))
            self.match_type.setEnabled(False)
            self.pushButton.setText('Save')
            curr_match = start_data[0]
            start_data = start_data[1]
            self.lineEdit.setText(str(curr_match))
            self.lineEdit.setEnabled(False)
            self.auto_check.setChecked(string_to_bool(start_data[0]))
            self.tote_check.setChecked(string_to_bool(start_data[1]))
            self.con_check.setChecked(string_to_bool(start_data[2]))
            self.s.setChecked(string_to_bool(start_data[3]))
            self.hl_spin.setValue(int(start_data[4]))
            self.landfill_spin.setValue(int(start_data[5]))
            self.litter_spin.setValue(int(start_data[6]))
            self.coop_spin.setValue(int(start_data[7]))
            self.textEdit.setText(start_data[8])
            self.draw_scouting_table(start_data[9])

    def draw_scouting_table(self, data):
        for row in range(self.scouting_table.rowCount()):
            for col in range(self.scouting_table.columnCount()):
                self.scouting_table.item(row, col).setText(data[row][col])

    def setup_table(self):
        for i in range(self.scouting_table.columnCount()):
            for j in range(self.scouting_table.rowCount()):
                # ooes = QTableWidgetItem()
                self.scouting_table.setItem(j, i, QTableWidgetItem(''))

    def scoring(self):
        if self.scouting_table.currentItem().text() == '/////':
            self.scouting_table.currentItem().setText('')
        else:
            self.scouting_table.currentItem().setText('/////')

    def get_table_content(self):
        rows = self.scouting_table.rowCount()
        cols = self.scouting_table.columnCount()

        data = np.zeros((rows, cols), np.str)

        data = np.array([[self.scouting_table.item(row, col).text() for col in range(cols)] for row in range(rows)])
        return data


    def give_back(self):
        data = []

        data.append(self.match_type.currentText())
        data.append(int(self.lineEdit.text()))  # match number
        data.append(self.auto_check.isChecked())  # auto set
        data.append(self.tote_check.isChecked())  # tote set
        data.append(self.con_check.isChecked())  # container set
        data.append(self.s.isChecked())  # Stackes Set
        data.append(self.hl_spin.value())  # Human Load totes
        data.append(self.landfill_spin.value())  # Landfill totes
        data.append(self.litter_spin.value())  # Litter Scored
        data.append(self.coop_spin.value())  # Coop Points scored
        data.append(self.textEdit.toPlainText())  # Comments
        data.append(self.get_table_content())

        return data


class StartWindow(QDialog, start_window.Ui_Dialog):
    def __init__(self, parent=None):
        super(StartWindow, self).__init__(parent)

        self.setupUi(self)

        check_internet()

        self.year_chosen = False
        self.year_box.activated[int].connect(self.populate_events)
        self.buttonBox.pressed.connect(self.finish_up)

    def populate_events(self):
        self.year_chosen = True
        year = int(self.year_box.currentText())
        self.events = Blue_Alliance_API.get_events(year)
        self.event_box.addItems(self.events[:, 0])

    def give_back(self):
        event_name = self.event_box.currentText()
        event_key = self.events[self.events[:, 0] == event_name][0][1]

        return event_key  # Exit Point

    def finish_up(self):
        if self.year_chosen:
            self.accept()


class NetworkThread(QThread):
    thread_done = Signal()

    def __init__(self, parent=None):
        super(NetworkThread, self).__init__(parent)

    def set_api(self, api):
        self.API = api

    def run(self):
        self.API.update_all()
        self.thread_done.emit()


class FileThread(QThread):
    def __init__(self, parent=None):
        super(FileThread, self).__init__(parent)

        self.api = None

    def set_api(self, api):
        self.api = api

    def run(self):
        joblib.dump(self.api, DATABASE_FILE, True)


class WaitingThread(QThread):
    thread_done = Signal()

    def __init__(self, parent=None):
        super(WaitingThread, self).__init__(parent)

    def set_time(self, time):
        self.time = int(time)

    def run(self):
        sleep(self.time)
        self.thread_done.emit()


def check_internet(action=sys.exit, *args, **kwargs):
    try:
        Blue_Alliance_API.get_events(2014)
    except URLError:
        message = QMessageBox()
        message.setText("<b>Error</b>: No Internet Connection")
        if message.exec_():
            action(*args, **kwargs)
    return True


def main():
    app = QApplication(sys.argv)
    database = None
    if SAVED:
        database = joblib.load(DATABASE_FILE)

    dialog = MainWindow(database)
    dialog.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()