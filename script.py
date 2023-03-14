from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import pandas as pd

# Parse the HTML
url = "http://www.catholicathletics.com/sports/bsb/2022-23/teams/catholic?view=lineup&r=0&pos="
response = Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(response).read()
page_soup = soup(webpage, "html.parser")


# Create a 2D array containing all extended hitting statistics
extended_master = []
table = page_soup.findAll("div", "stats-wrap clearfix")[1].findChild("table")
for row in table.find_all("tr")[1:]:
    player = [cell.get_text(strip=True) for cell in row.find_all("td")]
    player[1] = " ".join(player[1].strip().split())
    extended_master.append(player)

extended_master = extended_master[:-2]

for i in range(len(extended_master)):
    for j in range(len(extended_master[i])):
                if j == 0 or j == 14 or j > 3 and j < 13:
                    if extended_master[i][j] == "-":
                        extended_master[i][j] = 0
                    else:
                        extended_master[i][j] = int(extended_master[i][j])
                if j == 13:
                    if extended_master[i][j] == "-":
                        extended_master[i][j] = 0.0
                    else:
                        extended_master[i][j] = float(extended_master[i][j])

# Create a 2D array containing all basic hitting statistics
basic_master = []
table = page_soup.find("td", "sort").find_parent("table")
for row in table.find_all("tr")[1:]:
    player = [cell.get_text(strip=True) for cell in row.find_all("td")]
    player[1] = " ".join(player[1].strip().split())
    basic_master.append(player)

basic_master = basic_master[:-2]

for i in range(len(basic_master)):
    for j in range(len(basic_master[i])):
        if j == 0 or j > 3 and j < 16:
            if basic_master[i][j] == "-":
                basic_master[i][j] = 0
            else:
                basic_master[i][j] = int(basic_master[i][j])
        elif j >= 16:
            basic_master[i][j] = float(basic_master[i][j])

# Combine the basic and extended arrays into a master array
table = {}
for player in basic_master:
    table[player[0]] = player[1:]

master = []
for player in extended_master:
    key = player[0]
    if key in table:
        master.append([key] + table[key] + player[4:])

# Constant variable representing a statistic corresponding to each field in each subarray
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

# Functions to calculate extra statistics
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

# Create a pandas dataframe containing specific stats
columns = ['No.', 'Player', 'PA', 'HR', 'R', 'RBI', 'SB', 'BB%', 'K%', 'ISO', 'BABIP', 'AVG', 'OBP', 'SLG']
df = pd.DataFrame(columns=columns)

for player in master:
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
        'SLG': f"{player[SLG]:.3f}"
    }

    df = pd.concat([df, pd.DataFrame(data, index = [0])], ignore_index = True)

# Save and export the dataframe as a csv
csv_table = df.to_csv(index = False)
with open('C:/Users/Max/Documents/smomara.github.io/table2022.csv', 'w') as f:
    f.write(csv_table)

