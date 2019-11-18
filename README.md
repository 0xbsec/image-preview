## Image Preview

<img src="screenshots/app.png" />

Menu bar app that shows random images from a source folder of your choice.

More information in this blog post [this blog post](http://mhasbini.com/blog/introducing-image-preview-app.html).

## Screenshots

![Screenshot 1](screenshots/1.png)
![Screenshot 2](screenshots/2.png)

## Development

- Install requirements: `pip3 install -r requirements.txt`.
- Package:
  - `fbs freeze`
  - `fbs installer`
- Run tests: `python3 -m unittest discover -s src/main/python/ -p 'test_*.py'`
- Run linter: `black src/main/python/`