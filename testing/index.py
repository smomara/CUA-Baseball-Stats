from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup

response = Request("https://www.d3baseball.com/seasons/2023/schedule/", headers = {'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(response).read()
page_soup = soup(webpage, "html.parser")

games = []
count = 0
index = -1
table = page_soup.find("tr", "roster-row0").find_parent("table")
for row in table.find_all("td")[6:]:
    curr = [cell.get_text(strip = True) for cell in row]
    
    if count % 7 == 0:
        index += 1
        games.append([])
        
    games[index].append([cell.get_text(strip = True) for cell in row])
    count += 1

for i in range(len(games)):
    games[i] = [elem for sublist in games[i] for elem in sublist]
    
ttf_games = []
index = -1
for game in games:
    if game[0][:3] == "No." or game[6][:3] == "No.":
        ttf_games.append([game[0], game[1], game[4], game[6], game[7], game[10], game[12]])

for game in ttf_games:
    if len(game[0]) > 0:
        game[0] = game[0].strip().split()[1] + " "
    
    if len(game[3]) > 0:
        game[3] = game[3].strip().split()[1] + " "
    
    if len(game[6].strip().split()) > 2:
        if game[6].strip().split()[0] == "Bottom":
            game[6] = " ".join(["Bot", game[6].strip().split()[2][:-2]])
        elif game[6].strip().split()[0] == "Top":
            game[6] = " ".join(["Top", game[6].strip().split()[2][:-2]])

def sort_key(subarr):
    last_elem = subarr[-1]
    if last_elem.startswith('Bot'):
        return (0, int(last_elem.split()[1]))
    elif last_elem.startswith('Top'):
        return (1, int(last_elem.split()[1]))
    elif last_elem.startswith('Final'):
        return (2,)
    elif ':' in last_elem:
        return (3, last_elem)
    elif last_elem == 'Cancelled' or last_elem == 'Postponed':
        return (4,)
    else:
        return (5,)

ttf_games = sorted(ttf_games, key = sort_key)

for game in ttf_games:
    if game[2] != "" and game[5] != "":
        row = f"{game[0]}{game[1]} @ {game[3]}{game[4]}: {game[2]} - {game[5]} {game[6]}"
    else:
        row = f"{game[0]}{game[1]} @ {game[3]}{game[4]}: {game[6]}"
    print(f"document.getElementById('output').innerHTML += '{row}\\n';")