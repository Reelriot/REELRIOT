# reddit_scraper.py – descarga 1 vídeo top del día
import os, random, pathlib, requests, praw

DL = pathlib.Path("downloads"); DL.mkdir(exist_ok=True)

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent="reelriot/0.1 by u/"+os.getenv("REDDIT_USER")
)

SUBS = "Unexpected+PublicFreakout+reels+TikTokCringe+videos"
posts = list(reddit.subreddit(SUBS).top(time_filter="day", limit=10))
random.shuffle(posts)

for post in posts:
    if not post.is_video:
        continue
    url = post.media["reddit_video"]["fallback_url"]
    target = DL / f"{post.id}.mp4"
    print("Descargando", url)
    vid = requests.get(url, timeout=30).content
    target.write_bytes(vid)
    print("Guardado →", target)
    break
