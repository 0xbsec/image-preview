## Image Preview

Menu bar app that shows images from a source folder of your choice.

## Screenshots

![Screenshot 1](screenshots/1.png)
![Screenshot 2](screenshots/2.png)
![Screenshot 3](screenshots/3.png)

## Development

- Install requirements: `pip3 install -r requirements.txt`.
- Package:
  - `fbs freeze`
  - `fbs installer`
- Run tests: `python3 -m unittest discover -s src/main/python/ -p 'test_*.py'`
- Run linter: `black src/main/python/`