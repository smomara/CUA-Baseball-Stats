from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import pandas as pd

# Scrape html
url = "http://www.catholicathletics.com/sports/bsb/2021-22/teams/catholic?view=lineup&r=0&pos="
response = Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(response).read()
page_soup = soup(webpage, "html.parser")

# Create 2D array containing extended hitting stats for each player
extended = []
table = page_soup.findAll("div", "stats-wrap clearfix")[1].findChild("table")
for row in table.find_all("tr")[1:]:
    player = [cell.get_text(strip=True) for cell in row.find_all("td")]
    player[1] = " ".join(player[1].strip().split())
    extended.append(player)

# Clean the array
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

# Create 2D array containing all basic hitting stats for each player
basic = []
table = page_soup.find("td", "sort").find_parent("table")
for row in table.find_all("tr")[1:]:
    player = [cell.get_text(strip=True) for cell in row.find_all("td")]
    player[1] = " ".join(player[1].strip().split())
    basic.append(player)

# Clean the array
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

# Combine both arrays
table = {}
for player in basic:
    table[player[0]] = player[1:]
individual_master = []
for player in extended:
    key = player[0]
    if key in table:
        individual_master.append([key] + table[key] + player[4:])

# Constants for the fields in each subarray
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

# Functions to calculate extra extended stats
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

# wOBA weights from Tango
def calcwOBA(player):
    numerator = 0.72 * player[BB] + 0.75 * player[HBP] +  0.9 * (player[H] - player[DOUBLE] - player[TRIPLE] - player[HR]) + 1.24 * player[DOUBLE] + 1.56 * player[TRIPLE] + 1.95 * player[HR]
    denominator = player[AB] + player[BB] + player[SF] + player[HBP]
    
    if denominator <= 0:
        return "-"
    else:
        return f"{numerator/denominator:.3f}"

# Create a dataframe with selected statistics
columns = ['No.', 'Player', 'PA', 'HR', 'R', 'RBI', 'SB', 'BB%', 'K%', 'ISO', 'BABIP', 'AVG', 'OBP', 'SLG', 'wOBA']
df = pd.DataFrame(columns=columns)

for player in individual_master:
    data = {
        'No.': player[NUM],
        'Player': player[NAME],
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
        'wOBA': f"{calcwOBA(player)}"
    }

    df = pd.concat([df, pd.DataFrame(data, index = [0])], ignore_index = True)

# Export df as csv
csv_table = df.to_csv(header = False, index = False)
with open('C:/Users/Max/Documents/smomara.github.io/2022/table2022.csv', 'w') as f:
    f.write(csv_table)






