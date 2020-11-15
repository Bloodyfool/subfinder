#!/usr/bin/env pipenv-shebang

import sys
import requests
import time
import re
import os
import mechanicalsoup

browser = mechanicalsoup.StatefulBrowser()

def get_next_url(url):
    browser.open(url)
    return "https://subscene.com" + browser.get_current_page().find("div", {"class": "download"}).find('a')["href"]

def set_language(langs = ['13']):
    langmap = {
            "Arabic"                : "2"  ,
            "Brazillian Portuguese" : "4"  ,
            "Danish"                : "10" ,
            "Dutch"                 : "11" ,
            "English"               : "13" ,
            "Farsi/Persian"         : "46" ,
            "Finnish"               : "17" ,
            "French"                : "18" ,
            "German"                : "19" ,
            "Greek"                 : "21" ,
            "Hebrew"                : "22" ,
            "Indonesian"            : "44" ,
            "Italian"               : "26" ,
            "Korean"                : "28" ,
            "Malay"                 : "50" ,
            "Norwegian"             : "30" ,
            "Portuguese"            : "32" ,
            "Romanian"              : "33" ,
            "Spanish"               : "38" ,
            "Swedish"               : "39" ,
            "Turkish"               : "41" ,
            "Vietnamese"            : "45" ,
            "Albanian"              : "1"  ,
            "Armenian"              : "73" ,
            "Azerbaijani"           : "55" ,
            "Basque"                : "74" ,
            "Belarusian"            : "68" ,
            "Bengali"               : "54" ,
            "Big 5 code"            : "3"  ,
            "Bosnian"               : "60" ,
            "Bulgarian"             : "5"  ,
            "Bulgarian/ English"    : "6"  ,
            "Burmese"               : "61" ,
            "Cambodian/Khmer"       : "79" ,
            "Catalan"               : "49" ,
            "Chinese BG code"       : "7"  ,
            "Croatian"              : "8"  ,
            "Czech"                 : "9"  ,
            "Dutch/ English"        : "12" ,
            "English/ German"       : "15" ,
            "Esperanto"             : "47" ,
            "Estonian"              : "16" ,
            "Georgian"              : "62" ,
            "Greenlandic"           : "57" ,
            "Hindi"                 : "51" ,
            "Hungarian"             : "23" ,
            "Hungarian/ English"    : "24" ,
            "Icelandic"             : "25" ,
            "Japanese"              : "27" ,
            "Kannada"               : "78" ,
            "Kurdish"               : "52" ,
            "Latvian"               : "29" ,
            "Lithuanian"            : "43" ,
            "Macedonian"            : "48" ,
            "Malayalam"             : "64" ,
            "Manipuri"              : "65" ,
            "Mongolian"             : "72" ,
            "Nepali"                : "80" ,
            "Pashto"                : "67" ,
            "Polish"                : "31" ,
            "Punjabi"               : "66" ,
            "Russian"               : "34" ,
            "Serbian"               : "35" ,
            "Sinhala"               : "58" ,
            "Slovak"                : "36" ,
            "Slovenian"             : "37" ,
            "Somali"                : "70" ,
            "Sundanese"             : "76" ,
            "Swahili"               : "75" ,
            "Tagalog"               : "53" ,
            "Tamil"                 : "59" ,
            "Telugu"                : "63" ,
            "Thai"                  : "40" ,
            "Ukrainian"             : "56" ,
            "Urdu"                  : "42" ,
            "Yoruba"                : "71" ,
            }

    cookie_obj = requests.cookies.create_cookie(name='LanguageFilter', value=','.join(langs), domain='subscene.com')
    browser.session.cookies.set_cookie(cookie_obj)

def get_num():
    try:
        return int(input('Enter a number: '))
    except KeyboardInterrupt:
        sys.exit()
    except:
        return None

def get_numrange(numberstring):
    nums = []
    for num in [x for x in numberstring.split(" ") if x]:
        tmp = num.split("-")
        if len(tmp) == 1:
            try:
                nums.append(int(tmp[0].strip()))
                continue
            except:
                print("invalid selection")
                return None
        elif len(tmp) == 2:
            try:
                l = int(tmp[0].strip())
                r = int(tmp[1].strip())
                nums += list(range(l, r+1))
            except:
                print("invalid selection")
                return None

        else:
            print("invalid selection")
            return None

    return nums

def norm(name):
    return name.replace(' ', '.').lower()

def extract_medium(name):
    """
    option 1: split on year and get 2nd after
    option 2: split on resolution and get 1nd after
    option 3: check for all types if it is in the name (best i think)
    """

    mediums = ["blu-ray", "bluray", "bluray", "bdrip", "brip", "brrip", "bdmv",
            "bdr", "bd25", "bd50", "bd5", "bd9", "hc", "hd-rip", "web-cap",
            "webcap", "webrip", "web-rip", "web", "webdl", "web-dl", "hdrip",
            "web-dlrip", "vodrip", "vodr", "dsr", "dsrip", "satrip", "dthrip",
            "dvbrip", "hdtv", "pdtv", "dtvrip", "tvrip", "hdtvrip", "dvdr",
            "dvd-full", "full-rip", "dvd-5", "dvd-9", "dvdrip", "dvdmux", "r5",
            "ddc", "scr", "screener", "dvdscr", "dvdscreener", "bdscr", "ppv",
            "ppvrip", "tc", "hdtc", "telecine", "wp", "workprint", "ts", "hdts",
            "telesync", "pdvd", "predvdrip", "cam-rip", "cam", "hdcam"]

    for medium in mediums:
        if medium in name:
            return medium
    return None

def extract_group(name):
    return re.split("[._-]", name)[-1]

"Top level functions"

def get_file_info(args): # main step 1 - or arg
    """
    looks in current dir for video files and returns filename, asking the user
    if there are multiple options
    """

    video_extentions = [ "webm", "mkv", "flv", "flv", "vob", "ogv", "ogg",
            "drc", "gif", "gifv", "mng", "avi", "MTS", "M2TS", "TS", "mov",
            "qt", "wmv", "yuv", "rm", "rmvb", "viv", "asf", "amv", "mp4", "m4p",
            "m4v", "mpg", "mp2", "mpeg", "mpe", "mpv", "mpg", "mpeg", "m2v",
            "m4v", "svi", "3gp", "3g2", "mxf", "roq", "nsv", "flv", "f4v",
            "f4p", "f4a", "f4b"]

    if len(args) > 1:
        print(f"sub takes 1 optional arg: a filename or seachname")
        exit()
    if len(args) == 1:
        arg = args[0][2:] if args[0].startswith("./") else args[0] # remove optional leading ./
        return arg

    # list all videos in current dir
    video_files = []
    for file_name in os.listdir():
        extention = file_name.rsplit(".", 1)[-1]
        if extention in video_extentions:
            video_files.append(file_name)

    # if there is only 1 video in the dir, use that. Else ask the user which to use
    if len(video_files) == 1:
        return video_files[0]
    else:
        while True:
            print("What file do you want to search for: ")
            for a, b in enumerate(video_files, 1):
                print(f"{a:2} {b}")
            if (index := get_num()) != None:
                if index <= len(video_files):
                    return video_files[index-1]
                else:
                    print(f"{index} not a valid option")

def find_movie_info(video_name): # main step 2
    """
    Tries to find a movie in subscene based on the filename, asks the user if
    unsure
    """
    # get page
    browser.open("https://subscene.com/")
    form = browser.select_form()
    form["query"] = video_name
    browser.submit_selected()

    # parse options
    def parse(tag):
        return {
                "name": tag.find("a").text.rsplit(" ", 1)[0],
                "full_name": tag.find("a").text,
                "year":  tag.find("a").text.rsplit(" ", 1)[-1][1:5],
                "url":   "https://subscene.com" + tag.find("a")["href"],
                "count": int(tag.find("div", {"class": "count"}).text.strip().split(" ")[0]),
                }
    options = browser.get_current_page().find("div", {"class": "search-result"}).find_all("li")
    parsed = [ parse(movie) for movie in options ]

    # filter
    filtered  = [ movie for movie in parsed
            if movie["year"] in video_name and
            movie["count"] > 20]
    if not filtered:
        filtered  = [ movie for movie in parsed
                if movie["year"] in video_name
                ]
    if not filtered:
        filtered  = parsed

    # select
    if len(filtered) == 1:
        return filtered[0]
    else:
        while True:
            print("Cannot infer movie, please specify:")
            for a, b in enumerate(filtered, 1):
                print(f"{a:2} {b['full_name']}")
            if (index := get_num()) != None:
                if index <= len(filtered):
                    return filtered[index-1]
                else:
                    print(f"{index} not a valid option")

def get_all_subtitles(movie_link): # main step 3
    "Get all subtitles from a movie link "
    # get page
    browser.open(movie_link)

    # parse options
    def parse(url_language_name, notes):
        name = url_language_name.find('a').find_all('span')[1].text.strip()
        norm_name = norm(name)
        return {
                "url": "https://subscene.com" + url_language_name.find('a')['href'],
                "language": url_language_name.find('a').find_all('span')[0].text.strip(),
                "name": name,
                "normalised_name": norm_name,
                "notes": notes.find('div').text.strip(),
                "medium": extract_medium(norm_name),
                "group": extract_group(norm_name),
                }
    rows = browser.get_current_page().find("tbody").find_all("tr")[1:]
    parsed = [ parse(cells[0], cells[4]) for row in rows if len(cells := row.find_all('td')) == 5]
    return parsed

def order_subs_by_match(subtitles, video_name, movie): # main step 4
    """
    Orders subs by my heuristic:
    1. Full name matches are the best
    2. Next is if the release type and release group BOTH match
    3. Next is if the release type only matches
    4. Next is if the release group only matches
    5. Finally the rest
    """

    vname  = norm(video_name)
    medium = extract_medium(vname)
    group  = extract_medium(vname)

    best  = []
    next1 = []
    next2 = []
    next3 = [] # for order
    rest  = []
    for sub in subtitles:
        # full match
        if sub['normalised_name'] in vname:
            best.append(sub)
            continue

        mmatch = sub['medium'] == medium
        gmatch = sub['group'] == group

        # Source medium matches AND group matches
        if mmatch and gmatch:
            next1.append(sub)
            continue

        # Only medium matches
        if mmatch:
            next2.append(sub)
            continue

        # Only group matches
        if gmatch:
            next3.append(sub)
            continue

        rest.append(sub)

    return best + next1 + next2 + next3 + rest


    return ans

def choose_and_download_subs(subtitles): # main step 5
    "Takes a list of subs, asks the user which to download, and downloads them"
    # print first 10
    print("The 10 best matches are:")
    for a, b in enumerate(subtitles[:10], 1):
        print(f"{a:2} {b['name']}")
        print(f"    {b['notes']}")

    to_download = []

    # ask how many (default 1-5)
    while True:

        if (indeces := get_numrange(input(f'Enter subs to download (max {len(subtitles)+1}) Default: [1-5]: ') or "1-5")) != None:
            print("Getting: " + ", ".join([str(i) for i in indeces]))
            for index in indeces:
                if index <= len(subtitles):
                    to_download.append(subtitles[index-1])
                else:
                    break
            break

    for index, sub in zip(indeces, to_download):
        new_url = get_next_url(sub['url'])
        new_name = f"{index}_{sub['name']}.srt"
        os.system(f"mkdir -p .{index}_tmp")
        os.system(f"""(
        echo {index} &&
        wget -q -O .{index}_tmp/sub_just_downloaded_for_you.zip {new_url} &&
        unzip -q -o .{index}_tmp/sub_just_downloaded_for_you.zip -d .{index}_tmp &&
        mv .{index}_tmp/*.srt {new_name} &&
        rm -r .{index}_tmp &&
        echo Downloaded: {new_name}
        ) & disown""")
    time.sleep(3) # should be enough to keep the terminal pretty most of the time

def main(args):
    video_name = get_file_info(args) # step 1
    print(f"Finding subtitles for: \"{video_name}\"")

    movie_info = find_movie_info(video_name) # step 2
    print(f"Scanning {movie_info['count']} subtitles for \"{movie_info['full_name']}\"")

    set_language(['13']) # english

    subtitles  = get_all_subtitles(movie_info["url"]) # step 3

    ordered_subtitles  = order_subs_by_match(subtitles, video_name, movie_info) # step 4

    choose_and_download_subs(ordered_subtitles) # step 5

if __name__ == "__main__":
    try:
        exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit()
