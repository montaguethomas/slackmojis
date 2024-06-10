#!/usr/bin/env python3
import functools, io, json, multiprocessing, os, requests, yaml
from PIL import Image


SLACKMOJIS_JSON_URL = "https://slackmojis.com/emojis.json"
STORAGE_DIR = "storage"
DOWNLOAD_DIR = "downloaded"
PACK_DIR = "packs"
SLACKMOJIS_JSON_FILE = "slackmojis.json"
PARALLELISM = multiprocessing.cpu_count() - 1


def create_dirs(dir):
  """Create directory and all intermediate-level directories"""
  if not os.path.isdir(dir):
    os.makedirs(dir)

def download_file(url, output_file):
  response = requests.get(url)
  with open(output_file, "wb") as f:
    f.write(response.content)
  return response

def write_yaml_file(data, output_file):
  with open(output_file, "w") as f:
    yaml.dump(data, f, default_flow_style=False)

def get_slackmojis(url, output_file):
  if os.path.isfile(output_file):
    with open(output_file, "r") as f:
      return json.load(f)

  print("fetching slackmojis ...")
  page=0
  slackmojis = []
  while True:
    print(f"... page {page}")
    response = requests.get(url + f"?page={page}")
    response.raise_for_status()
    emojis = response.json()
    if len(emojis) == 0:
        break
    slackmojis.extend(emojis)
    page = page + 1
  with open(output_file, "w") as f:
    json.dump(slackmojis, f)
  print("done.")
  return slackmojis

def get_categories(slackmojis):
  categories = set()
  categories.add("uncategorized")
  for slackmoji in slackmojis:
    if "category" in slackmoji:
      category = slackmoji["category"]["name"].lower().replace(" ", "-")
      categories.add(category)
  return categories

def valid_image(name, src):
  try:
    ext = os.path.splitext(src)[1]
    # the downloaded filename is different from if you download it manually
    # because of the possible duplicates
    dl_file = os.path.join(STORAGE_DIR, DOWNLOAD_DIR, f"{name}{ext}")
    if os.path.isfile(dl_file):
      with open(dl_file, "rb") as f:
        body = f.read()
    else:
      response = download_file(src, dl_file)
      body = response.content

    with io.BytesIO(body) as f:
      # Is it an image?
      im = Image.open(f)
      if im.width > 256 or im.height > 256:
        print(f":{name}: ({dl_file}) is {im.size}\t{src}")
        return False, None

    return True, dl_file
  except Exception as e:
    print(f":{name}: ({dl_file}) - unknown exception - {e}")
    return False, None


def process_slackmoji(slackmoji, name_count, packs):
  name = slackmoji["name"]
  print(f"... {name}")

  category = "uncategorized"
  if "category" in slackmoji:
    category = slackmoji["category"]["name"].lower().replace(" ", "-")

  # Special cases - a.k.a stupid cases
  if name == "yes2":
    # there are two "yes" and one "yes2" emojis already
    name = "yes2-1"
  if name == "no2":
    # there are two "no" and one "no2" emojis already
    name = "no2-1"
  sports = ["mlb", "nba", "nfl", "nhl"]
  if category in sports:
    # The NFL logo should not be :nfl-nfl:
    if name == "nfl":
      pass
    else:
      name = f"{category}-{name}"
  if "facebook" in category:
    name = f"fb-{name}"
  if "scrabble" in category:
    name = f"scrabble-{name}"

  name_count[name] = name_count[name] + 1 if name in name_count else 1
  if name_count[name] > 1:
    name = f"{name}{name_count[name]}"
  src = slackmoji["image_url"].split("?")[0]

  success, dl_file = valid_image(name, src)
  if not success:
    return

  packs[category]["emojis"].append({
    "name": name,
    "file": dl_file,
    "src": src,
  })


def main():
  slackmoji_pack_dir = os.path.join(STORAGE_DIR, PACK_DIR)
  create_dirs(slackmoji_pack_dir)
  create_dirs(os.path.join(STORAGE_DIR, DOWNLOAD_DIR))

  slackmojis = get_slackmojis(SLACKMOJIS_JSON_URL, os.path.join(STORAGE_DIR, SLACKMOJIS_JSON_FILE))
  categories = get_categories(slackmojis)

  with multiprocessing.Manager() as manager:
    # Initialize dicts
    name_count = manager.dict()
    packs = manager.dict()
    for category in categories:
      packs[category] = {
        "title": f"slackmoji-{category}",
        "emojis": manager.list(),
      }

    # Process slackmojis
    with multiprocessing.Pool(processes=PARALLELISM) as pool:
      print("processing slackmojis ...")
      _process_slackmoji = functools.partial(process_slackmoji, name_count=name_count, packs=packs)
      pool.map(_process_slackmoji, slackmojis)
      print("done")

    print("writing category files ...")
    for category in categories:
      print(f"... {category}")
      data = packs[category]
      data["emojis"] = list(data["emojis"])
      write_yaml_file(data, os.path.join(slackmoji_pack_dir, f"slackmojis-{category}.yaml"))
    print("done")


if __name__ == "__main__":
  main()
