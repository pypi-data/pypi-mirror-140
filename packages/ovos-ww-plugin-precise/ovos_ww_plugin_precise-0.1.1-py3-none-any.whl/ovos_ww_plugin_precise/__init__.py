# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import distutils.spawn
from ovos_plugin_manager.templates.hotwords import HotWordEngine
from ovos_utils.log import LOG
from os.path import join, isfile, expanduser, isdir
from petact import install_package
import platform
from ovos_utils.xdg_utils import xdg_data_home
from precise_runner import PreciseRunner, PreciseEngine, ReadWriteStream


class PreciseHotwordPlugin(HotWordEngine):
    """Precise is the default wake word engine for Mycroft.

    Precise is developed by Mycroft AI and produces quite good wake word
    spotting when trained on a decent dataset.
    """

    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super().__init__(key_phrase, config, lang)
        self.expected_duration = self.config.get("expected_duration") or 3
        self.has_found = False
        self.stream = ReadWriteStream()

        self.trigger_level = self.config.get('trigger_level', 3)
        self.sensitivity = self.config.get('sensitivity', 0.5)
        self.version = str(self.config.get("version", "0.2"))

        dist_exe = distutils.spawn.find_executable("precise-engine")
        precise_exe = self.config.get("binary_path", dist_exe)
        model = self.config.get('model')

        if not precise_exe:
            precise_exe = self.get_binary(self.version)

        if model and model.startswith("http"):
            model = self.download_model(model)

        if not model or not isfile(expanduser(model)):
            raise ValueError("Model not found")

        self.precise_model = expanduser(model)

        self.runner = PreciseRunner(
            PreciseEngine(precise_exe, self.precise_model),
            self.trigger_level, self.sensitivity,
            stream=self.stream, on_activation=self.on_activation,
        )
        self.runner.start()

    @staticmethod
    def get_binary(version="0.2"):
        base_url = "https://github.com/MycroftAI/mycroft-precise/releases/download/"
        if version == "0.2":
            base_url += "v0.2.0/precise-engine_0.2.0_{arch}.tar.gz"
            folder = join(xdg_data_home(), 'precise02')
        elif version == "0.3":
            base_url += "v0.3.0/precise-engine_0.3.0_{arch}.tar.gz"
            folder = join(xdg_data_home(), 'precise03')
        else:
            LOG.info("Supported versions are 0.2 and 0.3, "
                     "please provide a path to the precise binary")
            raise ValueError("Unsupported Precise Version")

        if not isdir(folder):
            LOG.info("Downloading binary for precise {v}".format(v=version))
            LOG.info("This might take a while")
            arch = platform.machine()
            install_package(base_url.format(arch=arch), folder)
            LOG.info("Binary downloaded")

        precise_exe = join(folder, 'precise-engine', 'precise-engine')
        return precise_exe

    def download_model(self, url):
        if self.version == "0.2":
            folder = join(xdg_data_home(), 'precise02models')
        elif self.version == "0.3":
            folder = join(xdg_data_home(), 'precise03models')
        else:
            LOG.info("Supported versions are 0.2 and 0.3, "
                     "please provide a path to the precise binary")
            raise ValueError("Unsupported Precise Version")

        name = url.split("/")[-1].split(".")[0] + ".pb"
        model_path = join(folder, name)
        if not isfile(model_path):
            LOG.info("Downloading model for precise {v}".format(
                v=self.version))
            LOG.info(url)
            install_package(url, folder)
            LOG.info(f"Model downloaded to {model_path}")

        return model_path

    def on_activation(self):
        self.has_found = True

    def update(self, chunk):
        self.stream.write(chunk)

    def found_wake_word(self, frame_data):
        if self.has_found:
            self.has_found = False
            return True
        return False

    def stop(self):
        if self.runner:
            self.runner.stop()
