from urllib.parse import urlparse

def is_valid_instagram_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.netloc not in ("www.instagram.com", "instagram.com"):
        return False
    
    path = parsed.path.rstrip("/")

    return (
        path.startswith("/p/")
        or path.startswith("/reel/")
        or path.startswith("/tv/")
    )

def is_valid_youtube_url(url: str) -> bool:
    parsed = urlparse(url)

    return parsed.netloc in (
        "www.youtube.com",
        "youtube.com",
        "youtu.be",
    )
def is_valid_reddit_url(url: str) -> bool:
    parsed = urlparse(url)

    return parsed.netloc in (
        "www.reddit.com",
        "reddit.com",
        "old.reddit.com",
        "m.reddit.com",
    )