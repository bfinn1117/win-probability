import requests
import matplotlib.pyplot as plt
import json
import sys

if len(sys.argv) != 2:
    sys.exit("Sorry, correct usage is python main.py {insert gameID}")

# Example Game IDs for testing:
# 5/1: 718353 Home team: Red Sox https://www.mlb.com/gameday/blue-jays-vs-red-sox/2023/05/01/718353/final/wrap
# 5/6: 718284 Home team: Phillies https://www.mlb.com/gameday/red-sox-vs-phillies/2023/05/06/718284/final
# 5/7: 718270 Home team: Phillies https://www.mlb.com/gameday/red-sox-vs-phillies/2023/05/07/718270/final 

gameId = sys.argv[1]

url = "https://ws.statsapi.mlb.com/api/v1.1/game/" + gameId + "/feed/live?language=en"

payload = {}
headers = {
  'authority': 'ws.statsapi.mlb.com',
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'max-age=0',
  'origin': 'https://www.mlb.com',
  'referer': 'https://www.mlb.com/',
  'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}
# get data from webscraping mlb.com, save to a variable
response = requests.get(url, headers=headers)
gamedata = response.json()

# getting list of innings data with run and hit data
innings = gamedata['liveData']['linescore']['innings']

# score tracking
homeScore = 0
awayScore = 0

# hit tracking
homeHits = 0
awayHits = 0
# inning variable
inn = 1

# create dictionary for home team win probabilty (value) per inning (key)
probabilityScale = {0: 50}

for inning in innings:
    homeProbability = 0.5
    # if the home team is winning, the bottom of the 9th is not played
    if inning['num'] >= 9 and homeScore > awayScore:
        awayScore += inning['away']['runs']
        awayHits += inning['away']['hits']
    else:    
        homeScore += inning['home']['runs']
        awayScore += inning['away']['runs']
        homeHits += inning['home']['hits']
        awayHits += inning['away']['hits']
    

    runDiff = homeScore - awayScore
    hitDiff = homeHits - awayHits

    # run differential scale
    # deficit scale
    if runDiff <= -5:
        homeProbability -= .3
    elif runDiff == -4 or runDiff == -3:
        homeProbability -= .2
    elif runDiff == -1 or runDiff == -2:
        homeProbability -= .125
    # winning scale
    elif 1 <= runDiff <= 2:
        homeProbability += .125
    elif 3 <= runDiff <= 4:
        homeProbability += .2
    elif runDiff >= 5:
        homeProbability += .3


    # hit differential scale
    # deficit scale
    if hitDiff <= -6:
        homeProbability -= .15
    elif hitDiff == -4 or hitDiff == -5:
        homeProbability -= .1
    elif -3 <= hitDiff <= -1:
        homeProbability -= .05
    # winning scale
    elif 1<= hitDiff <= 3:
        homeProbability += .05
    elif 4 <= hitDiff <= 5:
        homeProbability += .1
    elif hitDiff >= 6:
        homeProbability += .15

    print("Inning #" + str(inn) + ": ")
    print("Run Diff: " + str(runDiff))
    print("Hit Diff: " + str(hitDiff))
    print("Home Team Win Probability: " + str(homeProbability * 100) + "%")
    print("")

    # add new inning probability to dict
    probabilityScale[inn] = homeProbability * 100
    # next inning
    inn += 1
    
print(probabilityScale)

names = list(probabilityScale.keys())
values = list(probabilityScale.values())

if homeScore > awayScore:
    print("Home team wins!")
else:
    print("Home team loses :(")
    #print(str(homeProbability))

plt.plot(names, values)
plt.xlabel("Inning")
plt.xlim([0, 9])
plt.ylabel("Home Team Win Probability")
plt.ylim([0, 100])
plt.show()


