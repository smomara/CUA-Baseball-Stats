from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import pandas as pd

BPF = 1.05

def generateIndividualStats(url):
    response = Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(response).read()
    page_soup = soup(webpage, "html.parser")

    extended = []
    table = page_soup.findAll("div", "stats-wrap clearfix")[1].findChild("table")
    for row in table.find_all("tr")[1:]:
        player = [cell.get_text(strip=True) for cell in row.find_all("td")]
        player[1] = " ".join(player[1].strip().split())
        extended.append(player)

    extended = extended[:-2]
    for i in range(len(extended)):
        for j in range(len(extended[i])):
                    if j == 0 or j == 14 or j > 3 and j < 13:
                        if extended[i][j] == "-":
                            extended[i][j] = 0
                        else:
                            extended[i][j] = int(extended[i][j])
                    if j == 13:
                        if extended[i][j] == "-":
                            extended[i][j] = 0.0
                        else:
                            extended[i][j] = float(extended[i][j])

    basic = []
    table = page_soup.find("td", "sort").find_parent("table")
    for row in table.find_all("tr")[1:]:
        player = [cell.get_text(strip=True) for cell in row.find_all("td")]
        player[1] = " ".join(player[1].strip().split())
        basic.append(player)

    basic = basic[:-2]
    for i in range(len(basic)):
        for j in range(len(basic[i])):
            if j == 0 or j > 3 and j < 16:
                if basic[i][j] == "-":
                    basic[i][j] = 0
                else:
                    basic[i][j] = int(basic[i][j])
            elif j >= 16:
                basic[i][j] = float(basic[i][j])

    table = {}
    for player in basic:
        table[player[0]] = player[1:]

    individual_master = []
    for player in extended:
        key = player[0]
        if key in table:
            individual_master.append([key] + table[key] + player[4:])
    
    return individual_master

def generateTeamStats(url):
    response = Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(response).read()
    page_soup = soup(webpage, "html.parser")
    
    batting = []
    table = page_soup.find("th", string = "AVG").find_parent("table")
    for row in table.find_all("tr")[1:]:
        batting.append([cell.get_text(strip=True) for cell in row.find_all("td")])
    for i, row in enumerate(table.find_all("tr")[1:]):
        batting[i][0] = [cell.get_text(strip=True) for cell in row.find_all("th")][0]

    for i in range(len(batting)):
        for j in range(len(batting[i])):
            if j == 1 or j == 11 or j == 16 or j == 23:
                batting[i][j] = float(batting[i][j])
            elif j != 0 and j != 19:
                batting[i][j] = int(batting[i][j])
                
    pitching = []
    table = page_soup.find("th", string = "ERA").find_parent("table")
    for row in table.find_all("tr")[1:]:
        pitching.append([cell.get_text(strip=True) for cell in row.find_all("td")])
    for i, row in enumerate(table.find_all("tr")[1:]):
        pitching[i][0] = [cell.get_text(strip=True) for cell in row.find_all("th")][0]

    for i in range(len(pitching)):
        for j in range(len(pitching[i])):
            if j == 1 or j == 16:
                pitching[i][j] = float(pitching[i][j])
            elif j != 0 and j != 2 and j != 11 and j != 6:
                pitching[i][j] = int(pitching[i][j])
            elif j == 6:
                pitching[i][j] = round(float(pitching[i][j]))
    
    table = {}
    for team in batting:
        table[team[0]] = team[1:]

    team_master = []
    for team in pitching:
        key = team[0]
        if key in table:
            team_master.append([key] + table[key] + team[1:])
    
    return team_master

def calcLeagueStats(team_master):
    total = []
    for j in range(len(team_master[0])):
        if j in set([3, 4, 5, 6, 7, 8, 12, 13, 17, 29]):
            count = 0
            for i in range(len(team_master)):
                count += team_master[i][j]
            total.append(count)
        elif j == 19:
            SB_count = 0
            CS_count = 0
            for i in range(len(team_master)):
                SB_count += int(team_master[i][j].strip().split("-")[0])
                CS_count += int(team_master[i][j].strip().split("-")[1]) - int(team_master[i][j].strip().split("-")[0])
            total.append(SB_count)
            total.append(CS_count)
    
    league_AB = total[0]
    league_R = total[1]
    league_H = total[2]
    league_DOUBLE = total[3]
    league_TRIPLE = total[4]
    league_HR = total[5]
    league_SINGLE = league_H - league_DOUBLE - league_TRIPLE - league_HR
    league_BB = total[6]
    league_HBP = total[7]
    league_SF = total[8]
    league_SB = total[9]
    league_CS = total[10]
    league_IP = int(total[11])
    league_PA = league_AB + league_BB + league_SF + league_HBP
    league_runCS = -1 * (2 * league_R / (league_IP * 3) + 0.075)
    league_wSB = (league_SB * 0.2 + league_CS * league_runCS) / (league_SINGLE + league_BB + league_HBP)
    league_wOBA = float(f"{(0.72 * league_BB + 0.75 * league_HBP +  0.9 * league_SINGLE + 1.24 * league_DOUBLE + 1.56 * league_TRIPLE + 1.95 * league_HR) / league_PA}")
    
    return league_AB, league_R, league_H, league_DOUBLE, league_TRIPLE, league_HR, league_SINGLE, league_BB, league_HBP, league_SF, league_SB, league_CS, league_IP, league_PA, league_runCS, league_wSB, league_wOBA

NUM = 0
NAME = 1
YR = 2
POS = 3
G = 4
AB = 5
R = 6
H = 7
DOUBLE = 8
TRIPLE = 9
HR = 10
RBI = 11
BB = 12
K = 13
SB = 14
CS = 15
AVG = 16
OBP = 17
SLG = 18
G = 19
HBP = 20
SF = 21
SH = 22
TB = 23
XHB = 24
HDP = 25
GO = 26
FO = 27
GOFO = 28
PA = 29

def calcSINGLE(player):
    return player[H] - player[DOUBLE] - player[TRIPLE] - player[HR]

def calcBABIP(player):
    numerator = player[H] - player[HR]
    denominator = player[AB] - player[HR] - player[K] + player[SF]
    
    if denominator == 0:
        return "-"
    else:
        return f"{numerator/denominator:.3f}"

def calcISO(player):
    return f"{player[SLG] - player[AVG]:.3f}"

def calcBBrate(player):
    if player[PA] == 0:
        return "-"
    else:
        return f"{player[BB]/player[PA] * 100:.1f}"

def calcKrate(player):
    if player[PA] == 0:
        return "-"
    else:
        return f"{player[K]/player[PA] * 100:.1f}"

def calcwOBA(player):
    numerator = 0.72 * player[BB] + 0.75 * player[HBP] +  0.9 * calcSINGLE(player) + 1.24 * player[DOUBLE] + 1.56 * player[TRIPLE] + 1.95 * player[HR]
    denominator = player[AB] + player[BB] + player[SF] + player[HBP]
    return float(f"{numerator/denominator:.3f}")

def calcwRAA(player):
    return float(f"{(calcwOBA(player) - league_wOBA) / 1.15 * player[PA]:.1f}")

def calcwRC(player):
    return float(f"{(((calcwOBA(player) - league_wOBA) / 1.15) + (league_R / league_PA)) * player[PA]:.1f}")

def calcwRCPlus(player):
    return float(f"{(((calcwRAA(player) / player[PA] + league_R / league_PA) + (league_R / league_PA - BPF * league_R / league_PA)) / (league_R / league_PA) * 100):.1f}")

def calcwSB(player):
    wSB = float(f"{player[SB] * 0.2 + player[CS] * league_runCS - league_wSB * (calcSINGLE(player) + player[BB] + player[HBP]):.1f}")
    if wSB == 0.0:
        return 0.0
    return wSB

def calcBattingRunsAboveAverage(player):
    return calcwRAA(player) + (league_R / league_PA - (BPF * league_R / league_PA)) * player[PA] + (league_R / league_PA - (league_R / league_PA)) * player[PA]

def generateDataFrame(individual_master):
    columns = ['Player', 'G', 'PA', 'HR', 'R', 'RBI', 'SB', 'BB%', 'K%', 'ISO', 'BABIP', 'AVG', 'OBP', 'SLG', 'wOBA', 'wRC+', 'wSB', 'Off']
    df = pd.DataFrame(columns=columns)

    for player in individual_master:
        data = {
            'Player': player[NAME],
            'G': player[G],
            'PA': player[PA],
            'HR': player[HR],
            'R': player[R],
            'RBI': player[RBI],
            'SB': player[SB],
            'BB%': f"{calcBBrate(player)}%",
            'K%': f"{calcKrate(player)}%",
            'ISO': calcISO(player),
            'BABIP': calcBABIP(player),
            'AVG': f"{player[AVG]:.3f}",
            'OBP': f"{player[OBP]:.3f}",
            'SLG': f"{player[SLG]:.3f}",
            'wOBA': f"{calcwOBA(player):.3f}",
            'wRC+': calcwRCPlus(player),
            'wSB': f"{calcwSB(player):.1f}",
            'Off': f"{calcwSB(player) + calcBattingRunsAboveAverage(player):.1f}"
        }

        df = pd.concat([df, pd.DataFrame(data, index = [0])], ignore_index = True)
        
    return df

def exportCSV(df, filepath):
    csv_table = df.to_csv(header = False, index = False)
    with open(filepath, 'w') as f:
        f.write(csv_table)

individual_stats = generateIndividualStats("http://www.catholicathletics.com/sports/bsb/2022-23/teams/catholic?view=lineup&r=0&pos=")
team_stats = generateTeamStats("https://landmarkconference.org/stats.aspx?path=baseball&year=2023")
league_AB, league_R, league_H, league_DOUBLE, league_TRIPLE, league_HR, league_SINGLE, league_BB, league_HBP, league_SF, league_CS, league_SB, league_IP, league_PA, league_runCS, league_wSB, league_wOBA = calcLeagueStats(team_stats)
exportCSV(generateDataFrame(individual_stats), 'C:\\Users\\Max\\Documents\\smomara.github.io\\2023\\table2023.csv')

individual_stats = generateIndividualStats("http://www.catholicathletics.com/sports/bsb/2021-22/teams/catholic?view=lineup&r=0&pos=")
team_stats = generateTeamStats("https://landmarkconference.org/stats.aspx?path=baseball&year=2022")
league_AB, league_R, league_H, league_DOUBLE, league_TRIPLE, league_HR, league_SINGLE, league_BB, league_HBP, league_SF, league_CS, league_SB, league_IP, league_PA, league_runCS, league_wSB, league_wOBA = calcLeagueStats(team_stats)
exportCSV(generateDataFrame(individual_stats), 'C:\\Users\\Max\\Documents\\smomara.github.io\\2022\\table2022.csv')