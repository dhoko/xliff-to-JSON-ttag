# Convert XLIFF to ttag JSON (compact format)

Based on https://ttag.js.org/ 


## requirements

- python 3.x (3.9 _during this dev_)
- `lxml`
- `pipenv` _optional_

## CLI

```sh
usage: convert.py [-h] --input INPUT --output OUTPUT --locale LOCALE

convert xliff to ttag JSON (compact)

optional arguments:
  -h, --help       show this help message and exit
  --input INPUT    input xliff file
  --output OUTPUT  output JSON file
  --locale LOCALE  locale from crowdin you're using
```

ex: `$ python convert.py --input demo/webapp.xliff --output monique.json --locale fr`

> for `[--locale]` you can open the file `lib/config/gettext-plurals.json` to see all the options you have

## How to get the xliff from crowdin?

You need to download the translations from the download button here when you open your language.

![download](https://user-images.githubusercontent.com/713283/235617439-b80a1642-dfa5-40c7-a7ec-eb190e014ca1.jpg)

> :warning: Do not pick the 2 options _export xxx xliff_ as crowdin has an issue and breaks the plurals inside these files.
