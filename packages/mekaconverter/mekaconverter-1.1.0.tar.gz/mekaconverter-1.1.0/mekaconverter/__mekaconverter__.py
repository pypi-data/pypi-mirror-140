import datetime
import os
import json
import re
import click
import pyfiglet


def parse_component_number(fileName, letter):
    rgx = r'\_' + letter + r'(.*?)\_'
    rgx2 = r'\--' + letter + r'(.*?)\_'
    rgx3 = r'\__' + letter + r'(.*?)\--'
    rgx4 = letter + r'(.*?)\--'

    result = ''

    if re.search(rgx, fileName):
        result = re.search(rgx, fileName).group(1)
    elif re.search(rgx2, fileName):
        result = re.search(rgx2, fileName).group(1)
    elif re.search(rgx3, fileName):
        result = re.search(rgx3, fileName).group(1)
    elif re.search(rgx4, fileName):
        result = re.search(rgx4, fileName).group(1)
    else:
        return None

    return re.sub('[^0-9]', '', result)


@click.group()
@click.version_option("1.1.0")
def main():
    pass


@main.command()
@click.option('--path', default=os.getcwd(), help='Path to the directory containing the files to be converted.')
@click.option('--output', default=os.getcwd(), help='Path to the directory where the converted files will be saved.')
def convert(path, output):
    click.echo(pyfiglet.figlet_format("MekaConverter", font="rectangles"))
    click.echo('Source: ' + path)
    click.echo('Destination: ' + output + '\n')

    directory = path
    assets = []
    files_length = 0

    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
            files_length += 1
            arms = parse_component_number(filename, 'A')
            body = parse_component_number(filename, 'BO')
            eye = parse_component_number(filename, 'E')
            background = parse_component_number(filename, 'B')
            frame = parse_component_number(filename, 'F')

            assets.append(
                {
                    'name': filename.split('.', 1)[0].split('--X', 1)[0],
                    'frame': frame,
                    'components': {
                        'arms': arms,
                        'body': body,
                        'eye': eye,
                        'background': background
                    }
                }
            )

    assets_length = len(assets)
    if files_length == 0:
        click.echo('No files found in ' + directory)
        exit(1)

    if files_length != assets_length:
        print('Files and assets do not match!')
        exit(1)

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    click.echo('Saving to file: ' + output + '/export--' + timestamp + '.json')
    with open('export--' + timestamp + '.json', 'w') as outfile:
        json.dump(assets, outfile, indent=4, sort_keys=True)

    print(assets_length, 'assets converted to file: ' +
          output + '/export--' + timestamp + '.json')


if __name__ == '__main__':
    main()