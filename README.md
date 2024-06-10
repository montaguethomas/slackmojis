# Slackmojis

Downloads emojis from [slackmojis.com](https://slackmojis.com) and generates "packs" by
category. Allows uploading of emojis to Slack as a normal Slack user with permissions
to add emojis.

## Usage

### Download

```
mkdir slackmojis
cd slackmojis
docker run --rm -it -v $PWD:/app/storage ghcr.io/montaguethomas/slackmojis:latest download.py
```

### Upload

```
cd slackmojis
docker run --rm -it -v $PWD:/app/storage ghcr.io/montaguethomas/slackmojis:latest upload.py
```

## ToDo

- Add support for `upload.py` to use slackmoji packs.

## References

- https://github.com/lambtron/emojipacks
- https://github.com/smashwilson/slack-emojinator
