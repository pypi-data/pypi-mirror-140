from __future__ import annotations
import argparse
import json
import os
import sys
import requests
import gdown
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup


WEBSITE = "https://nptel.ac.in"
ARCHIVE_WEBSITE = "https://archive.nptel.ac.in"
YOUTUBE = "https://youtube.com/watch?v="

DOWNLOAD_SUCCESS_MSG = "Download successfull: {}"
DOWNLOADING_MSG = "Downloading {}: {}"
INVALID_URL_MSG = "ERROR: {} is not a valid url"
MESSAGES = [
    DOWNLOAD_SUCCESS_MSG,
    INVALID_URL_MSG,
    DOWNLOADING_MSG
]


def print_message(status: int, messages: list[str]):
    """
    Print message from message list depending on status.
    """
    print(MESSAGES[status].format(*messages))


def write_json(dict_: dict, filename: str):
    with open(filename, "w") as f:
        f.write(json.dumps(dict_, indent=4))


def get_dict(dict_: dict, dict_name: str):
    """
    Return Dict value for a key or entire dict if key=all 
    """
    if dict_name == "all":
        return dict_
    else:
        return dict_[dict_name]


def get_course_data(input_url: str):
    """
    Get course_id, course_url and webpage of course from course_id or url
    """
    if input_url.isnumeric():
        url = f"{ARCHIVE_WEBSITE}/courses/{input_url}"
    else:
        url = input_url

    if "nptel.ac.in" not in url:
        return

    try:
        course_res = requests.get(url)
    except:
        return
    else:
        if course_res.status_code >= 400:
            return
        url = course_res.url
        course_id = url.split("/")[-2]
        return course_id, url, course_res.text


def get_course_dict(course_data: tuple[str, str, str]):
    """
    Get all course info in a dictionary.

    Takes a tuple of course_id, course_url, webpage text as parameter.
    """
    course_id, course_url, webpage = course_data
    soup = BeautifulSoup(webpage, "lxml")

    course_title = soup.title.get_text().strip()

    outer_div = soup.body.select_one("div.container")
    header_div = outer_div.find_next("div")
    course_div = header_div.find_next("div")

    infos = header_div.find_all("a")
    discipline = infos[1].get_text().strip()
    subject_title = infos[2].get_text().strip()
    syllabus_pdf = infos[3].get("href")
    syllabus_pdf = f"{ARCHIVE_WEBSITE}{syllabus_pdf}" if syllabus_pdf else ""
    institute = infos[4].span.get_text().strip()
    course_date = infos[5].span.get_text().strip()

    course_div: BeautifulSoup
    modules = course_div.select("div#div_lm>ul>li")

    course_dict = {
        "course_id": course_id,
        "course_url": course_url,
        "course_title": course_title,
        "discipline": discipline,
        "institute": institute,
        "course_date": course_date,
        "syllabus": syllabus_pdf,
        "modules": [],
        "yt": {},
        "direct": {},
    }

    assignements = course_div.select("div#tab3>table>tbody>tr>td>a")
    assignements_links = {}
    for assignement in assignements:
        assignement_title = assignement.get_text().strip()
        assignements_link = assignement.get("href")
        assignements_links[assignement_title] = assignements_link

    transcripts = course_div.select("table#request1>tbody>tr")
    transcripts_links = {}
    for transcript in transcripts:
        transcript_title = transcript.find_next("td").find_next("td").get_text().strip()
        try:
            transcript_link = transcript.select_one("a").get("href")
        except:
            transcript_link = ""
        transcripts_links[transcript_title] = transcript_link
    books = course_div.select("div#download_books>table>tbody>tr")
    books_links = {}
    for book in books:
        book_title = book.find_next("td").find_next("td").get_text().strip()
        try:
            book_link = book.select_one("a").get("href")
        except:
            continue
        books_links[book_title] = book_link

    course_dict.update(
        {
            "assignements": assignements_links,
            "transcripts": transcripts_links,
            "books": books_links,
        }
    )

    for module in modules:
        module_tag = module.a
        module_title = module_tag.get_text().strip()
        videos_list = []
        yt = {}
        direct = {}
        if module.get("id"):
            video_tag = module_tag
            video_title = video_tag.get_text().strip()
            video = video_tag.get("onclick")[17:]
            video_id, yt_video_id, direct_video_link = eval(video)
            yt_video_link = f"{YOUTUBE}{yt_video_id}" if yt_video_id else ""
            direct_video_link = f"{ARCHIVE_WEBSITE}{direct_video_link}" if direct_video_link else yt_video_link
            videos_dict = {
                "video_id": video_id,
                "video_title": video_title,
                "yt_video_link": yt_video_link,
                "direct_video_link": direct_video_link,
                "transcript": "",
            }
            videos_list.append(videos_dict)
            yt[video_title] = yt_video_link
            direct[video_title] = direct_video_link
        else:
            videos = module.select("ul>li")
            for v in videos:
                video_tag = v.a
                video_title = video_tag.get_text().strip()
                video = video_tag.get("onclick")[17:]
                video_id, yt_video_id, direct_video_link = eval(video)
                yt_video_link = f"{YOUTUBE}{yt_video_id}" if yt_video_id else ""
                direct_video_link = f"{ARCHIVE_WEBSITE}{direct_video_link}" if direct_video_link else yt_video_link
                videos_dict = {
                    "video_id": video_id,
                    "video_title": video_title,
                    "yt_video_link": yt_video_link,
                    "direct_video_link": direct_video_link,
                    "transcript": list(transcripts_links.values())[video_id - 1],
                }
                videos_list.append(videos_dict)
                yt[video_title] = yt_video_link
                direct[video_title] = direct_video_link

        module_dict = {
            "module_title": module_title,
            "videos": videos_list,
        }
        course_dict["modules"].append(module_dict)
        course_dict["yt"][module_title] = yt
        course_dict["direct"][module_title] = direct

    return course_dict


def get_courses(input_urls: list[str]):
    """
    Return course_dict of list of courses
    """
    courses = []
    for input_url in input_urls:
        course_data = get_course_data(input_url)
        course_dict = {}
        if course_data:
            course_dict = get_course_dict(course_data)
        courses.append((input_url, course_dict))
    return courses


def dump_jsons(input_urls: list[str], dict_name: str, single: bool):
    """
    Dump course info to stdout
    """
    courses = get_courses(input_urls)
    single_output_dict = {}
    for input_url, course_dict in courses:
        if not course_dict:
            print_message(1, [input_url])
            continue
        output_dict = get_dict(course_dict, dict_name)
        if not single:
            print(json.dumps(output_dict, indent=4))
        else:
            single_output_dict[course_dict["course_id"]] = output_dict
    if single:
        print(json.dumps(single_output_dict, indent=4))


def write_jsons(input_urls: list[str], dict_name: str, single: bool):
    """
    Download info of course in json file
    """
    courses = get_courses(input_urls)
    single_output_dict = {}
    course_ids = []
    for input_url, course_dict in courses:
        if not course_dict:
            print_message(1, [ input_url ])
            continue
        course_id = course_dict["course_id"]
        output_dict = get_dict(course_dict, dict_name)
        if not single:
            filename = f"{course_id}. {course_dict['course_title']} - {dict_name}.json"
            write_json(output_dict, filename)
        else:
            course_ids.append(course_id)
            single_output_dict[course_id] = output_dict
    if single:
        filename = f"{', '.join(course_ids)} - {dict_name}.json"
        write_json(single_output_dict, filename)


def ytdl_download(link: str, ytdl_opts: dict):
    """
    Download link using yt-dlp
    """
    if not link:
        return
    link = link.replace(WEBSITE, ARCHIVE_WEBSITE)
    with YoutubeDL(ytdl_opts) as ytdl:
        ytdl.download(link)


def drive_download(link: str, file_path: str="", filename: str=""):
    """
    Download google drive links
    """
    if not link:
        return
    link = link.replace(WEBSITE, ARCHIVE_WEBSITE)
    os.makedirs(file_path, exist_ok=True)
    output = f"{file_path}/{filename}" if filename else f"{file_path}/"
    gdown.download(link, output, fuzzy=True)


def download_course(input_url: str, opts: dict) -> int:
    """
    Download course from url or course id
    """
    course_data = get_course_data(input_url)
    required_list = opts["required"]
    if course_data is None:
        return 1
    course_dict = get_course_dict(course_data)
    course_id = course_dict["course_id"]
    course_title = course_dict["course_title"]
    course_dir = f"{course_id}. {course_title}"
    ytdl_opts = {}
    for required in required_list:
        if required == "all":
            ytdl_opts["outtmpl"] = f"{course_dir}/syllabus.pdf"
            syllabus = get_dict(course_dict, "syllabus")
            print_message(2, ["syllabus", syllabus])
            ytdl_download(syllabus, ytdl_opts)
            for required_ in ["books", "assignements"]:
                required_dict = get_dict(course_dict, required_)
                for name, link in required_dict.items():
                    print_message(2, [name, link])
                    ytdl_opts["outtmpl"] = f"{course_dir}/{required_}/{name}.pdf"
                    ytdl_download(link, ytdl_opts)
            modules = get_dict(course_dict, "modules")
            for module in modules:
                module_title, videos = module.values()
                for video in videos:
                    video_id, video_title, yt_video_link, direct_video_link, transcript_link = video.values()
                    filename = f"{video_id}. {video_title}.%(ext)s"
                    ytdl_opts["outtmpl"] = f"{course_dir}/{module_title}/{filename}"
                    print_message(2, [filename, direct_video_link])
                    ytdl_download(direct_video_link, ytdl_opts)
                    filename = f"{video_id}. {video_title}.pdf"
                    file_path = f"{course_dir}/{module_title}"
                    print_message(2, [filename, transcript_link])
                    drive_download(transcript_link, file_path, filename)
                    
        if required == "syllabus":
            ytdl_opts["outtmpl"] = f"{course_dir}/syllabus.pdf"
            syllabus = get_dict(course_dict, "syllabus")
            print_message(2, ["syllabus", syllabus])
            ytdl_download(syllabus, ytdl_opts)
        if required in ["books", "transcripts", "assignements"]:
            required_dict = get_dict(course_dict, required)
            for name, link in required_dict.items():
                file_path = f"{course_dir}/{required}"
                filename = f"{name}.pdf" 
                print_message(2, [filename, link])
                if "drive.google.com" in link:
                    drive_download(link, file_path, filename)
                    continue
                ytdl_opts["outtmpl"] = f"{file_path}/{filename}"
                ytdl_download(link, ytdl_opts)
    return 0


def download_courses(input_urls: list[str], opts: dict):
    """
    Download multiple courses from urls or course ids
    """
    for input_url in input_urls:
        download_status = download_course(input_url, opts)
        print_message(download_status, [ input_url ])


def main():
    """
    Run from command line
    """
    dict_names = [
        "all",
        "modules",
        "yt",
        "direct",
        "assignements",
        "transcripts",
        "books",
    ]
    required_names = ["videos", "syllabus", "transcripts", "assignements", "books"]
    choices_str = f"Available options: {', '.join(dict_names)}"
    parser = argparse.ArgumentParser(
        description="Download NPTEL courses", allow_abbrev=True
    )
    parser.add_argument("URL", nargs="+", help="URLs or COURSE_IDs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dump-json",
        "-j",
        dest="dict_name",
        help="Dump info dict of urls in json. " + choices_str,
        metavar="",
        choices=dict_names,
    )
    group.add_argument(
        "--dump-single-json",
        "-J",
        dest="dict_name_single",
        help="Dump info dict of urls in single json. " + choices_str,
        metavar="",
        choices=dict_names,
    )
    parser.add_argument(
        "--write-json",
        "-w",
        help="Write json. Requires either --dump-json or --dump-single-json",
        action="store_true",
    )
    parser.add_argument(
        "--all",
        "-A",
        action="store_true",
        help=f"Download all i.e. {', '.join(required_names)}.",
    )
    parser.add_argument("--books", "-b", action="store_true", help="Download books")
    parser.add_argument("--videos", "-v", action="store_true", help="Download videos")
    parser.add_argument(
        "--syllabus", "-s", action="store_true", help="Download syllabus"
    )
    parser.add_argument(
        "--transcripts", "-t", action="store_true", help="Download transcripts"
    )
    parser.add_argument(
        "--assignements", "-a", action="store_true", help="Download assignements"
    )
    args = parser.parse_args()
    input_urls = args.URL
    if args.write_json:
        if not args.dict_name and not args.dict_name_single:
            parser.error(
                "--write/-w requires either of --dump-json or --dump-single-json"
            )
        if args.dict_name:
            write_jsons(input_urls, args.dict_name, False)
        if args.dict_name_single:
            write_jsons(input_urls, args.dict_name_single, True)
        return
    if args.dict_name:
        dump_jsons(input_urls, args.dict_name, False)
        return
    if args.dict_name_single:
        dump_jsons(input_urls, args.dict_name_single, True)
        return
    required_list = []
    if args.all:
        download_courses(input_urls, {"required": ["all"]})
        return
    if args.videos:
        required_list.append("videos")
    if args.assignements:
        required_list.append("assignements")
    if args.books:
        required_list.append("books")
    if args.transcripts:
        required_list.append("transcripts")
    if args.syllabus:
        required_list.append("syllabus")

    download_courses(input_urls, {"required": required_list})


if __name__ == "__main__":
    main()
