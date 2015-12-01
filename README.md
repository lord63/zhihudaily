# ZhihuDaily

Yet another web application for Zhihu daily which is powered by Flask.

## Features

* has several UIs, including text UI, image UI, pages UI and three columns UI

## QuickStart

clone the source code:

    $ git clone git@github.com:lord63/zhihudaily.git

set up the development environment, virtualenv is recommended:

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

init the database(default is fetching last 10 days news, you can also specify
the number of days by -n):

    $ python fetch_data.py init

run the zhihudaily:

    $ python run.py runserver

open your browser and have a look.

## Contribute

* It sucks? Why not help me improve it? Let me know the bad things.
* Want a new feature? Feel free to file an issue for a feature request.
* Find a bug? Open an issue please, or it's better if you can send me a pull request.

Contributions are always welcome at any time! :sparkles: :cake: :sparkles:

## License

MIT.
