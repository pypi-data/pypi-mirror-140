# nptel-dl
Download courses from NPTEL

### Installation
`pip install nptel-dl`

#### Manual
```
    git clone https://github.com/deshdeepak1/nptel-dl
    cd nptel-dl
    python3 -m venv venv
    pip3 install -r requirements.txt
```

#### Usage
```
usage: nptel-dl [-h] [--dump-json  | --dump-single-json ] [--write-json] [--all] [--books] [--videos] [--syllabus] [--transcripts]
                   [--assignements]
                   URL [URL ...]

Download NPTEL courses

positional arguments:
  URL                   URLs or COURSE_IDs

optional arguments:
  -h, --help            show this help message and exit
  --dump-json , -j      Dump info dict of urls in json. Available options: all, modules, yt, direct, assignements, transcripts, books
  --dump-single-json , -J 
                        Dump info dict of urls in single json. Available options: all, modules, yt, direct, assignements, transcripts, books
  --write-json, -w      Write json. Requires either --dump-json or --dump-single-json
  --all, -A             Download all i.e. videos, syllabus, transcripts, assignements, books.
  --books, -b           Download books
  --videos, -v          Download videos
  --syllabus, -s        Download syllabus
  --transcripts, -t     Download transcripts
  --assignements, -a    Download assignements
```
