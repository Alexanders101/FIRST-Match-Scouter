__author__ = 'alex'
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

import urllib.request
import json
import numpy as np
from numpy import array as np_array
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class BlueAllianceAPI:
    URL = 'http://www.thebluealliance.com/api/v2/'
    HEADER_KEY = 'X-TBA-App-Id'
    HEADER_VAL = 'frc846:scouting-stats:1'
    EVENT_KEY = ''

    def __init__(self, event_key):
        self.EVENT_KEY = event_key

        self.qualification_matches = []
        self.quarter_final_matches = []
        self.semi_final_matches = []
        self.final_matches = []

        self.raw_teams = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/teams')
        self.raw_matches = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/matches')
        self.raw_rankings = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/rankings')
        self.raw_stats = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/stats')

        self.__update_matches()
        self.__separate_stats()
        self.__update_rankings()
        self.do_some_stats()

        self.qualification_scouting = []
        self.quarter_final_scouting = []
        self.semi_final_scouting = []
        self.final_scouting = []
        self.__setup_scouting_arrays()

    def __update_matches(self):

        for match_type, var in [['qm', 'qualification_matches'], ['qf', 'quarter_final_matches'],
                                ['sf', 'semi_final_matches'], ['f', 'final_matches']]:
            num_matches = self.__count_matches(self.raw_matches, match_type)
            if num_matches is not 0:
                # zero = range(num_matches)
                red_teams = np.zeros((num_matches,), np.object)
                blue_teams = np.zeros((num_matches,), np.object)
                blue_scores = np.zeros((num_matches,), np.object)
                red_scores = np.zeros((num_matches,), np.object)
                match_numbers = np.arange(1, num_matches + 1, 1)

                for match in self.raw_matches:
                    if match['comp_level'] == match_type:
                        match_num = match['match_number'] - 1
                        red_teams[match_num] = [np.int(match['alliances']['red']['teams'][0][3:]),
                                                np.int(match['alliances']['red']['teams'][1][3:]),
                                                np.int(match['alliances']['red']['teams'][2][3:])]
                        red_scores[match_num] = [-1 if match['alliances']['red']['score'] is None
                                                 else match['alliances']['red']['score'],
                                                  -1 if match['score_breakdown']['red']['auto'] is None
                                                  else match['score_breakdown']['red']['auto'],
                                                  -1 if match['score_breakdown']['red']['foul'] is None
                                                  else match['score_breakdown']['red']['foul']]
                        blue_teams[match_num] = [np.int(match['alliances']['blue']['teams'][0][3:]),
                                                 np.int(match['alliances']['blue']['teams'][1][3:]),
                                                 np.int(match['alliances']['blue']['teams'][2][3:])]
                        blue_scores[match_num] = [-1 if match['alliances']['blue']['score'] is None
                                                  else match['alliances']['blue']['score'],
                                                  -1 if match['score_breakdown']['blue']['auto'] is None
                                                  else match['score_breakdown']['blue']['auto'],
                                                  -1 if match['score_breakdown']['blue']['foul'] is None
                                                  else match['score_breakdown']['blue']['foul']]

                red_win = np_array(red_scores.tolist())[:, 0] > np_array(blue_scores.tolist())[:, 0]

                self.__setattr__(var,
                                 np.rot90(np_array([match_numbers, red_teams, blue_teams, red_scores, blue_scores, red_win], np.object))[::-1])

    def __update_rankings(self):
        self.rankings = np.array(self.raw_rankings[1:]).astype(np.int)

    def __separate_stats(self):
        stats = self.raw_stats
        if stats is not None:
            combined = np.array([[int(team), stats['oprs'][team], stats['dprs'][team],
                                  stats['ccwms'][team]] for team in stats['oprs'].keys()], np.object)
        else:
            teams = self.get_teams()[:, 0]
            num_teams = len(teams)
            combined = np.rot90(np_array([teams, np.zeros(num_teams), np.zeros(num_teams), np.zeros(num_teams)], np.object))[::-1]
        self.stats = combined

    def __setup_scouting_arrays(self):

        teams = self.get_teams()[:, 0]

        qm = [[team, []] for team in teams]
        qf = [[team, []] for team in teams]
        sf = [[team, []] for team in teams]
        f = [[team, []] for team in teams]

        qm = np.array(qm, np.object)
        qf = np.array(qf, np.object)
        sf = np.array(sf, np.object)
        f = np.array(f, np.object)

        self.qualification_scouting = qm
        self.quarter_final_scouting = qf
        self.semi_final_scouting = sf
        self.final_scouting = f

    def update_all(self):
        self.qualification_matches = []
        self.quarter_final_matches = []
        self.semi_final_matches = []
        self.final_matches = []

        self.raw_teams = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/teams')
        self.raw_matches = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/matches')
        self.raw_rankings = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/rankings')
        self.raw_stats = self.__get_request(self.URL + 'event/' + self.EVENT_KEY + '/stats')

        self.__update_matches()
        self.__separate_stats()
        self.__update_rankings()
        self.do_some_stats()

    def __get_request(self, request_code):
        request = urllib.request.Request(request_code)
        request.add_header(self.HEADER_KEY, self.HEADER_VAL)
        response = urllib.request.urlopen(request)
        jsonified = json.loads(response.read().decode("utf-8"))
        return jsonified

    @staticmethod
    def __count_matches(matches, match_type='qm'):
        match_sum = 0
        for match in matches:
            if match['comp_level'] == match_type:
                match_sum += 1
        return match_sum

    def get_team_matches(self, team_number, match_type='qm'):
        matches = self.get_matches(match_type)

        if len(matches) is not 0:
            team_matches = [((team_number in match[1]) or (team_number in match[2])) for match in matches[:, :3]]
            team_matches = np.array(team_matches)
            team_matches = matches[team_matches]
        else:
            team_matches = []

        return team_matches

    def get_matches(self, match_type='qm'):
        if match_type is 'qm':
            return self.qualification_matches
        elif match_type is 'qf':
            return self.quarter_final_matches
        elif match_type is 'sf':
            return self.semi_final_matches
        elif match_type is 'f':
            return self.final_matches

    def get_teams(self, team_number='all'):
        curr_teams = np.array([[int(team['team_number']), team['nickname']] for team in self.raw_teams], np.object)
        if team_number is 'all':
            return curr_teams
        return curr_teams[curr_teams[:, 0] == team_number][0]

    def get_team_awards(self, team_key):
        jsonified = self.__get_request(self.URL + 'team/' + team_key + '/2015')
        events = jsonified['events']
        team_awards = []

        for event in events:
            for award in event['awards']:
                team_awards.append(award['name'])

        return team_awards

    def get_team_rankings(self, team='all'):
        # ['Rank' 'Team' 'Qual Avg' 'Auto' 'Container' 'Coopertition' 'Litter' 'Tote' 'Played']
        request = np.array(self.raw_rankings[1:]).astype(np.int)
        # print(np.array(self.raw_rankings[0]))
        if team is 'all':
            return request
        getter = request[request[:, 1] == team]
        if len(getter) is not 0:
            return request[request[:, 1] == team][0]
        return np_array([0, team, 0, 0, 0, 0, 0, 0, 0])

    def get_team_stats(self, team='all'):
        if team is 'all':
            return self.stats
        return self.stats[self.stats[:, 0] == team][0]


    def do_some_stats(self):
        rankings = self.rankings

        if len(rankings) is not 0:
            self.extra_stats = np.array([[np.mean(rankings[:, i]), np.std(rankings[:, i])] for i in np.arange(2, 8, 1)])
            curr_maxes = np.array([np.max(rankings[:, i]) for i in range(len(rankings[0]))])
            curr_min = np.array([np.min(rankings[:, i]) for i in range(len(rankings[0]))])
            self.maxes = self.get_z_scores(curr_maxes, False)
            self.mins = abs(self.get_z_scores(curr_min, False))

        else:
            teams = self.get_teams()[:, 0]
            self.extra_stats = np.zeros((6, 2))
            curr_maxes = np.zeros((9,))
            curr_min = np.zeros((9,))
            self.maxes = self.get_z_scores(curr_maxes, False)
            self.mins = abs(self.get_z_scores(curr_min, False))

    def get_z_scores(self, rankings, normalize=True):
        curr = rankings[2:8]
        curr = (curr - self.extra_stats[:, 0]) / self.extra_stats[:, 1]
        if normalize:
            curr += self.mins
            curr /= ((self.maxes + self.mins) / self.maxes)
        return curr

    def add_scout_data(self, team, match_number, data, match_type='qm'):
        data = np.array(data, np.object)

        if match_type == 'qm':
            curr_scout = self.qualification_scouting
        elif match_type == 'qf':
            curr_scout = self.quarter_final_scouting
        elif match_type == 'sf':
            curr_scout = self.semi_final_scouting
        elif match_type == 'f':
            curr_scout = self.final_scouting
        else:
            print('Incorrect Match Type')
            return

        curr_scout[curr_scout[:, 0] == team][0][1].append([match_number, data])

    def delete_scout_data(self, team, match_number, match_type='qm'):
        if match_type == 'qm':
            curr_scout = self.qualification_scouting
        elif match_type == 'qf':
            curr_scout = self.quarter_final_scouting
        elif match_type == 'sf':
            curr_scout = self.semi_final_scouting
        elif match_type == 'f':
            curr_scout = self.final_scouting
        else:
            print('Incorrect Match Type')
            return

        temp = np.array(curr_scout[curr_scout[:, 0] == team][0][1], np.object)
        location = (temp[:, 0] == match_number)
        location = np.nonzero(location)[0]
        if len(location) is not 1:
            return False
        location = location[0]
        del (curr_scout[curr_scout[:, 0] == team][0][1][location])
        return True

    def edit_scout_data(self, team, match_number, data, match_type='qm'):
        data = np.array(data, np.object)

        if match_type == 'qm':
            curr_scout = self.qualification_scouting
        elif match_type == 'qf':
            curr_scout = self.quarter_final_scouting
        elif match_type == 'sf':
            curr_scout = self.semi_final_scouting
        elif match_type == 'f':
            curr_scout = self.final_scouting
        else:
            print('Incorrect Match Type')
            return

        match_number = int(match_number)
        temp = np.array(curr_scout[curr_scout[:, 0] == team][0][1], np.object)
        location = (temp[:, 0] == match_number)
        location = np.nonzero(location)[0]
        if len(location) is not 1:
            return False
        location = location[0]

        curr_scout[curr_scout[:, 0] == team][0][1][location] = [match_number, data]

    def get_scout_data(self, team, match_type='qm'):
        if match_type is 'qm':
            curr_scout = self.qualification_scouting
        elif match_type is 'qf':
            curr_scout = self.quarter_final_scouting
        elif match_type is 'sf':
            curr_scout = self.semi_final_scouting
        elif match_type is 'f':
            curr_scout = self.final_scouting

        return curr_scout[curr_scout[:, 0] == team][0]

    def plot_skill(self, values, names):
        if len(values) is not len(names):
            print('Length of data and names does not match')
            return
        num = len(values)
        r = np.concatenate((values, [values[0]]))
        theta = np.deg2rad(np.arange(0, 361, 360 / num))
        if np.isnan(np.sum(r)):
            r = np.nan_to_num(r)
        fig = plt.Figure(dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        # fig = plt.Figure()
        ax = fig.add_subplot(111, polar=True)
        ax.plot(theta, r)
        ax.set_xticks(np.array(theta[:-1]))
        ax.set_ylim(0, np.max(self.maxes).round())
        ax.set_xticklabels(names)
        ax.set_yticks([10])

        canvas = FigureCanvas(fig)

        return canvas

    def create_sstatistics(self):
        teams = self.get_teams()[:, 0]




def get_events(year):
    year = str(year)
    request = urllib.request.Request('http://www.thebluealliance.com/api/v2/events/%s' % year)
    request.add_header('X-TBA-App-Id', 'frc846:scouting-stats:1')
    response = urllib.request.urlopen(request)
    raw = json.loads(response.read().decode("utf-8"))

    events = np.array([[event['name'], event['key']] for event in raw])
    ind = np.lexsort((events[:, 1], events[:, 0]))

    return events[ind]