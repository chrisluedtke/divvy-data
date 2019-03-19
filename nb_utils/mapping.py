import time, os

import folium
import folium.plugins
import pandas as pd
from PIL import Image
from selenium import webdriver


def create_map(df, center_at=[41.90, -87.66], zoom=12, width_px=1350,
               height_px=1350, circle_line_weight=0.5,
               show_tooltip=True):
    m = folium.Map(
        location=center_at,
        zoom_start=zoom,
        width=width_px,
        height=height_px,
        zoom_control=False,
        tiles="CartoDB dark_matter")

    for i, r in df.iterrows():
        if r['avg_use'] < 0.01:
            continue

        tooltip=(f'Station: {r.station_id}<br>'
                 f'Average Use: {round(r.avg_use,2)}<br>'
                 f'Departures: {round(r.pt_departures*100,2)}%')

        folium.CircleMarker(
            location=(r['lat'], r['lon']),
            radius=r['radius'] if 'radius' in df else r['avg_use'],
            color=r['color'],
            weight=circle_line_weight,
            tooltip=tooltip if show_tooltip else None,
            fill=True
        ).add_to(m)

    return m


def gen_maps_by_group(df, group_label, preview=False, save_dir=None, **kwargs):
    if save_dir and not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if not save_dir and not preview:
        raise ValueError('Must either preview or save')

    for g_name, g_df in df.groupby(group_label):
        m = create_map(g_df, **kwargs)

        if preview:
            return m
        if save_dir:
            m.save(f"{save_dir}/{str(g_name).zfill(5)}.html")

    return None


def render_maps_dir_to_pngs(maps_dir, output_dir, map_x_px=None, map_y_px=None,
                            sleep_s=3.5):
    driver = get_driver(map_x_px=map_x_px, map_y_px=map_y_px)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for map_fn in os.listdir(maps_dir):
        if not map_fn.endswith('.html'):
            continue

        map_path = os.path.join(maps_dir, map_fn)
        output_path = os.path.join(output_dir, map_fn.replace('.html', '.png'))

        render_html_map_to_png(map_path=map_path, output_path=output_path,
                               driver=driver, sleep_s=sleep_s, quit_after=False)

    return driver.quit()


def get_driver(gecko_path='geckodriver', map_x_px=None, map_y_px=None):
    driver = webdriver.Firefox(executable_path=gecko_path)

    if map_x_px and map_y_px:
        driver.set_window_size(map_x_px, map_y_px + 100)

    return driver


def render_html_map_to_png(map_path, output_path, map_x_px=None, map_y_px=None,
                           driver=None, sleep_s=3.0, quit_after=True,
                           preview=False):
    if not map_path.endswith('.html'):
        raise ValueError('map_path must end in .html')

    if not output_path.endswith('.png'):
        raise ValueError('output_path must end in .png')

    if not driver:
        driver = get_driver()

    driver.get(f'file://{map_path}')
    time.sleep(sleep_s)
    driver.save_screenshot(output_path)
    print(f'Wrote: {output_path}')

    if preview:
        image = Image.open(output_path)
        driver.quit()
        return image.show()

    elif quit_after:
        return driver.quit()

    else:
        return None
