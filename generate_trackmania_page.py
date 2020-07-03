import numpy as np
import requests
import re
import datetime
import hashlib


def string_to_milliseconds(string):
    elems = re.split("h|'|\"", string)
    milliseconds = float(elems[-1]) * 10.0 + float(elems[-2]) * 1000.0 + float(elems[-3]) * 60000.0
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
    custom_tracks = ["F01-Race.Gbx", "F03-Obstacle.Gbx", "F05-Endurance.Gbx",
                     "F07-Race.Gbx", "F09-Speed.Gbx", "F11-Race.Gbx",
                     "F13-Race.Gbx", "F15-Endurance.Gbx"]
    medal_names = ["bronze", "silver", "gold", "authortime"]
    # ctracks = dict()
    # medals = ["br
    for t in custom_tracks:
        content = requests.get(url+t).text
        key = t.replace(".Gbx", "")
        data[key] = {}
        for med in medal_names:
            # print(med + '"=(.*)"')
            searchObj = re.search(med + '=\"(.*)\"', content)
            if searchObj:
                time = float(searchObj.group(1).split()[0].replace('"',""))
                if med == "authortime":
                    name = "author"
                else:
                    name = med
                data[key][name] = time
        print("-", key, ":", data[key])

        # searchObj = re.search("<td>[A-E][0-1][0-9]-(.*)", t)
        # if searchObj:
        #     line = t.split("<td>")
        #     name = re.sub("</?td>", "", searchObj.group().replace("\r", ""))
        #     ctracks[name] = dict()
        #     for i, n in enumerate(medal_names):
        #         raw_time = line[5 + i].split("<")[0]
        #         ctracks[name][n] = string_to_milliseconds(raw_time)
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

# def make_ghost_file_name(url="https://sites.google.com/site/trackmaniachampionnat/archive/", key="", player="", suffix=".gbx"):
#     return "{}{}-{}{}".format(url, key, player, suffix)

def make_ghost_file_name(key="", player="", suffix=".gbx", url=""):
    return "{}{}-{}{}".format(url, key, player, suffix)



def extract_time_from_file(file_url):
    time = None
    try:
        content = requests.get(file_url).text
        searchObj = re.search("best=(.*) ", content)
        if searchObj:
            time = float(searchObj.group(1).split()[0].replace('"',""))
    except ConnectionError:
        pass
    return time


def get_player_times(players, data, medal_names, base_url):
    for p in players.keys():
        print("Getting times for player: {}".format(p))
        for key in data.keys():
            suffix = ".gbx"
            # ghost_url = make_ghost_file_name(key=key, player=p, suffix=suffix, url=base_url)
            time = extract_time_from_file(make_ghost_file_name(key=key, player=p, suffix=suffix, url=base_url))
            if time is None:
                suffix = ".Gbx"
                # ghost_url = make_ghost_file_name(key=key, player=p, suffix=suffix, url=base_url)
                time = extract_time_from_file(make_ghost_file_name(key=key, player=p, suffix=suffix, url=base_url))
            if time is not None:
                data[key][p] = dict()
                data[key][p]["time"] = time
                if data[key]["fastest_time"] is None:
                    data[key]["fastest_time"] = time
                else:
                    data[key]["fastest_time"] = min(data[key]["fastest_time"], time)
                nmedals = 0
                for n in medal_names:
                    if time < data[key][n]:
                        nmedals += 1
                data[key][p]["medals"] = nmedals
                data[key][p]["url"] = make_ghost_file_name(key=key, player=p, suffix=suffix)
                print("  - {} : {}".format(key, time))
    return

# def rgb_to_hex(rgb):
#     return '#%02x%02x%02x' % rgb


# def make_color(col, shift=None):
#     delta = 0.4
#     h = col.lstrip('#')
#     rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
#     if shift is not None:
#         rgb = (min(255, int((shift * delta + 1.0) * rgb[0])),
#                min(255, int((shift * delta + 1.0) * rgb[1])),
#                min(255, int((shift * delta + 1.0) * rgb[2])))
#     return rgb_to_hex(rgb)


def create_race_plots(players, data):

    archive = requests.get("https://sites.google.com/site/trackmaniachampionnat/archive").text.split("\n")

    for key in data.keys():
        for p in players.keys():
            name = make_ghost_file_name(url="", key=key, player=p)
            print(name)

            # Search for the Race-Player.gbx string in the archive source
            for i in range(len(archive)):
                if archive[i].find(name) >= 0:
                    # Get the source of the page listing the version dates
                    wuid = re.search("id=\"JOT_FILECAB_label_(.*)\" aria-hidden", archive[i])
                    # if wuid:
                    print(wuid.group(1))
                    # exit()
                    url = "https://sites.google.com/site/trackmaniachampionnat/system/app/pages/admin/revisions?wuid=" + wuid.group(1)
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
                    searchObj = re.search(">v\. (.*)  </td>", archive[i+3])
                    if searchObj:
                        nversions = int(searchObj.group(1))
                        # gather_versions()
                        # print(version)
                        # print(searchObj.group(1))
                        for n in range(nversions):
                            ghost_url = make_ghost_file_name(key=key, player=p, suffix=".gbx?revision={}".format(n+1))
                            time = extract_time_from_file(ghost_url)
                            # if time is not None:

                    break

            exit()

















#===============================================================================

standalone = False
fetch_new_ghosts = False
base_url = "https://sites.google.com/site/trackmaniachampionnat/archive/"


# Define players
player_names = ["Baptiste", "Neil", "Olivier", "Jacques", "Seb", "Baba", "Chris"]
# player_names = ["Baptiste"]

players = dict()
for p in player_names:
    players[p] = dict()
    players[p]["color"] = "#" + hashlib.md5(p.encode("utf-8")).hexdigest()[:6]
    players[p]["medals"] = 0
    players[p]["records"] = 0
    # print(players[p]["color"])

# record_color = "border: 2px solid #ff0000;"
# record_color = "#00ffff"
record_color = "#000000"


medal_names = ["bronze", "silver", "gold", "author"]
race_groups = {"A": "White", "B": "Green", "C": "Blue", "D": "Red", "E": "Black", "F": "Yellow"}

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
bckgrnd = "#4f4f4f";
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
# outputHTML += "tr {border:4px solid transparent;}\n"
# TR:hover TD { background:#BAFECB !important; }
for n, p in players.items():
    outputHTML += ".{} {{ background-color: {} }}\n".format(n, p["color"])
    outputHTML += ".record{} {{ background: radial-gradient({}, #000000); }}\n".format(n, p["color"])
outputHTML += ".fontRecord {font-weight: bold;}\n"
outputHTML += ".boldCenter {font-weight: bold; text-align: center;}\n"
outputHTML += "</style>\n"
if standalone:
    outputHTML += "</head>\n"
    outputHTML += "<body>\n"
# outputHTML += "<div style=\"background-color:{};\">".format(bckgrnd)
outputHTML += "<div>"
# outputHTML += "<table border=\"0\" style=\"border-spacing: 10px 1px; font-family: Courier New;\"><th style=\"background-color: {};\"></th>".format(bckgrnd)
outputHTML += "<table border=\"0\" style=\"border-spacing: 10px 1px; font-family: Courier New;\">\n<th></th>\n"
for p in players.keys():
    # outputHTML += "<th class=\"{}\" style=\"color: #000000;\">{}</th>".format(p, p);
    outputHTML += "<th class=\"{}\">{}</th>\n".format(p, p);
current_group = "Z"
for race_count, key in enumerate(data.keys()):
    if current_group != key[0]:
        current_group = key[0]
        # outputHTML += "<tr><td colspan=\"" + str(len(player_names) + 1) + "\" style=\"background-color: " + bckgrnd + ";\">&nbsp;</td></tr><tr style=\"background-color: " + race_groups[current_group] + ";\"><td colspan=\"" + str(len(player_names) + 1) + "\""
        outputHTML += "<tr>\n<td colspan=\"" + str(len(player_names) + 1) + "\">&nbsp;</td>\n</tr>\n<tr>\n<td colspan=\"" + str(len(player_names) + 1) + "\" style=\"background-color: " + race_groups[current_group] + ";"
        if race_groups[current_group] in ["White", "Yellow"]:
            outputHTML += " color: black;"
        outputHTML += "\">" + race_groups[current_group] + "</td>\n</tr>\n"
    outputHTML += "<tr>\n<td>" + key + "</td>\n"
    for p in players.keys():
        # bg_color = make_color(players[p]["color"])#, -1.0 * (race_count % 2 == 0))
        bg_color = players[p]["color"]#)#, -1.0 * (race_count % 2 == 0))
        outputHTML += "<td class=\""
        if p in data[key].keys():
            players[p]["medals"] += data[key][p]["medals"]
            # outputHTML += "<td style=\""# + bg_color
            # outputHTML += "<td class=\""# + bg_color
            if data[key][p]["time"] == data[key]["fastest_time"]:
                # outputHTML += "background: repeating-linear-gradient(45deg, " + bg_color + ", " + bg_color + " 10px, " + record_color + " 10px, " + record_color + " 20px);"
                # outputHTML += "background: radial-gradient(" + bg_color + ", #000000);"
                outputHTML += "record"
                # outputHTML += record_color
                players[p]["records"] += 1
                # afont = "style=\"font-weight: bold;\""
                afont = "class=\"fontRecord\" "
            else:
                # outputHTML += "background-color: " + bg_color + ";"
                afont = ""
            outputHTML += p + "\"><a " + afont + "href=\"" + data[key][p]["url"] + "\">" + milliseconds_to_string(data[key][p]["time"]) + "</a>"
            if data[key][p]["medals"] > 0:
                outputHTML += "&nbsp;<img src=\"" + image_url + medal_names[data[key][p]["medals"] - 1] + ".png\" />"
            outputHTML += "</td>\n"
        else:
            # outputHTML += "<td style=\"background-color: " + bg_color + ";\"></td>"
            outputHTML += "{}\"></td>\n".format(p)

    outputHTML += "</tr>\n"
# outputHTML += "<tr><td colspan=\"" + str(len(player_names) + 1) + "\" style=\"background-color: {};\">&nbsp;</td></tr>\n".format(bckgrnd)
outputHTML += "<tr>\n<td colspan=\"" + str(len(player_names) + 1) + "\">&nbsp;</td>\n</tr>\n"

# Count medals and records
max_medals = 0
max_records = 0
for p in players.keys():
    max_medals = max(max_medals, players[p]["medals"])
    max_records = max(max_records, players[p]["records"])

titles = ["medals", "records"]
maxval = [max_medals, max_records]

for t, m in zip(titles, maxval):
    # outputHTML += "<tr><td style=\"font-weight: bold;\">" + t.capitalize()[:-1] + " count</td>"
    outputHTML += "<tr>\n<td class=\"fontRecord\">" + t.capitalize()[:-1] + " count</td>\n"
    for p in players.keys():
        # outputHTML += "<td style=\"font-weight: bold; text-align: center; "
        outputHTML += "<td class=\""
        # bg_color = make_color(players[p]["color"])
        # bg_color = players[p]["color"]
        if players[p][t] == m:
            # outputHTML += "background: radial-gradient(" + bg_color + ", #000000)"
            outputHTML += "record"
        # else:
        #     outputHTML += "background-color: " + bg_color
        # outputHTML += p + "\" style=\"font-weight: bold; text-align: center;\">" + str(players[p][t]) + "</td>"
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
