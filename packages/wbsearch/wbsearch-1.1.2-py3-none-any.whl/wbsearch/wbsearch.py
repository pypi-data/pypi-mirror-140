import webbrowser
import click

@click.command()
#@click.option('--object','-o', help='Words or links you want to serahc on your browser.\nUse "\\" before the space to search multiple words.', required=True, prompt='Words or link:')
@click.argument('object', required=True)
def search(object):
    try:
        object.index('http://')
    except:
        try:
            object.index('https://')
        except:
            object = object.replace(' ', '+')
            webbrowser.open(f'https://www.google.com/search?q={object}')
        else:
            webbrowser.open(object)
    else:
        webbrowser.open(object)