import os
from urllib.parse import quote, unquote
from docutils import nodes
from docutils.parsers.rst import directives
from typing import Optional
from sphinx.application import Sphinx
from sphinx.directives.patches import Figure
from sphinx_metadata_figure import MetadataFigure
import subprocess
import tempfile


DEFAULT_BASE_URL = "https://openla.ewi.tudelft.nl/applet/"

def get_last_modified_date(file_url: str, env) -> Optional[str]:
    """Get last modified date using git only. Caches repo clone in env."""
    try:
        # Parse GitHub URL
        parts = unquote(file_url).split('/blob/')
        if len(parts) != 2:
            return None
        
        owner_repo = parts[0].replace('https://github.com/', '')
        branch_path = parts[1]
        branch, filepath = branch_path.split('/', 1)
        repo_url = f"https://github.com/{owner_repo}.git"
        
        # Use cached clone if available
        if repo_url not in env.git_cache:
            tmpdir = tempfile.mkdtemp(prefix='git_cache_')
            subprocess.run(
                ['git', 'clone', '--filter=blob:none',
                 '--sparse', repo_url, tmpdir],
                check=True, capture_output=True
            )
            env.git_cache[repo_url] = tmpdir
        else:
            tmpdir = env.git_cache[repo_url]
        
        # Get commit date
        result = subprocess.run(
            ['git', '-C', tmpdir, 'log', '-1', '--format=%ci', '--', filepath],
            capture_output=True, text=True, check=True
        )

        date = result.stdout.strip().split(' ')[0]
        return date
    except Exception:
        return None

def _init_git_cache(app, env, docnames):
    """Initialize git cache at start of build."""
    if not hasattr(env, 'git_cache'):
        env.git_cache = {}

def _cleanup_git_cache(app, exception):
    """Clean up temp directories after build."""
    if hasattr(app.env, 'git_cache'):
        import shutil
        for tmpdir in app.env.git_cache.values():
            try:
                shutil.rmtree(tmpdir, ignore_errors=True)
            except:
                pass

def generate_style(height: Optional[str], width: Optional[str]):
	'''
	Given a height and width, generates an inline style that can be used in HTML.
	'''

	styles = ''

	if height:
		styles += f'height: {height};'

	if width:
		styles += f'width: {width};'

	return styles


def parse_value(val: str) -> str:
	'''
	Parses a string value to a string that can be used in a URL query parameter. This is a hacky way to use boolean in docutils.
	(For some reason docutils can't parse 'true' or 'True' strings??)
	'''

	if val == 'enabled':
		return 'true'
	elif val == 'disabled':
		return 'false'
	else:
		return str(val)


def parse_options(options: dict) -> dict:
	# Settings keys that are passed along to the applet iframe
	applet_keys = ['title', 'background', 'autoPlay', 'position', 'isPerspectiveCamera', 'enablePan', 'distance', 'zoom']

	return {key: parse_value(val) for key, val in options.items() if key in applet_keys and val != ''}

class AppletDirective(MetadataFigure):
    option_spec = MetadataFigure.option_spec.copy()
    option_spec.update(
        {
            "url": directives.unchanged_required,
            "fig": directives.unchanged_required,
            "title": directives.unchanged,
            "background": directives.unchanged,
            "autoPlay": directives.unchanged,
            "position": directives.unchanged,
            "isPerspectiveCamera": directives.unchanged,
            "enablePan": directives.unchanged,
            "distance": directives.unchanged,
            "zoom": directives.unchanged,
            "height": directives.unchanged,
            "width": directives.unchanged,
            "status": directives.unchanged,
        }
    )
    required_arguments = 0

    def run(self):

        # Access environment/config
        env = getattr(self.state.document.settings, 'env', None)
        config = getattr(env.app, 'config', None) if env else None
        base_url = config.prime_applets_base_url if config and hasattr(config, 'prime_applets_base_url') else DEFAULT_BASE_URL

        url = self.options.get("url")
        fig = self.options.get("fig")

        assert url is not None
        if "?" in url:
             url, url_params = url.split("?", 1)
        else:
             url_params = ""
        if fig is None:
            fig = base_url + url + "/image.png"
        
        iframe_class = self.options.get("class")  # expect a list/string of classes

        if iframe_class is None:
            iframe_class = ""
        elif isinstance(iframe_class, list):
            iframe_class = " ".join(iframe_class)
        else:
            iframe_class = str(iframe_class)

        self.arguments = [fig]
        self.options["class"] = ["applet-print-figure"]

        metadata = getattr(config, 'prime_applets_metadata', True) if config else True
        if metadata:
            # Use MetadataFigure to add metadata to the figure
            self.options["author"] = self.options["author"] if "author" in self.options else "PRIME"
            self.options["license"] = self.options["license"] if "license" in self.options else "CC-BY"
            repo_url = f"https://github.com/PRIME-TU-Delft/Open-LA-Applets/blob/main/src/routes/applet/{url}"
            last_modified_date = get_last_modified_date(repo_url,env)
            if last_modified_date:
                self.options["date"] = self.options["date"] if "date" in self.options else last_modified_date
                year = last_modified_date.split("-")[0]
                self.options["copyright"] = self.options["copyright"] if "copyright" in self.options else f"© TU Delft {year}"
            else:
                self.options["copyright"] = self.options["copyright"] if "copyright" in self.options else "© TU Delft"
            self.options["source"] = self.options["source"] if "source" in self.options else f"[PRIME-TU-Delft]({repo_url})"
            # force placement to caption, unless margin or admonition is used as default
            metadata_settings = getattr(config, 'metadata_figure_settings', {}) if config else {}
            style_settings = metadata_settings.get('style', {})
            placement = self.options.get('placement', style_settings.get('placement', 'caption'))
            if placement not in ['margin', 'admonition']: # hide is always overruled to caption
                self.options["placement"] = 'caption'
                (figure_node,) = MetadataFigure.run(self)
                other_nodes = None
            elif placement == 'admonition':
                self.options["placement"] = 'admonition'
                figure_nodes = MetadataFigure.run(self)
                figure_node = figure_nodes[0]
                other_nodes = figure_nodes[1]
            elif placement == 'margin':
                self.options["placement"] = 'margin'
                figure_nodes = MetadataFigure.run(self)
                figure_node = figure_nodes[1]
                other_nodes = figure_nodes[0]
        else:
            # Just create a normal figure node without metadata
            (figure_node,) = Figure.run(self)
            other_nodes = None

        # Generate GET params and inline styling
        # we do not perform validation or sanitization
        params_dict = parse_options(self.options)
        params_dict["iframe"] = (
            "true"  # To let the applet know its being run in an iframe
        )
        if url_params != "":
            for param in url_params.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params_dict[key] = value
                else:
                    params_dict[param] = "true"
        # overwrite language based on document language
        lang = self.state.document.settings.env.config.language
        if lang is None:
            lang = "en"
        params_dict["lang"] = lang  # language is always overwritten
        params = "&".join(
            [f"{key}={quote(value)}" for key, value in params_dict.items()]
        )
        style = generate_style(
            self.options.get("width", None), self.options.get("height", None)
        )

        full_url = f'{base_url}{url}{"?" if params else ""}{params}'
        applet_html = f"""
			<div class="applet" style="{style}; ">
					<iframe class="prime-applet {iframe_class}" src="{full_url}" allow="fullscreen" loading="lazy" frameborder="0"></iframe>
			</div>
		 """
        applet_node = nodes.raw(None, applet_html, format="html")

        # Add applet as the first child node of figure
        figure_node.insert(0, applet_node)

        if metadata:
            if self.options.get('placement', style_settings.get('placement', 'caption')) not in ['margin', 'admonition']:
                return [figure_node]
            elif self.options.get('placement', style_settings.get('placement', 'caption')) == 'admonition':
                return [figure_node] + [other_nodes]
            elif self.options.get('placement', style_settings.get('placement', 'caption')) == 'margin':
                return [other_nodes] + [figure_node]
        else:
            return [figure_node]
        
def setup(app):

    app.setup_extension('sphinx_metadata_figure')
    app.add_config_value("prime_applets_metadata", True, "env")
    app.add_config_value("prime_applets_base_url", DEFAULT_BASE_URL, "env")
    app.add_directive("applet", AppletDirective)
    app.add_css_file('prime_applets.css')
    app.connect("build-finished",write_css)
    app.connect("env-before-read-docs", _init_git_cache)  # Initialize cache
    app.connect("build-finished", _cleanup_git_cache)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

def write_css(app: Sphinx,exc):
  CSS_content = """.applet {
  height: 500px;
}

.applet * {
  width: 100%;
  height: 500px; /* TODO: subject for discussion */
}

.applet-print-figure {
  display: none;
}

.applet iframe {
  border-radius: 10px;
}

@media print {
  .applet iframe {
    display: none;
  }
  .applet-print-figure {
    display: initial;
  }
}"""
  # write the css file
  staticdir = os.path.join(app.builder.outdir, '_static')
  filename = os.path.join(staticdir,'prime_applets.css')
  with open(filename,"w") as css:
        css.write(CSS_content)
