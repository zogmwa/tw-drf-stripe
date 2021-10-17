from typing import Optional

from furl import furl


def get_embed_video_url(video_url: str) -> Optional[str]:
    """
    Consumes a regular or embed video url and returns an embed video url which is ready for rendering on the frontend.
    """
    if video_url is None:
        return video_url

    """ Takes a URL string for a video and converts it into an embeddeable video link """
    if '//' not in video_url:
        video_url = "https://{}".format(video_url)

    f = furl(video_url)

    if 'youtu.be' in f.netloc:
        # For youtu.be links the video id is in the path
        embed_url = 'https://www.youtube.com/embed' + str(f.path)
    elif 'youtube.com' in f.netloc and not str(f.path).startswith('/embed'):
        vid = f.args['v']
        embed_url = 'https://www.youtube.com/embed/{}'.format(vid)
    elif "vimeo.com" in f.netloc and not str(f.path).startswith('/video'):
        # Vimeo also keeps video id in the path
        embed_url = 'https://player.vimeo.com/video' + str(f.path)
    else:
        # If the scheme was http then override it with https
        f.scheme = 'https'
        embed_url = f.url

    return embed_url
