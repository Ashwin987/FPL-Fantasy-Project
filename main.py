from bs4 import BeautifulSoup
import requests
import unidecode
import csv

#database of 2021-22 FPL players with their positions
players_url = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/2021-22/cleaned_players.csv'
players_table = requests.get(players_url).text
positions_db = BeautifulSoup(players_table, 'lxml')

#database of 2021-22 FPL players with price data
price_data = 'https://github.com/vaastav/Fantasy-Premier-League/blob/master/data/2021-22/players_raw.csv'
price_table = requests.get(price_data).text
prices_db = BeautifulSoup(price_table, 'lxml')

stats_dict = {}     #midfielders and their stats
name_convert = {}   #name differences between FBref and GitHub databases
mids = []           #midfielder names from GitHub databases
minutes = []
points = []
initial_price = []
final_pct_selected = []

price_table_body = prices_db.find('table', class_ = 'js-csv-data csv-data js-file-line-container').tbody
price_table_rows = price_table_body.find_all('tr')

rows = positions_db.find_all('tr', class_ = 'js-file-line')
for row in rows:
    row_data = row.find_all('td')
    pos = row_data[-1].text
    
    #get FPL midfielders
    if pos == 'MID':
        mins_played = row_data[6].text
        
        #get midfielders who had playing time
        if mins_played != '0':
            minutes.append(int(mins_played))
            points.append(int(row_data[5].text))
            first_name = row_data[1].text
            last_name = row_data[2].text
            
            #remove accent marks
            mids.append(unidecode.unidecode(first_name + ' ' + last_name))

            player_index = rows.index(row) - 1
            price_row = price_table_rows[player_index]
            cells = price_row.find_all('td')
            
            price_change = float(cells[12].text) / 10
            final_price = float(cells[39].text) / 10
            initial_price.append(final_price - price_change)
            final_pct_selected.append(float(cells[50].text))

#page with all 380 match reports
games_url = 'https://fbref.com/en/comps/9/2021-2022/schedule/2021-2022-Premier-League-Scores-and-Fixtures'
all_games = requests.get(games_url).text
games_db = BeautifulSoup(all_games, 'lxml')

reports = []
rows = games_db.find_all('td', attrs = {'data-stat' : 'match_report'})
for row in rows:
    if row.text.strip() != '':
        reports.append('https://fbref.com' + row.a['href'])

count = 0

#for each match report
for report_url in reports:
    count += 1
    print(count)
    report = requests.get(report_url).text
    match_report_data = BeautifulSoup(report, 'lxml')

    rows = match_report_data.find_all('div', class_ = 'table_wrapper tabbed')
    for row in rows:
    
        #find the 2 tables with stats of all players (1 table per team)
        if 'all_player_stats' in row.get('id'):
            
            #summary table contains interceptions data
            summary_table = row.find('tbody')
            summary_rows = summary_table.find_all('tr')

            players = []    #players who played in the match (all positions)
                            #FBref positions are different from official FPL positions – wingers are considered FPL midfielders

            #for each player who made an appearance in the match
            for table_row in summary_rows:
            
                #player's name on FBref
                name = unidecode.unidecode(table_row.a.text)
                players.append(name)
                full_name = name
                
                #if player's FBref name is 1 word (Fabinho, Jorginho, Martinelli, etc.)
                if name.split()[0] == name.split()[-1]:
                
                    #player profile page
                    player_link = 'https://fbref.com' + table_row.a['href']
                    page = requests.get(player_link).text
                    player_profile_page = BeautifulSoup(page, 'lxml')
                    header = player_profile_page.find('div', attrs = {'id' : 'meta'})
                    
                    #if player's FBref name is different from full name, the first profile entry is their full name
                    #otherwise, it is the word 'Position:'
                    profile = header.find('strong').text
                    if profile != 'Position:':
                        full_name = unidecode.unidecode(profile)
                
                #edge cases – full name is set to Github database name
                if name == 'Rodri':
                    full_name = 'Rodrigo Hernandez'
                if name == 'Son Heung-min':
                    full_name = 'Heung-Min Son'
                if name == 'Joe Willock':
                    full_name = 'Joseph Willock'
                if name == 'Solly March':
                    full_name = 'Solomon March'
                if name == 'Dele Alli':
                    full_name = 'Bamidele Alli'
                if name == 'James Mcatee':
                    full_name = 'James McAtee'
                if name == 'Jesuran Rak Sakyi':
                    full_name = 'Jesurun Rak-Sakyi'
                if name == 'Jaden Philogene Bidace':
                    full_name = 'Jaden Philogene-Bidace'
                
                first_last = full_name.split()
                
                #check if player is an FPL midfielder
                for mid in mids:
                    if first_last[0] in mid and first_last[-1] in mid:
                    
                        #if player isn't in dictionaries
                        if name_convert.get(name) == None:
                            name_convert[name] = mid
                            pos = mids.index(mid)
                            original_pts = points[pos]
                            mins = minutes[pos]
                            starting_price = initial_price[pos]
                            pct_selected = final_pct_selected[pos]
                            stats_dict[name] = {'Interceptions': 0, 'Tackles Won': 0, 'GW Recoveries': 0, 'Ball Recovery Points': 0, 'Total Points': original_pts, 'Minutes': mins, 'Starting Price': starting_price, 'Final Teams Selected By %': pct_selected}
                        
                        ints = table_row.find('td', attrs = {'data-stat' : 'interceptions'}).text
                        
                        #total interceptions for the entire season
                        stats_dict[name]['Interceptions'] += int(ints)
                        
                        #number of recoveries for this match – temporary variable, used to calculate recovery points for this match
                        stats_dict[name]['GW Recoveries'] = int(ints)

            #other tables in match report
            tabs = row.find_all('div', attrs = {'class' : True, 'id' : True})
            for tab in tabs:
            
                #find defensive actions tables – contains tackles won data
                if 'defense' in tab.get('id') and tab.table != None:
                    defense_table_body = tab.find('tbody')
                    defense_rows = defense_table_body.find_all('tr')
                    for defense_row in defense_rows:
                        pos = defense_rows.index(defense_row)
                        name = players[pos]
                        
                        #if player is an FPL midfielder, his name will already be in stats_dict
                        if stats_dict.get(name) != None:
                            tklw = defense_row.find('td', attrs = {'data-stat' : 'tackles_won'}).text
                            
                            #total tackles won for the entire season
                            stats_dict[name]['Tackles Won'] += int(tklw)
                            
                            #add interceptions with tackles won to get total recoveries in this match
                            stats_dict[name]['GW Recoveries'] += int(tklw)
                            
                            #1 point for every 3 recoveries in the match
                            pts = stats_dict[name]['GW Recoveries'] / 3
                            
                            #total points for ball recoveries for the entire season
                            stats_dict[name]['Ball Recovery Points'] += pts
                            
                            #new total points for the entire points, including ball recovery points
                            stats_dict[name]['Total Points'] += pts

#delete temporary recoveries variable (currently set to number of recoveries from last match played)
for key, val in stats_dict.items():
    del val['GW Recoveries']

#write data to csv file
with open('midfielders.csv', 'w') as csv_file:
    field_names = ['Player', 'Minutes', 'Starting Price', 'Final Teams Selected By %', 'Interceptions', 'Tackles Won', 'Ball Recovery Points', 'Total Points']
    writer = csv.DictWriter(csv_file, field_names)
    for key, val in sorted(stats_dict.items()):
        r = {'Player' : key}
        r.update(val)
        writer.writerow(r)
