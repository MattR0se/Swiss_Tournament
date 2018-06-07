// Swiss tournament algorithm in JavaScript

class Player {
    constructor(name, dci=0) {
        this.name = name;
        this.dci = dci;
        this.table_number = 0;
        this.points_total = 0;
        this.matches_won = 0;
        this.matches_played = 0;
        this.matches_drawn = 0;
        this.games_won = 0;
        this.games_played = 0;
        this.games_drawn = 0;
        // tiebreakers:
        // MWP = own Match Win %; PGW = own Game Win %;
        // OMW = opponents' match win %; OGW = opponents' Game Win %
        this.mwp = 0;
        this.pgw = 0;
        this.omw = 0;
        this.ogw = 0;

        this.opponents = [];
    }
}

class Tournament {
    constructor() {
        this.players = [];
        this.dropouts = [];
        this.results_entered = [];
        this.pairings = [];
        this.no_of_rounds = 0;
        this.round_no = 0;
        this.starting_table = 1;
        this.bye = new Player('BYE', 0);
        this.event_name = 'mytournament';
        this.event_information = 'Frontier PPTQ @Spielhölle Musterstadt';
        this.use_recommended_rounds = true

        self.dci_required = true;
        self.generated_IDs = [];
        // get time for tournament ID
        // self.tournament_id = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        const d = new Date();
        this.date = d.toISOString().slice(0,10);
        this.tournament_id = d
    }

    print_players() {
        console.log('\nPlayers in this tournament:');
        this.sort_players('points');
        //console.log(this.players)
        for (let player of this.players) {
            console.log(player.name, player.points_total);
        }

    }

    sort_players(order, reverse=false) {
        // sorts players by the given attribute
        if (order == 'name') {
            this.players.sort(function(a, b) {
            let nameA = a.name.toUpperCase(); // ignore upper and lowercase
            let nameB = b.name.toUpperCase(); // ignore upper and lowercase
            if (nameA < nameB) return -1;
            if (nameA > nameB) return 1;
            // namen müssen gleich sein
            return 0;
          })
        } else if (order == 'points') {
            if (reverse) {
                // sorts by points_total, lowest to highest
                this.players.sort(function(b, a) {
                    if (a.points_total > b.points_total) return -1;
                    if (a.points_total < b.points_total) return 1;
                    return 0;
                })
            } else {
                // sorts by points_total, highest to lowest
                this.players.sort(function(a, b) {
                    if (a.points_total > b.points_total) return -1;
                    if (a.points_total < b.points_total) return 1;
                    return 0;
                })
            }
        } else if (order == 'oppscore') {
            if (reverse) {
                // sort by oppscore
                this.players.sort(function(b, a) {
                    if (a.points_total > b.points_total) return -1;
                    if (a.points_total < b.points_total) return 1;
                    if (a.omw > b.omw) return -1;
                    if (a.omw < b.omw) return 1;
                    if (a.pgw > b.pgw) return -1;
                    if (a.pgw < b.pgw) return 1;
                    if (a.ogw > b.ogw) return -1;
                    if (a.ogw < b.ogw) return 1;

                    return 0;
                })
            } else {
                // sort by oppscore
                this.players.sort(function(a, b) {
                    if (a.points_total > b.points_total) return -1;
                    if (a.points_total < b.points_total) return 1;
                    if (a.omw > b.omw) return -1;
                    if (a.omw < b.omw) return 1;
                    if (a.pgw > b.pgw) return -1;
                    if (a.pgw < b.pgw) return 1;
                    if (a.ogw > b.ogw) return -1;
                    if (a.ogw < b.ogw) return 1;

                    return 0;
                })
            }
        }
    }

    calculate_rounds() {
        let no_of_players = this.players.length;
            if (this.use_recommended_rounds) {
                // set the no. of rounds based on number of players
                //     5 - 8 = 3
                //    9 - 16 = 4
                //   17 - 32 = 5
                //   33 - 64 = 6
                //  65 - 128 = 7
                // 129 - 226 = 8
                // 227 - 409 = 9
                //      410+ = 10
                if (no_of_players <= 128) {
                    this.no_of_rounds = Math.ceil(Math.log2(no_of_players));
                } else if (no_of_players <= 226) {
                    this.no_of_rounds = 8;
                } else if (no_of_players <= 409) {
                    this.no_of_rounds = 9;
                } else {
                    self.no_of_rounds = 10;
                }
            } else {
                // get user input
            }
    }

    new_round() {
        let no_of_pairings = Math.floor(this.players.length / 2);
        this.round_no ++;
        if (this.round_no == 1) {
            // first round, pair at random
            this.pairings = [];
            this.players_temp = [];
            shuffle(this.players);

            if (this.players.length % 2 != 0) {
                // give a bye if number of players is odd
                let player1 = this.players.pop(0);
                let player2 = this.bye;
                this.pairings.push([player1, player2]);
                this.enter_result(0, [2, 0, 0]);
                this.players_temp.push(player1);
            }
            for (let i = 0; i < no_of_pairings; i++) {
                let player1 = this.players.pop(0);
                let player2 = this.players.pop(0);
                this.pairings.push([player1, player2]);
                player1.table_number = i;
                player2.table_number = i;
                this.players_temp.push(player1);
                this.players_temp.push(player2);
            }
            for (let pairing of this.pairings) {
                pairing[0].opponents.push(pairing[1]);
                pairing[1].opponents.push(pairing[0]);
            }
            this.players = this.players_temp;
        } else if (this.round_no == this.no_of_rounds + 1) {
            // last round
            console.log('test');
        } else if (this.round_no > this.no_of_rounds) {
            console.log('WARNING: This was the last round!')
        } else {
            // all rounds except first and last
            if (this.results_entered.length < no_of_pairings) {
                console.log('WARNING: Results are still missing!');
                this.round_no --;
                return;
            } else {
                let player1, player2;
                let attempts = 0;
                while (true) {
                    this.pairings = [];
                    this.players_temp = [];
                    let table = 0;
                    // shuffle the players, then sort by points to get random players
                    // within same points
                    while (this.players.length > 1) {
                        shuffle(this.players);
                        this.sort_players('points', true);
                        player1 = this.players.pop(0);
                        let index = 0;
                        while (player1.opponents.includes(this.players[index])) {
                            index ++;
                            }
                            player2 = this.players.pop(index);
                        this.pairings.push([player1, player2]);
                        player1.table_number = table + this.starting_table;
                        player2.table_number = table + this.starting_table;
                        this.players_temp.push(player1);
                        this.players_temp.push(player2);
                        table ++;
                    }
                    if (this.players.length == 1) {
                        player1 = this.players.pop(0);
                        player2 = this.bye;
                        this.pairings.push([player1, player2]);
                        player1.table_number = 0;
                        this.players_temp.push(player1);
                        this.enter_result(this.pairings.length - 1, [2, 0, 0]);
                    }

                    this.players = this.players_temp;
                    if (this.check_pairings() || attempts >= 1000) {
                        break;
                    } else {
                        attempts ++;
                    }
                }
                for (let pairing of this.pairings) {
                    pairing[0].opponents.push(pairing[1]);
                    pairing[1].opponents.push(pairing[0]);
                }
                this.results_entered = [];
            }
        }
    }

    check_pairings() {
        for (let pairing of this.pairings) {
            if (list_in_list([pairing[1]],
                             pairing[0].opponents)) {
                return false;
            }
        }
        return true;
    }

    enter_result(table_number, result) {
        // result is an array [player1_win, player2_win, draw]
        // TO DO: Make results a dict with table number as key
        // instead of the array index
        let player1_win = result[0];
        let player2_win = result[1];
        let draw = result[2];
        let table = table_number;
        // if (table_number != 0) {
        //     table = table_number - this.starting_table;
        // }
        if (this.results_entered.includes(table)) {
            console.log('WARNING: Result already entered!');
            return;
        } else if ((player1_win + player2_win + draw) > 3) {
            console.log('WARNING: Invalid result!');
            return;
        } else if (table >= this.starting_table + Math.floor(this.players.length / 2)) {
            console.log('WARNING: Table number does not exist');
            return;
        } else {
            this.results_entered.push(table);
        }
        this.pairings[table][0].games_won += player1_win;
        this.pairings[table][1].games_won += player2_win;
        this.pairings[table][0].games_drawn += draw;
        this.pairings[table][1].games_drawn += draw;
        this.pairings[table][0].games_played += (player1_win + player2_win
                                                     + draw);
        this.pairings[table][1].games_played += (player1_win + player2_win
                                                     + draw);
         if (player1_win > player2_win) {
             this.pairings[table][0].matches_won += 1;
         } else if (player1_win < player2_win) {
             this.pairings[table][1].matches_won += 1;
         } else {
             this.pairings[table][0].matches_drawn += 1;
             this.pairings[table][1].matches_drawn += 1;
         }
         this.pairings[table][0].matches_played += 1;
         this.pairings[table][1].matches_played += 1;
    }

    print_pairings() {
        this.sort_players('name');
        //console.log('\nPairings:');
        let header = '<table style="width:50%"><tr class="dash"><td>Table<\/td><td>Player<\/td><td>' +
                    'DCI<\/td><td>Opponent<\/td><td>DCI<\/td><td>' +
                    'Points<\/td><\/td>';
        let rows = [];
        for (let player of this.players) {
            let table = player.table_number;
            let pl = player.name;
            let pl_dci = player.dci;
            let opps = player.opponents;
            let opp = opps[opps.length - 1].name;
            let opp_dci = opps[opps.length - 1].dci;
            let points = String(player.points_total) + ' - ' +
                     String(opps[opps.length - 1].points_total);
            //console.log(table, pl, pl_dci, opp, opp_dci, points);
            let pairings_string = '<tr><td>' + String(table) + '<\/td><td>' +
                        String(pl) + '<\/td><td>' + String(pl_dci) +
                        '<\/td><td>' + String(opp) + '<\/td><td>' +
                        String(opp_dci) + '<\/td><td>' + String(points) +
                        '<\/td><\/td>';
            rows.push(pairings_string);
        }
        let output_table = header;
        output_table += '<tr><td colspan="6">-------------------------------' +
        '-------------------------------------------------------------------' +
        '---------------------------------------------<\/td><\/tr>';
        for (let row of rows) {
            output_table += row;
        }
        output_table += '<\/table>';
        document.write('<br><br>Pairings by Name<br>' +  'Tournament-ID: ' +
                       String(this.tournament_id) + '<br>Event Date: ' +
                       String(this.date) + '<br>Event Information: ' +
                       String(this.event_information) + '<br>Round ' +
                       String(this.round_no) + ' of ' +
                       String(this.no_of_rounds) + '<br><br>');
        document.write(output_table);
    }

    print_standings() {
        this.sort_players('oppscore');
        document.write('<br><br>Standings by Rank<br>' +  'Tournament-ID: ' +
                       String(this.tournament_id) + '<br>Event Date: ' +
                       String(this.date) + '<br>Event Information: ' +
                       String(this.event_information) + '<br><br>Opponents Match ' +
                       'Win Percent: OMW%<br>Game Win Percent: GW%' +
                       '<br>Opponents Game Win Percent: OGW%<br><br>');
        let header = '<table style="width:50%"><tr><td>Rank<\/td><td>Name<\/td><td>' +
                   'Points<\/td><td>OMW%<\/td><td>GW%<\/td><td>' +
                   'OGW%<\/td><\/td>';
        let rank = 1;
        let rows = [];
        for (let player of this.players) {
            let pairings_string = '<tr><td>' + String(rank) + '<\/td><td>' +
                String(player.name) + '<\/td><td>' + String(player.points_total) +
                '<\/td><td>' + String(player.omw * 100) + '<\/td><td>' +
                String(player.pgw * 100) + '<\/td><td>' + String(player.ogw * 100) +
                '<\/td><\/td>';
            rows.push(pairings_string);
            rank ++;
        }
        let output_table = header;
        output_table += '<tr><td colspan="6">-------------------------------' +
        '-------------------------------------------------------------------' +
        '---------------------------------------------<\/td><\/tr>';
        for (let row of rows) {
            output_table += row;
        }
        output_table += '<\/table>';
        document.write(output_table);
    }

    calculate_points () {
        for (let player of this.players) {
            player.points_total = player.matches_won * 3 + player.matches_drawn;
        }
        this.sort_players('points');
    }

    calculate_oppscores() {
        // calcutale own percentages
        for (let player of this.players) {
            player.mwp = player.matches_won / player.matches_played;
            player.pgw = player.games_won / player.games_played;
        }
        // calculate oppscores after
        for (let player of this.players) {
            let omws = [];
            let ogws = [];
            for (let opp of player.opponents) {
                if (opp.name != 'BYE') {
                    ogws.push(opp.pgw);
                    if (opp.mwp < 0.33) {
                        omws.push(0.33);
                    } else {
                        omws.push(opp.mwp);
                    }
                }
            }
            player.omw = mean(omws);
            player.ogw = mean(ogws);
        }
    }

    pool_players() {
        this.sort_players();
        this.pools = [[]];
        let nr = 0;
        //console.log(this.players);
        for (let i = 0; i < this.players.length; i++) {
            if (i == this.players.length - 1) {
                this.pools[nr].push(this.players[i]);
            } else if (this.players[i].points_total != this.players[i + 1].points_total) {
                this.pools[nr].push(this.players[i]);
                this.pools.push([]);
                nr ++;
            } else {
                this.pools[nr].push(this.players[i]);
            }
        }
    }

}



function list_in_list(list1, list2) {
    // check if all items of list1 are in list2
    let dci_list_1 = list1.map(i => i.dci);
    let dci_list_2 = list2.map(i => i.dci);
    let len1 = dci_list_1.length;
    let hits = 0;
    for (let dci of dci_list_1) {
        if (dci_list_2.includes(dci)) {
            hits ++;
        }
    }
    return hits == len1;
}

function shuffle(a) {
    // shuffle in place
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

function mean(array) {
    let sum = 0;
    for (let i = 0; i < array.length; i++) {
        sum += array[i];
    }
    return (sum / array.length);
}

function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min + 1) ) + min;
}

function generate_random_players(number) {
    let names = list_of_names;
    let formatted_names = []
    for (i = 0; i < names.length; i++) {
        // split the names at the first space into first- and surname
        let split_name = names[i].split(/ (.*)/);
        // format the names like "surname(s), firstname"
        formatted_names.push(split_name[1] + ', ' + split_name[0])
    }
    shuffle(formatted_names);
    let players = [];
    let generated_numbers = [];
    let dci;
    for (let i = 0; i < number; i++) {
        while (true) {
            dci = getRndInteger(1000000000, 9999999999);
            if (!generated_numbers.includes(dci)) {
                generated_numbers.push(dci);
                break;
            }
        }
        players.push(new Player(formatted_names.pop(0), dci));
    }
    return players;
}

function random_result() {
    let p1_wins, p2_wins, draws;
    let rng1 = Math.random();
    if (rng1 > 0.05) {
        let rng2 = Math.random();
        if (rng2 > 0.75) {
            return [2, 0, 0];
        } else if (rng2 > 0.5) {
            return [0, 2, 0];
        } else if (rng2 > 0.25) {
            return [2, 1, 0];
        } else {
            return [1, 2, 0];
        }
    } else {
        return [1, 1, 1];
    }

}

function simulate_round(tournament) {
    tournament.new_round();
    console.log(tournament.round_no);
    tournament.print_pairings();
    for (let i = 0; i < tournament.pairings.length - 1; i++) {
        let table = i;
        let result = random_result()
        tournament.enter_result(table, result);
    }
    tournament.calculate_points();
}

let event = new Tournament();
event.starting_table = 10;
event.players = generate_random_players(27);
event.calculate_rounds();

for (let i = 0; i < event.no_of_rounds; i++) {
    simulate_round(event);
}

event.calculate_oppscores();
event.print_standings();

// check for doubled pairings
for (player of event.players) {
    player.opponents.sort();
    var results = [];
    for (var i = 0; i < player.opponents.length - 1; i++) {
        if (player.opponents[i + 1] == player.opponents[i]) {
            results.push(player.opponents[i]);
        }
    }
    if (results.length > 0) {
        console.log(results);
        console.log(player.opponents);
    }
}
