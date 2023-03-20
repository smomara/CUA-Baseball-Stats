fetch("https://www.d3baseball.com/seasons/2023/schedule/", {
    mode: "cors",
    headers: {
      "Access-Control-Allow-Origin": "*"
    }
  })
  .then(response => response.text())
  .then(html => {
    const parser = new DOMParser();
    const page_soup = parser.parseFromString(html, "text/html");

    const games = [];
    let count = 0;
    let index = -1;
    const table = page_soup.querySelector(".roster-row0").parentNode;
    for (const row of table.querySelectorAll("td").values()) {
      const curr = [...row.childNodes].map(cell => cell.textContent.trim());

      if (count % 7 === 0) {
        index += 1;
        games.push([]);
      }

      games[index].push(curr);
      count += 1;
    }

    for (let i = 0; i < games.length; i++) {
      games[i] = games[i].flat();
    }

    const ttf_games = [];
    index = -1;
    for (const game of games) {
      if (game[0].startsWith("No.") || game[6].startsWith("No.")) {
        ttf_games.push([game[0], game[1], game[4], game[6], game[7], game[10], game[12]]);
      }
    }

    for (const game of ttf_games) {
      if (game[0].length > 0) {
        game[0] = game[0].trim().split(" ")[1] + " ";
      }

      if (game[3].length > 0) {
        game[3] = game[3].trim().split(" ")[1] + " ";
      }

      if (game[6].trim().split(" ").length > 2) {
        if (game[6].startsWith("Bottom")) {
          game[6] = `Bot ${game[6].trim().split(" ")[2].slice(0, -2)}`;
        } else if (game[6].startsWith("Top")) {
          game[6] = `Top ${game[6].trim().split(" ")[2].slice(0, -2)}`;
        }
      }
    }

    function sort_key(subarr) {
      const last_elem = subarr.slice(-1)[0];
      if (last_elem.startsWith("Bot")) {
        return [0, parseInt(last_elem.trim().split(" ")[1], 10)];
      } else if (last_elem.startsWith("Top")) {
        return [1, parseInt(last_elem.trim().split(" ")[1], 10)];
      } else if (last_elem.startsWith("Final")) {
        return [2];
      } else if (last_elem.includes(":")) {
        return [3, last_elem];
      } else if (last_elem === "Cancelled" || last_elem === "Postponed") {
        return [4];
      } else {
        return [5];
      }
    }

    const sorted_ttf_games = ttf_games.sort((a, b) => {
      const key_a = sort_key(a);
      const key_b = sort_key(b);
      for (let i = 0; i < Math.min(key_a.length, key_b.length); i++) {
        if (key_a[i] < key_b[i]) {
          return -1;
        } else if (key_a[i] > key_b[i]) {
          return 1;
        }
      }
      return 0;
    });
    console.log(sorted_ttf_games);
  })
  .catch(error => console.error(error));