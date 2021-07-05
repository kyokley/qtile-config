import requests
import json
import re
import shlex
import schedule
import os
import random
import subprocess
import multiprocessing

from datetime import datetime, timedelta
from dateutil import tz
from pathlib import Path
from collections import namedtuple
from custom.utils import determine_browser

from libqtile.widget.generic_poll_text import GenPollText
from libqtile.widget.graph import CPUGraph

rand = random.SystemRandom()

BUTTON_UP = 4
BUTTON_DOWN = 5
BUTTON_LEFT = 1
BUTTON_MIDDLE = 2
BUTTON_RIGHT = 3

VT_CMD = ('docker run --rm -v /home/yokley/.ssh:/root/.ssh '
          '--env VT_URL=https://almagest.dyndns.org:7001/vittlify/ '
          '--env VT_USERNAME=yokley --env VT_DEFAULT_LIST=personal '
          '--env VT_PROXY= --net=host kyokley/vt list -quW')
GCAL_CMD = ('docker run --rm '
            '-v /home/yokley/.gcalcli_oauth:/root/.gcalcli_oauth '
            'kyokley/gcalcli')
KRILL_CMD = (
    'docker run --rm --cpus=.25 kyokley/krill '
    'krill++ -S /app/sources.txt --snapshot')

KRILL_BROWSER = determine_browser()
MAX_KRILL_LENGTH = 100

XAUTOLOCK_STATUS_PATH = Path('/tmp/xautolock.status')


class ScheduledWidget(GenPollText):
    defaults = [
        ('interval', .5, 'Run every interval minutes'),
    ]

    def __init__(self, **config):
        config['func'] = self._poll_func
        config['update_interval'] = 1
        super().__init__(**config)
        self.add_defaults(ScheduledWidget.defaults)

        self._schedule_job(self.interval)
        self.text = ''

    def _job(self):
        return lambda: None

    def _schedule_job(self, interval):
        schedule.every(interval).minutes.at(':00').do(self._job())

    def _poll_func(self):
        schedule.run_pending()
        return self.text

    def update(self, text):
        if self.text != text:
            if self.layout:
                old_width = self.layout.width

            self.text = text

            # If our width hasn't changed, we just draw ourselves. Otherwise,
            # we draw the whole bar.
            if self.layout:
                old_width = self.layout.width
                if self.layout.width == old_width:
                    self.draw()
                else:
                    self.bar.draw()


class WallpaperDir(ScheduledWidget):
    defaults = [
        ("directory", "~/Pictures/wallpapers/", "Wallpaper Directory"),
        ("wallpaper_command", None, "Wallpaper command"),
        ("label", None, "Use a fixed label instead of image name."),
        ("all_images_label", "All", "Label to use for all images"),
        ("middle_click_command", None, "Command to run for middle-click"),
    ]

    def __init__(self, **config):
        config['interval'] = 15
        super().__init__(**config)
        self.add_defaults(WallpaperDir.defaults)

        self._directories = dict()
        self._dir_index = 0
        self._image_index = 0
        self._cur_image = None

        self.text = 'N/A'
        self.set_wallpaper()

    def _job(self):
        return self.set_wallpaper

    @staticmethod
    def _is_image(path):
        if path.is_file() and path.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            return True
        return False

    def get_wallpapers(self):
        self._directories = {self.all_images_label: []}
        for root, dirs, files in os.walk(self.directory):
            root_path = Path(root).resolve()

            for file in sorted(files):
                file_path = root_path / file
                if not self._is_image(file_path):
                    continue

                self._directories.setdefault(
                    self.all_images_label, []).append(file_path)

            for dir in sorted(dirs):
                dir_path = root_path / dir

                for file in sorted(os.listdir(dir_path)):
                    file_path = dir_path / file
                    if file_path.is_file() and self._is_image(file_path):
                        self._directories.setdefault(
                            dir_path.name, []).append(file_path)
                        self._directories.setdefault(
                            self.all_images_label, []).append(file_path)

    def set_wallpaper(self, use_random=True):
        self.get_wallpapers()
        try:
            directory = list(self._directories.keys())[self._dir_index]
        except IndexError:
            self._dir_index = 0
            directory = list(self._directories.keys())[self._dir_index]

        images = self._directories[directory]

        if not images:
            self.update('Empty')
            return

        try:
            if use_random:
                self._image_index = rand.randint(0, len(images) - 1)
            else:
                self._image_index = self._image_index % len(images)

            self._cur_image = images[self._image_index]
        except IndexError:
            self._image_index = 0
            self._cur_image = images[self._image_index]

        if self.label is None:
            cur_image_basename = os.path.basename(self._cur_image)
            cur_image_basename = (
                f'{cur_image_basename[:7]}...'
                if len(cur_image_basename) > 7 else cur_image_basename)
            text = f'{directory}: {cur_image_basename}'
        else:
            text = self.label

        num_displays = int(subprocess.check_output(
            'xrandr | grep connected -w | wc -l', shell=True).strip())

        if self.wallpaper_command:
            self.wallpaper_command.append(self._cur_image)
            subprocess.call(self.wallpaper_command)
            self.wallpaper_command.pop()
        else:
            command = [
                'nitrogen',
                '--head=0',
                '--set-scaled',
                '--save',
                self._cur_image,
            ]
            subprocess.call(command)

            if num_displays > 1:
                for i in range(1, num_displays):
                    command = [
                        'nitrogen',
                        f'--head={i}',
                        '--random',
                        '--set-scaled',
                        '--save',
                        os.path.dirname(self._cur_image),
                    ]
                    subprocess.call(command)

        print(f'Update text to {text}')
        self.update(text)

    def button_press(self, x, y, button):
        print(button)
        if button == BUTTON_LEFT:
            self._image_index += 1
            self.set_wallpaper(use_random=False)
        elif button == BUTTON_RIGHT:
            self._image_index -= 1
            self.set_wallpaper(use_random=False)
        elif button == BUTTON_MIDDLE:
            if self.middle_click_command:
                command = shlex.split(
                    self.middle_click_command)
                command.append(self._cur_image)
                subprocess.call(command)
            else:
                self.set_wallpaper(use_random=True)
        elif button == BUTTON_UP:
            self._dir_index += 1
            self.set_wallpaper(use_random=False)
        elif button == BUTTON_DOWN:
            self._dir_index -= 1
            self.set_wallpaper(use_random=False)


class ScreenLockIndicator(GenPollText):
    defaults = [
        ('update_interval', 10, 'Update interval'),
    ]

    def __init__(self, **config):
        config['func'] = self.check_autolock
        super().__init__(**config)
        self.add_defaults(ScreenLockIndicator.defaults)

    def check_autolock(self):
        try:
            with open(XAUTOLOCK_STATUS_PATH, 'r') as f:
                output = f.read().strip()

            if output == 'disabled':
                return 'SL Disabled'
            elif output == 'enabled':
                return ''
        except FileNotFoundError:
            pass
        return 'SL Status Unknown'


class CachedProxyRequest(GenPollText):
    defaults = [
        ('http_proxy', None, 'HTTP proxy to use for requests'),
        ('https_proxy', None, 'HTTPS proxy to use for requests'),
        ('socks_proxy', None, 'SOCKS proxy to use for requests'),
        ('cache_expiration',
         5,
         'Length of time in minutes that cache is valid for'),
        ('debug', False, 'Enable additional debugging'),
        ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(CachedProxyRequest.defaults)
        self._last_update = None
        self._cached_data = None
        self._locked = False

    def _print(self, msg):
        if self.debug:
            print('{}: {}'.format(self.__class__, msg))

    def cached_fetch(self):
        if self._locked:
            self._print('Instance locked. Returning cached data')
            return self._cached_data

        try:
            self._print('Setting lock')
            self._locked = True
            if (not self._cached_data or
                    not self._last_update or
                    self._last_update + timedelta(
                        minutes=self.cache_expiration) < datetime.now()):
                self._print('Getting data')
                self._cached_data = self._fetch()
                self._print('Got:')
                self._print(self._cached_data)
                self._last_update = datetime.now()
        except Exception as e:
            self._print('Got error')
            self._print(str(e))
        finally:
            self._print('Releasing lock')
            self._locked = False
            return self._cached_data

    def _fetch(self):
        proxies = {'http': self.http_proxy,
                   'https': self.https_proxy,
                   }
        resp = requests.get(self.URL, proxies=proxies)
        resp.raise_for_status()

        return resp.json()

    def clear_cache(self):
        self._last_update = None
        self._cached_data = None


WeatherTuple = namedtuple('WeatherTuple', 'temp conditions')


class Weather(CachedProxyRequest):
    URL = ('http://api.openweathermap.org/data/2.5/weather?'
           'id=4887398&units=imperial&appid=c4f4551816bd45b67708bea102d93522')
    defaults = [
        ('low_temp_threshold', 45, 'Temp to trigger low foreground'),
        ('high_temp_threshold', 80, 'Temp to trigger high foreground'),
        ('low_foreground', '18BAEB', 'Low foreground'),
        ('normal_foreground', 'FFDE3B', 'Normal foreground'),
        ('high_foreground', 'FF000D', 'High foreground'),
        ('markup', False, 'Do not use pango markup'),
        ]

    def __init__(self, **config):
        config['func'] = self.get_weather
        super().__init__(**config)
        self.add_defaults(Weather.defaults)

    def get_weather(self):
        data = self.cached_fetch()
        if data:
            conditions = rand.choice(data['weather'])['description']

            tup = WeatherTuple(data['main']['temp'], conditions)

            if tup.temp > self.high_temp_threshold:
                self.foreground = self.high_foreground
            elif tup.temp < self.low_temp_threshold:
                self.foreground = self.low_foreground
            else:
                self.foreground = self.normal_foreground

            return '{temp:.2g}F {conditions}'.format(temp=tup.temp,
                                                     conditions=tup.conditions)
        return 'N/A'

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            self.clear_cache()
            weather = self.get_weather()

            self.update(weather)


class VT(CachedProxyRequest):
    REGEX = re.compile(b'(?<=\x1b\[95m).*?(?=\x1b\[39m)') # noqa

    defaults = [('markup', False, 'Do not use pango markup'),
                ('debug', False, 'Enable additional debugging'),
                ]

    def __init__(self, **config):
        config['func'] = self.get_vt
        super().__init__(**config)
        self.add_defaults(VT.defaults)
        self._current_item = None

    def get_vt(self):
        self._data = self.cached_fetch()
        self._current_item = rand.choice(
            self._data) if self._data else b'No items'
        return self._current_item.decode('utf-8')

    def _fetch(self):
        cmd = shlex.split(VT_CMD)

        try:
            proc = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            self._print(str(e))
            return [b'Failed to load']

        if proc:
            lines = [b' '.join(x.strip().split()[1:])
                     for x in proc.splitlines()
                     if x and x.strip()]
            self._print(lines)
            return lines
        return [b'Failed to load']

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            self.get_vt()
        elif button in (BUTTON_UP, BUTTON_DOWN):
            if self._data and self._current_item in self._data:
                if button == BUTTON_UP:
                    idx = self._data.index(self._current_item) + 1
                else:
                    idx = self._data.index(self._current_item) - 1
                self._current_item = self._data[idx % len(self._data)]
                self._last_update = datetime.now() + timedelta(
                    seconds=self.update_interval)
            else:
                return

        self.update(self._current_item.decode('utf-8'))


class GCal(CachedProxyRequest):
    DATE_FORMAT = '%a %b %d %H:%M:%S %Z %Y'
    SPACE_REGEX = re.compile(b'\s+') # noqa

    defaults = [
        ('default_foreground', 'FFDE3B', 'Default foreground color'),
        ('soon_foreground', 'FF000D', 'Color used for events occuring soon'),
        ('markup', False, 'Do not use pango markup'),
        ]

    def __init__(self, **config):
        config['func'] = self.get_cal
        super().__init__(**config)
        self.add_defaults(GCal.defaults)
        self._current_item = None
        self.foreground = self.default_foreground

    def get_cal(self):
        self._data = self.cached_fetch()

        if not self._data:
            return 'No Events'

        self._current_item = rand.choice(self._data)
        if self._current_item[0]:
            self.foreground = self.soon_foreground
        else:
            self.foreground = self.default_foreground

        return self._format_line(self._current_item[1])

    def _format_line(self, line):
        line = line.decode('utf-8').split()
        return '{event} ({date})'.format(event=' '.join(line[3:]),
                                         date=' '.join(line[:3]))

    def _fetch(self):
        now = datetime.now(tz=tz.gettz('America/Chicago'))
        past_dt = now - timedelta(hours=1)
        short_dt = now + timedelta(hours=1)
        future_dt = now + timedelta(hours=120)

        short_cmd = shlex.split(GCAL_CMD)
        if self.https_proxy:
            short_cmd.extend(['--proxy', self.https_proxy])

        short_cmd.extend(['--nocolor',
                          '--prefix',
                          '%a %b %d',
                          'agenda',
                          past_dt.strftime(GCal.DATE_FORMAT),
                          short_dt.strftime(GCal.DATE_FORMAT),
                          '--noallday',
                          ])

        proc = subprocess.check_output(short_cmd)

        if proc:
            lines = [(True, GCal.SPACE_REGEX.sub(b' ', x))
                     for x in proc.splitlines()
                     if x and not x.startswith(b'No Events Found')]

        long_cmd = shlex.split(GCAL_CMD)
        if self.https_proxy:
            long_cmd.extend(['--proxy', self.https_proxy])

        long_cmd.extend(['--nocolor',
                         '--prefix',
                         '%a %b %d',
                         'agenda',
                         short_dt.strftime(GCal.DATE_FORMAT),
                         future_dt.strftime(GCal.DATE_FORMAT),
                         ])

        proc = subprocess.check_output(long_cmd)

        if proc:
            lines.extend(
               [(False, GCal.SPACE_REGEX.sub(b' ', x))
                   for x in proc.splitlines()
                if x and GCal.SPACE_REGEX.sub(b' ', x) not in map(
                    lambda x: x[1], lines)])
        return lines

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            self.get_cal()
        elif button == BUTTON_RIGHT:
            self.clear_cache()
        elif button in (BUTTON_UP, BUTTON_DOWN):
            if self._data:
                if button == BUTTON_UP:
                    idx = self._data.index(self._current_item) + 1
                else:
                    idx = self._data.index(self._current_item) - 1
                self._current_item = self._data[idx % len(self._data)]
                self._last_update = datetime.now() + timedelta(
                        seconds=self.update_interval)
            else:
                return

        self.foreground = (
                self.soon_foreground
                if self._current_item[0] else self.default_foreground)
        self.update(self._format_line(self._current_item[1]))


class Krill(CachedProxyRequest):
    defaults = [('sources_file', None, 'File containing sources'),
                ('markup', False, 'Do not use pango markup'),
                ('debug', False, 'Enable additional debugging'),
                ]

    def __init__(self, **config):
        config['func'] = self.get_krill
        super().__init__(**config)
        self.add_defaults(Krill.defaults)
        self._current_item = None
        self._last_item_change_time = None

    def get_krill(self):
        if not self.sources_file:
            return 'No sources provided'

        self._data = self.cached_fetch()
        if not self._data:
            return 'Could not load data from sources'

        if (not self._last_item_change_time or
                self._last_item_change_time + timedelta(
                    seconds=self.update_interval) < datetime.now()):
            self._current_item = rand.choice(self._data)
            self._last_item_change_time = datetime.now()
        return (self._current_item['title']
                if isinstance(self._current_item, dict)
                else self._current_item)

    def _fetch(self):
        cmd = shlex.split(KRILL_CMD)
        proc = subprocess.check_output(cmd)
        if proc:
            return json.loads(proc)
        return ['Failed to load']

    def button_press(self, x, y, button):
        if button == BUTTON_LEFT:
            if self._current_item and self._current_item.get('link'):
                self.qtile.cmd_spawn(f'{KRILL_BROWSER} {self._current_item["link"]}')
        elif button in (BUTTON_UP, BUTTON_DOWN):
            if self._data:
                if button == BUTTON_UP:
                    idx = self._data.index(self._current_item) + 1
                else:
                    idx = self._data.index(self._current_item) - 1
                self._current_item = self._data[idx % len(self._data)]
                self.update(self._current_item['title'])
                self._last_item_change_time = datetime.now() + timedelta(
                        seconds=self.update_interval)

    def update(self, text):
        if len(text) > MAX_KRILL_LENGTH:
            truncated_text = f'{text[:MAX_KRILL_LENGTH]}...'
        else:
            truncated_text = text

        super().update(truncated_text)


class MaxCPUGraph(CPUGraph):
    def __init__(self, **config):
        self._num_cores = multiprocessing.cpu_count()
        CPUGraph.__init__(self, **config)
        self.oldvalues = self._getvalues()

    def _getvalues(self):
        proc = '/proc/stat'

        with open(proc) as file:
            file.readline()
            lines = file.readlines()

        vals = [line.split(None, 6)[1:5] for line in lines[:self._num_cores]]
        return [map(int, val) for val in vals]

    def update_graph(self):
        new_values = self._getvalues()
        old_values = self.oldvalues

        max_percent = 0
        for old, new in zip(old_values, new_values):
            try:
                old_user, new_user = next(old), next(new)
                old_nice, new_nice = next(old), next(new)
                old_sys, new_sys = next(old), next(new)
                old_idle, new_idle = next(old), next(new)
            except StopIteration:
                continue

            busy = (
                new_user + new_nice + new_sys - old_user - old_nice - old_sys)
            total = busy + new_idle - old_idle

            if total:
                percent = float(busy) / total * 100
            else:
                percent = 0

            max_percent = max(max_percent, percent)

        self.oldvalues = new_values

        if max_percent:
            self.push(max_percent)
