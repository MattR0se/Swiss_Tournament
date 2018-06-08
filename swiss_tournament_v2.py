'''
to do list:
    - Seatings ausdrucken
    - parings ausdrucken CHECK
    - Top8 single elimination
    - Player hinzufügen während des Turniers
    - All time player list
    - mehr random names (500+) CHECK
    - fake DCIs wenn dci nicht required CHECK

'''

import random
import pickle
import datetime
import copy
from os import path, makedirs
from math import log, ceil
from prettytable import PrettyTable
import numpy as np

import randomnames


def list_in_list(list1, list2):
    dci_list_1 = [list1[i].dci for i in range(len(list1))]
    dci_list_2 = [list2[i].dci for i in range(len(list2))]
    
    len1 = len(dci_list_1)
    hits = 0
    for elem in dci_list_1:
        if elem in dci_list_2:
            hits += 1
    return hits == len1


class Player():
    def __init__(self, name, dci):
        self.name = name
        self.dci = dci
        self.table_number = 0
        self.points_total = 0
        self.matches_won = 0
        self.matches_played = 0
        self.matches_drawn = 0
        self.games_won = 0
        self.games_played = 0
        self.games_drawn = 0
        # tiebreakers
        # MWP = own Match Win %; PGW = own Game Win %
        # OMW = opponents' match win %; OGW = opponents' Game Win %
        self.MWP = 0
        self.PGW = 0
        self.OMW = 0
        self.OGW = 0
        
        self.opponents = []
  
    
     
class tournament():
    def __init__(self):
        self.players = []
        self.dropouts = []
        self.results_entered = []
        self.no_of_players = 0
        self.no_of_rounds = 0
        self.round_no = 0
        self.starting_table = 1
        self.bye = Player('BYE', 0)
        self.event_name = 'mytournament'
        self.event_information = 'Frontier PPTQ @Spielhölle Musterstadt'

        
        # initial setting
        #self.dci_required = input('DCI number required? y/n:  ')
        #if self.dci_required == 'y':
        self.dci_required = True
        self.generated_IDs = []
        # get time for tournament ID
        self.tournament_id = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.date = str(datetime.datetime.now().strftime('%Y/%m/%d'))
      
        
    def setup_players(self):          
        self.no_of_players = int(input('How many players?  '))
        
        for i in range(self.no_of_players):
            this_player = Player('', 0)
            name_exists = True
            while name_exists:
                name = input('Name of player {}: '.format(i + 1))
                if not self.players:
                    name_exists = False
                for player in self.players:
                    if player.name == name:
                        name_exists = True
                        print('--- WARNING: Name already exists! ---')
                        break
                    else:
                        name_exists = False
            this_player.name = name
            if self.dci_required:
                dci = int(input('DCI-Nr. of player {}: '.format(i + 1)))
                this_player.dci = dci
            else:
                while True:
                    dci = random.randint(0, 9999999999)
                    if not dci in self.generated_IDs:
                        this_player.dci = dci
                        self.generated_IDs.append(dci)
                        break
            self.players.append(this_player)
        
    
    def print_players(self):
        print('\nPlayers in this tournament:')
        self.sort_players(by='name')
        for player in self.players:
            if self.dci_required:
                print(player.name, player.dci)
            else:
                print(player.name)
    
    
    def calculate_rounds(self):
        #self.recommended_rounds = input('\nUse recommended number of rounds? y/n:   ')
        self.recommended_rounds = 'y'
        if self.recommended_rounds == 'n':
            self.no_of_rounds =  int(input('Enter number of rounds:   '))
        else:
            # set the no. of rounds based on number of players
            #     5 - 8 = 3
            #    9 - 16 = 4
            #   17 - 32 = 5
            #   33 - 64 = 6
            #  65 - 128 = 7
            # 129 - 226 = 8
            # 227 - 409 = 9
            #      410+ = 10
            if self.no_of_players <= 128:
                self.no_of_rounds = ceil(log(self.no_of_players,2))
            elif self.no_of_players <= 226:
                self.no_of_rounds = 8
            elif self.no_of_players <= 409:
                self.no_of_rounds = 9
            else:
                self.no_of_rounds = 10
    
    
    def new_round(self):
        no_of_pairings = self.no_of_players // 2
        self.round_no += 1
        if self.round_no == 1:
            # first round, completely random
            self.pairings = []
            self.players_temp = []
            random.shuffle(self.players)
            
            if len(self.players) %2 != 0:
                # if number of players is odd, give a bye
                player1 = self.players.pop(0)
		self.give_bye(player1)
                player2 = self.bye
                self.pairings.append([player1, player2])
                self.players_temp.append(player1)
                
            for i in range(no_of_pairings):
                player1 = self.players.pop(0)
                player2 = self.players.pop(0)
                self.pairings.append([player1, player2])
                player1.table_number = i + self.starting_table
                player2.table_number = i + self.starting_table
                self.players_temp.append(player1)
                self.players_temp.append(player2)
            
            for pair in self.pairings:
                pair[0].opponents.append(pair[1])
                pair[1].opponents.append(pair[0])
            
            self.players = self.players_temp
        
        elif self.round_no == self.no_of_rounds + 1:
            # last round, sort by opponent score
            if len(self.results_entered) < no_of_pairings:
                print('--- WARNING: Results are still missing! ---')
                self.round_no -= 1
                return
            else:
                self.calculate_oppscores()
                self.sort_players(by='oppscore')
        
        elif self.round_no > self.no_of_rounds:
            print('--- WARNING: This was the last round! ---')
            self.round_no -= 1
            return
        
        else:
            # all other rounds
            if len(self.results_entered) < no_of_pairings:
                print('--- WARNING: Results are still missing! ---')
                self.round_no -= 1
                return
            else:
                self.pool_players() 
                attempts = 0
                while True:
                    self.pairings = []
                    self.players_temp = [] 
                    pool_nr = 0
                    pool = copy.deepcopy(self.pools)
                    for i in range(no_of_pairings):
                        random.shuffle(pool[pool_nr])
                        # take 2 out of the same pool or next of only one left
                        if len(pool[pool_nr]) == 0:
                            pool_nr += 1
                        if len(pool[pool_nr]) == 1:
                            player1 = pool[pool_nr].pop(0)
                            while not pool[pool_nr]:
                                pool_nr += 1
                            player2 = pool[pool_nr].pop(random.randint(0, 
                                                len(pool[pool_nr]) - 1))
                        else:
                            while not pool[pool_nr]:
                                pool_nr += 1
                            random.shuffle(pool[pool_nr])
                            player1 = pool[pool_nr].pop(0)
    
                            if list_in_list(pool[pool_nr], player1.opponents):
                                # if played against all other players in this pool, 
                                # choose another one
                                try:
                                    while not pool[pool_nr]:
                                        #print(pool_nr)
                                        pool_nr += 1
                                    #print('pool_nr', pool_nr, len(pool))
                                    player2 = pool[pool_nr + 1].pop(random.randint(0, 
                                                        len(pool[pool_nr + 1]) - 1))
                                except:
                                    # DAS nennt man wohl faules programmieren
                                    print('no opponent found')
                                    pass
    
                            else:
                                player2 = pool[pool_nr].pop(random.randint(0, 
                                                    len(pool[pool_nr]) - 1))

                        player1.table_number = i + self.starting_table
                        player2.table_number = i + self.starting_table
                        self.pairings.append([player1, player2])
                        self.players_temp.append(player1)
                        self.players_temp.append(player2)
                    
                    # find the remaining player and give them a bye
                    for i in range(len(pool)):
                        for player in pool[i]:
                            if player:
                                self.give_bye(player)
                                self.players_temp.append(player)
                        
                    # conditions that have to be met:
                    # players can't be paired against each other twice 
                    #   in the tournament
                    # players can't receive more than one bye, if possible
                    if self.check_pairings() or attempts >= 10000:
                        #print(attempts)
                        break
                    else:
                        attempts += 1
                
                for pair in self.pairings:
                    pair[0].opponents.append(pair[1])
                    pair[1].opponents.append(pair[0])             
                
                self.players = self.players_temp
                self.results_entered = []
                
                
    def check_pairings(self):
         for pairing in self.pairings:
             if list_in_list([pairing[1]], pairing[0].opponents):
                 return False
         return True
    
    
    def give_bye(self, player):
        player.matches_won += 1
        player.games_won += 2
    
    
    def enter_result(self, table, result):
        player1_win, player2_win, draw = result
        if table in self.results_entered:
            print('--- WARNING: Result already entered! ---')
            return
        elif (player1_win + player2_win + draw) > 3:
            print('--- WARNING: Invalid Result! ---')
            return
        else:
            self.results_entered.append(table)
        self.pairings[table - 1][0].games_won += player1_win
        self.pairings[table - 1][1].games_won += player2_win
        self.pairings[table - 1][0].games_drawn += draw
        self.pairings[table - 1][1].games_drawn += draw
        self.pairings[table - 1][0].games_played += (player1_win + player2_win 
                                                     + draw)
        self.pairings[table - 1][1].games_played += (player1_win + player2_win 
                                                     + draw)
        if player1_win > player2_win:
            self.pairings[table - 1][0].matches_won += 1
        elif player1_win < player2_win:
            self.pairings[table - 1][1].matches_won += 1
        else:
            self.pairings[table - 1][0].matches_drawn += 1
            self.pairings[table - 1][1].matches_drawn += 1
        self.pairings[table - 1][0].matches_played += 1
        self.pairings[table - 1][1].matches_played += 1
    

    def print_standings(self, final=False):
        if not final:
            self.sort_players(by='points')
            print('\nStandings: ')
            for player in self.players:
                print(player.name, player.points_total)
        else:
            self.sort_players(by='oppscore')
            
            print('\nStandings by Rank')
            print('Tournament-ID: {}'.format(self.tournament_id))
            print('Event Date: {}'.format(self.date))
            print('Event Information: {}'.format(self.event_information))
            print('\nOpponents Match Win Percent: OMW%')
            print('Game Win Percent: GW%')
            print('Opponents Game Win Percent: OGW%')

            t = PrettyTable(['Rank', 'Name', 'Points', 'OMW%', 'GW%', 'OGW%'])
            rank = 1
            for player in self.players:
                t.add_row([str(rank), player.name, player.points_total, 
                           round(player.OMW * 100, 4), round(player.PGW * 100, 
                                4), round(player.OGW * 100, 4)])
                rank += 1
            t.align = 'l'
            #t.align['Points'] = 'r'
            print(t)
    
    def print_pairings(self):
        t = PrettyTable(['Table', 'Player', 'DCI', 'Opponent', 'DCI ', 'Points'])
        print('\nPairings by Name')
        print('Tournament-ID: {}'.format(self.tournament_id))
        print('Event Date: {}'.format(self.date))
        print('Event Information: {}'.format(self.event_information))
        print('\nRound {}\n'.format(self.round_no))
        self.sort_players('name')
        for player in self.players:
            table = player.table_number
            pl = player.name
            pl_dci = player.dci
            opp = player.opponents[-1].name
            opp_dci = player.opponents[-1].dci
            points = str(player.points_total) + ' - ' + str(
                                            player.opponents[-1].points_total)
            t.add_row([table, pl, pl_dci, opp, opp_dci, points])
        t.align = 'l'
        #t.border = False
        print(t)
            
    def calculate_points(self):
        for player in self.players:
            player.points_total = player.matches_won * 3 + player.matches_drawn
        self.sort_players()
        
    
    def calculate_oppscores(self):
        # calculate own percentages
        for player in self.players:
            player.MWP = player.matches_won / player.matches_played
            player.PGW = player.games_won / player.games_played
        
        # calculate oppscores
        for player in self.players:
            # calculate player OMW 
            omws = []
            for opp in player.opponents:
                if opp.name is not 'BYE':
                    if opp.MWP < 0.33:
                        omws.append(0.33)
                    else:
                        omws.append(opp.MWP)
            player.OMW = np.mean(omws)
            
            # calculate player OGW
            ogws = []
            for opp in player.opponents:
                if opp.name is not 'BYE':
                    ogws.append(opp.PGW)
            player.OGW = np.mean(ogws)
        self.sort_players(by='oppscore')
        

    def sort_players(self, by='points'):
        if by == 'points':
            self.players.sort(key=lambda x: x.points_total, reverse=True)
        elif by == 'oppscore':
            self.players.sort(key=lambda x: (x.points_total, x.OMW, x.PGW, 
                              x.OGW), reverse=True)
        elif by == 'name':
            self.players.sort(key=lambda x: x.name, reverse=False)
    
    
    def pool_players(self):
        # create different pools by points_total
        self.sort_players()
        self.pools = [[]]
        nr = 0
        for i in range(len(self.players)):

            if i == len(self.players) - 1:
                self.pools[nr].append(self.players[i])
            elif self.players[i].points_total != self.players[i + 1].points_total:
                self.pools[nr].append(self.players[i])
                self.pools.append([])
                nr += 1
            else:
                self.pools[nr].append(self.players[i])

    
    def drop_player(self, name):
        for player in self.players:
            if player.name == name:
                self.dropouts.append(player)
                self.players.remove(player)
                print('\n{} dropped from the tournament'.format(name))
                return
            else:
                break
        print('\n--- WARNING: Player already dropped or does not exist.')
        

    def save_tournament(self):
        # set up the saves directory
        dir_ = path.dirname('__file__')
        saves_dir = path.join(dir_, 'tournament save files')
        if not path.exists(saves_dir):
            makedirs(saves_dir)
        
        filename = 'tournament_' + self.tournament_id + '.txt'
        # save everything
        with open(path.join(saves_dir, filename), 'wb') as file:
            pickle.dump(self, file)
            
    def load_tournament(self, id_nr):
        try:
            dir_ = path.dirname('__file__')
            saves_dir = path.join(dir_, 'tournament save files')
            filename = 'tournament_' + id_nr + '.txt'
            with open(path.join(saves_dir, filename), 'rb') as file:
                return pickle.load(file)
        except:
            print('error loading the file')
            return


class League():
    def __init__(self):
        #self.tournaments = []
        self.ladder = []
        
    
    def add_results(self, results):
        ladder = set((i.name,i.dci) for i in self.ladder)
        new_players = [i for i in results if (
                       i.name,i.dci) not in ladder]
        
        for player in new_players:
            print(player.name)
    
    
    def print_results(self):
        pass


def generate_random_players(number):
    shuffled_names = list(randomnames.names)
    formatted_names = []
    for name in shuffled_names:
        firstname, surname = name.split()
        formatted_names.append(surname + ', ' +  firstname)
    
    random.shuffle(formatted_names)
    players = []
    generated_numbers = []
    for i in range(number):
        #players.append(Player(formatted_names.pop(0), random.randint(0, 99999999)))
        while True:
            dci = random.randint(1000000000, 9999999999)
            if not dci in generated_numbers:
                generated_numbers.append(dci)
                break
        players.append(Player(formatted_names.pop(0), dci))
    return players


def simulate_round(tournament):
    tournament.new_round()
    tournament.print_pairings()
    
    random_results = [
           (2, 0, 0),
           (2, 1, 0),
           (0, 2, 0),
           (1, 2, 0),
           (2, 0, 0),
           (2, 1, 0),
           (0, 2, 0),
           (1, 2, 0),
           (2, 0, 0),
           (2, 1, 0),
           (0, 2, 0),
           (1, 2, 0),
           (1, 1, 1)
           ]
    for i in range(tournament.no_of_players // 2):
        result = random.choice(random_results)
        tournament.enter_result(i, result)
    tournament.calculate_points()


def simulate_tournament(no_of_players):
    event = tournament()
    event.dci_required = False
    event.no_of_players = no_of_players
    event.starting_table = 24
    event.players = generate_random_players(no_of_players)
    #event.setup_players()
    
    event.print_players()
    
    event.calculate_rounds()
    
    for i in range(event.no_of_rounds):
        simulate_round(event)
        
    event.calculate_oppscores()
    
    event.print_standings(True)    
    
    # testing save and load
    #event.save_tournament()
    #event.tournament_id
    #event = event.load_tournament(event.tournament_id)
    
    
    return event.players

# 300 players max!
league = League()

for i in range(1):
    #players = random.randint(129)
    players = 9
    
    results = simulate_tournament(players)
    league.add_results(results)

#league.print_results()
