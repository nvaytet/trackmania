import numpy as np
import requests
import re
import datetime
import hashlib


def string_to_milliseconds(string):
    elems = re.split("h|'|\"", string)
    milliseconds = float(elems[-1]) * 10.0 + float(elems[-2]) * 1000.0 + float(
        elems[-3]) * 60000.0
    if len(elems) > 3:
        milliseconds += float(elems[0]) * 3.6e6
    return milliseconds


def get_medal_times(url, medal_names):
    print("Getting medal times")
    medals_source = requests.get(url).text.split("<tr")
    data = dict()

    for t in medals_source:
        searchObj = re.search("<td>[A-E][0-1][0-9]-(.*)", t)
        if searchObj:
            line = t.split("<td>")
            name = re.sub("</?td>", "", searchObj.group().replace("\r", ""))
            data[name] = dict()
            for i, n in enumerate(medal_names):
                raw_time = line[5 + i].split("<")[0]
                data[name][n] = string_to_milliseconds(raw_time)
            data[name]["fastest_time"] = None
    return data


def get_custom_tracks(data, url):
    print("Getting custom tracks")
    custom_tracks = [
        "F01-Race.Gbx", "F03-Obstacle.Gbx", "F05-Endurance.Gbx",
        "F07-Race.Gbx", "F09-Speed.Gbx", "F11-Race.Gbx", "F13-Race.Gbx",
        "F15-Endurance.Gbx"
    ]
    medal_names = ["bronze", "silver", "gold", "authortime"]
    for t in custom_tracks:
        content = requests.get(url + t).text
        key = t.replace(".Gbx", "")
        data[key] = {}
        for med in medal_names:
            searchObj = re.search(med + '=\"(.*)\"', content)
            if searchObj:
                time = float(searchObj.group(1).split()[0].replace('"', ""))
                if med == "authortime":
                    name = "author"
                else:
                    name = med
                data[key][name] = time
        print("-", key, ":", data[key])
        data[key]["fastest_time"] = None
    return


def milliseconds_to_string(milliseconds):
    if milliseconds < 0:
        return ""
    else:
        duration = str(datetime.timedelta(milliseconds=milliseconds))
        if duration.startswith("0:"):
            duration = duration[2:]
        if duration.endswith("000"):
            duration = duration[:-3]
        return duration


def make_ghost_file_name(key="", player="", suffix=".gbx", url=""):
    return "{}{}-{}{}".format(url, key, player, suffix)


def extract_time_from_file(file_url):
    time = None
    try:
        content = requests.get(file_url).text
        searchObj = re.search("best=(.*) ", content)
        if searchObj:
            time = float(searchObj.group(1).split()[0].replace('"', ""))
    except ConnectionError:
        pass
    return time


def get_player_times(players, data, medal_names, base_url):
    for p in players.keys():
        print("Getting times for player: {}".format(p))
        for key in data.keys():
            suffix = ".gbx"
            time = extract_time_from_file(
                make_ghost_file_name(key=key,
                                     player=p,
                                     suffix=suffix,
                                     url=base_url))
            if time is None:
                suffix = ".Gbx"
                time = extract_time_from_file(
                    make_ghost_file_name(key=key,
                                         player=p,
                                         suffix=suffix,
                                         url=base_url))
            if time is not None:
                data[key][p] = dict()
                data[key][p]["time"] = time
                if data[key]["fastest_time"] is None:
                    data[key]["fastest_time"] = time
                else:
                    data[key]["fastest_time"] = min(data[key]["fastest_time"],
                                                    time)
                nmedals = 0
                for n in medal_names:
                    if time < data[key][n]:
                        nmedals += 1
                data[key][p]["medals"] = nmedals
                data[key][p]["url"] = make_ghost_file_name(key=key,
                                                           player=p,
                                                           suffix=suffix)
                print("  - {} : {}".format(key, time))
    return


def create_race_plots(players, data):

    archive = requests.get(
        "https://sites.google.com/site/trackmaniachampionnat/archive"
    ).text.split("\n")

    for key in data.keys():
        for p in players.keys():
            name = make_ghost_file_name(url="", key=key, player=p)
            print(name)

            # Search for the Race-Player.gbx string in the archive source
            for i in range(len(archive)):
                if archive[i].find(name) >= 0:
                    # Get the source of the page listing the version dates
                    wuid = re.search(
                        "id=\"JOT_FILECAB_label_(.*)\" aria-hidden",
                        archive[i])
                    # if wuid:
                    print(wuid.group(1))
                    # exit()
                    url = "https://sites.google.com/site/trackmaniachampionnat/system/app/pages/admin/revisions?wuid=" + wuid.group(
                        1)
                    date_page = requests.get(url).text.split("\n")
                    # print(len(date_page))
                    # exit()
                    # Find out how many different versions of the file there are
                    for line in date_page:
                        print(line)
                    #     if line.find("(current)") >= 0:
                    #         print(line)
                    #         exit()
                    #         break
                    # # Then cycle through the different versions and get both ghost time and file upload date
                    exit()

                    # searchObj = re.search("target=\"_new\">Version (.*)</a> (current)

                    # print(archive[i+3])
                    searchObj = re.search(">v\. (.*)  </td>", archive[i + 3])
                    if searchObj:
                        nversions = int(searchObj.group(1))
                        # gather_versions()
                        # print(version)
                        # print(searchObj.group(1))
                        for n in range(nversions):
                            ghost_url = make_ghost_file_name(
                                key=key,
                                player=p,
                                suffix=".gbx?revision={}".format(n + 1))
                            time = extract_time_from_file(ghost_url)
                            # if time is not None:

                    break

            exit()


#===============================================================================

standalone = False
fetch_new_ghosts = False
base_url = "https://sites.google.com/site/trackmaniachampionnat/archive/"

# Define players
player_names = [
    "Baptiste", "Neil", "Olivier", "Jacques", "Seb", "Baba", "Chris"
]

players = dict()
for p in player_names:
    players[p] = dict()
    players[p]["color"] = "#" + hashlib.md5(p.encode("utf-8")).hexdigest()[:6]
    players[p]["medals"] = 0
    players[p]["records"] = 0

record_color = "#000000"
medal_names = ["bronze", "silver", "gold", "author"]
race_groups = {
    "A": "White",
    "B": "Green",
    "C": "Blue",
    "D": "Red",
    "E": "Black",
    "F": "Yellow"
}
medal_url = "http://en.tm-ladder.com/time_page/"
image_url = medal_url + "images/"

if fetch_new_ghosts:
    # Start by getting all the medal times
    data = get_medal_times(medal_url, medal_names)
    get_custom_tracks(data, base_url)
    get_player_times(players, data, medal_names, base_url)
    # Save
    np.save('my_dict.npy', data)
else:
    # Load from file
    data = np.load('my_dict.npy', allow_pickle=True).item()

# Create HTML table
bckgrnd = "#4f4f4f"
outputHTML = ""
if standalone:
    outputHTML += "<!doctype html>\n"
    outputHTML += "<html>\n"
    outputHTML += "<head>\n"
    outputHTML += "<title>Trackmania Championnat</title>\n"
outputHTML += "<base href=\"{}\">\n".format(base_url)

outputHTML += "<style>\n"
# outputHTML += "tr {border:4px solid transparent;}\n"
# outputHTML += "tr:nth-child(odd) {background-color: #999999;}\n"
# outputHTML += "tr:nth-child(even) {background-color: #4f4f4f;}\n"
outputHTML += "a {color: #ffffff; text-decoration: none;}\n"
outputHTML += "th, tr, td, div {color: #ffffff; background-color: " + bckgrnd + ";}\n"
outputHTML += "tr:hover td { background: #AED6F1 !important; color: #000000 !important;}\n"
outputHTML += "tr:hover a {color: #000000 !important;}\n"
for n, p in players.items():
    outputHTML += ".{} {{ background-color: {} }}\n".format(n, p["color"])
    outputHTML += ".record{} {{ background: radial-gradient({}, #000000); }}\n".format(
        n, p["color"])
outputHTML += ".fontRecord {font-weight: bold;}\n"
outputHTML += ".boldCenter {font-weight: bold; text-align: center;}\n"
outputHTML += "</style>\n"
if standalone:
    outputHTML += "</head>\n"
    outputHTML += "<body>\n"
outputHTML += "<div>"
outputHTML += "<table border=\"0\" style=\"border-spacing: 10px 1px; font-family: Courier New;\">\n<th></th>\n"
for p in players.keys():
    outputHTML += "<th class=\"{}\">{}</th>\n".format(p, p)
current_group = "Z"
for race_count, key in enumerate(data.keys()):
    if current_group != key[0]:
        current_group = key[0]
        outputHTML += "<tr>\n<td colspan=\"" + str(
            len(player_names) + 1
        ) + "\">&nbsp;</td>\n</tr>\n<tr>\n<td colspan=\"" + str(
            len(player_names) + 1
        ) + "\" style=\"background-color: " + race_groups[current_group] + ";"
        if race_groups[current_group] in ["White", "Yellow"]:
            outputHTML += " color: black;"
        outputHTML += "\">" + race_groups[current_group] + "</td>\n</tr>\n"
    outputHTML += "<tr>\n<td>" + key + "</td>\n"
    for p in players.keys():
        outputHTML += "<td class=\""
        if p in data[key].keys():
            players[p]["medals"] += data[key][p]["medals"]
            if data[key][p]["time"] == data[key]["fastest_time"]:
                outputHTML += "record"
                players[p]["records"] += 1
                afont = "class=\"fontRecord\" "
            else:
                afont = ""
            outputHTML += p + "\"><a " + afont + "href=\"" + data[key][p][
                "url"] + "\">" + milliseconds_to_string(
                    data[key][p]["time"]) + "</a>"
            if data[key][p]["medals"] > 0:
                outputHTML += "&nbsp;<img src=\"" + image_url + medal_names[
                    data[key][p]["medals"] - 1] + ".png\" />"
            outputHTML += "</td>\n"
        else:
            outputHTML += "{}\"></td>\n".format(p)

    outputHTML += "</tr>\n"
outputHTML += "<tr>\n<td colspan=\"" + str(len(player_names) +
                                           1) + "\">&nbsp;</td>\n</tr>\n"

# Count medals and records
max_medals = 0
max_records = 0
for p in players.keys():
    max_medals = max(max_medals, players[p]["medals"])
    max_records = max(max_records, players[p]["records"])
titles = ["medals", "records"]
maxval = [max_medals, max_records]

for t, m in zip(titles, maxval):
    outputHTML += "<tr>\n<td class=\"fontRecord\">" + t.capitalize(
    )[:-1] + " count</td>\n"
    for p in players.keys():
        outputHTML += "<td class=\""
        if players[p][t] == m:
            outputHTML += "record"
        outputHTML += p + " boldCenter\">" + str(players[p][t]) + "</td>\n"
    outputHTML += "</tr>\n"

outputHTML += "</table>\n"
outputHTML += "</div>\n"
if standalone:
    outputHTML += "</body>\n"
    outputHTML += "</html>\n"

with open("trackmania.html", "w") as f:
    f.write(outputHTML)

# chartHTML = create_race_plots(players, data)
# with open("plot.html", "w") as f:
#     f.write(chartHTML)
