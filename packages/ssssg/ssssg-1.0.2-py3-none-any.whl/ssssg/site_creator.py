from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from os import device_encoding, walk, makedirs, PathLike
from os.path import abspath, dirname, join
from configparser import ConfigParser
from shutil import copytree
import sass
from http.server import HTTPServer, SimpleHTTPRequestHandler
from .logger import get_logger
from os import getcwd


class JinjaConfig:
    """ Class to create a ConfigParser object

    """
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.root_dir = getcwd()
        self.config_filename = join(self.root_dir, "site.cfg")
        self.default_section = "site"
        self.defaults = {
            "SITENAME": "My Site",
            "SITEURL": "/",
            "STATIC_DIR": "static",
            "STATIC_OUTPUT_DIR": "static",
            "OUTPUT_DIR": "output",
            "SASS_ENABLED": True,
            "SASS_DIR": "sass",
            "CSS_OUTPUT_DIR": "css",
            "TEMPLATES_DIR": "templates",
            "PAGES_DIR": "pages",
        }

    @staticmethod
    def __list_converter() -> list:
        """ List converter.  I forget what this is for.

        :return: list
        """
        return []

    def read_config_file(self) -> dict:
        """ Reads a config file from ConfigParser's default list of files.

        :return: dict of site config
        """
        cp = ConfigParser(converters={"list": self.__list_converter})
        cp.optionxform = lambda option: option
        cp[self.default_section] = self.defaults
        cp.read(self.config_filename)
        self.logger.debug(cp.items('site'))
        return dict(cp.items('site'))


class JinjaSiteCreator:
    """ Class to create a static site using Jinja2 and optionally SASS.

    """
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.root_dir = getcwd()
        self.config = JinjaConfig().read_config_file()
        self.logger.debug(self.config)
        makedirs(self.config['OUTPUT_DIR'], exist_ok=True)
        self.pages = []
        self.config['MENUITEMS'] = []
        self.env = Environment(
            loader=FileSystemLoader(
                [self.config['TEMPLATES_DIR'], self.config['PAGES_DIR']]
            ),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def discover(self) -> dict:
        """ Walks the PAGES_DIR and creates adds them to the render queue.

        :return: A dictionary representing the page.
        """
        pages_dir = join(self.root_dir, self.config['PAGES_DIR'])
        for root, dirs, files in walk(pages_dir):
            for f in files:
                rel_path = root[
                   len(join(self.root_dir, self.config['PAGES_DIR'])) + 1:
                ]
                base_name = f[:-3]
                menu_item = (
                    base_name.title(),
                    f"{join(rel_path, base_name)}.html"
                )
                self.config['MENUITEMS'].append(menu_item)
                template_path = str(f)
                if len(rel_path) > 1:
                    template_path = join(rel_path, f)
                template = self.env.get_template(template_path)
                page = {
                    "base_name": base_name,
                    "rel_path": rel_path,
                    "template": template
                }
                self.logger.debug(page)
                self.pages.append(page)
                return page

    def copy_static(self) -> None:
        """ Copies the static site data from STATIC_DIR to the output
        directory.

        :return: None
        """
        copytree(
            join(self.root_dir, self.config['STATIC_DIR']),
            join(
                self.root_dir,
                self.config['OUTPUT_DIR'],
                self.config['STATIC_OUTPUT_DIR']
            ),
            dirs_exist_ok=True,
        )

    def create_page(
            self, base_name: str, rel_path: PathLike, template: Template
    ) -> None:
        """Renders the pages queued by discover.

        :param base_name:
        :param rel_path:
        :param template:
        :return:
        """
        output_dir = join(self.root_dir, self.config['OUTPUT_DIR'], rel_path)
        makedirs(output_dir, exist_ok=True)
        output_file = join(output_dir, f'{base_name}.html')
        self.logger.debug(f"Writing template: {template}")
        with open(output_file, 'w+') as o:
            o.write(template.render(self.config))

    def compile_sass(self) -> None:
        """ Compiles SASS to CSS in the OUTPUT_DIR.

        :return: None
        """
        css_output_dir = join(
            self.root_dir,
            self.config['OUTPUT_DIR'],
            self.config['STATIC_OUTPUT_DIR'],
            self.config['CSS_OUTPUT_DIR'],
        )
        sass.compile(
            dirname=(join(self.root_dir, self.config['SASS_DIR']), css_output_dir),
            output_style='compressed'
        )

    def create_site(self) -> None:
        """ Discovers and renders pages, copies static data, and compiles CSS.

        :return: None
        """
        self.discover()
        self.copy_static()
        if self.config['SASS_ENABLED']:
            self.compile_sass()
        for page in self.pages:
            self.logger.debug(f"Adding page: {page}")
            self.create_page(**page)

    def start_dev_server(self) -> None:
        """ Starts a development server.
        This server should not be run in production.

        :return: None
        """
        dev_port = 8088
        self.logger.info(f"Starting server on http://localhost:{dev_port}")
        server_address = ('', dev_port)
        httpd = HTTPServer(server_address, DevHandler)
        httpd.serve_forever()


class DevHandler(SimpleHTTPRequestHandler):
    """ Class to handle simple http dev server.

    """
    def __init__(self, *args, **kwargs) -> None:
        self.logger = get_logger(__name__)
        self.config = JinjaConfig().read_config_file()
        super().__init__(*args, directory=self.config['OUTPUT_DIR'], **kwargs)
