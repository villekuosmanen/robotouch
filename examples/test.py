import asyncio
from queue import Empty, Queue
import time

from tqdm import tqdm

from voyage_touch import TouchSensor
from voyage_touch import SensorType

NO_OF_SENSORS = 3

if __name__ == '__main__':
    sensor = TouchSensor('/dev/ttyACM0')

    # initialise sensor
    q = Queue()
    sensor.register_listener(0, q)
    thread = asyncio.run(sensor.start())

    # set up progress bars 
    progress_bars = []
    for i in range(NO_OF_SENSORS):
        progress_bars.append(tqdm(total=1000, desc=f'FSR {i+1}', ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'))
    for i in range(NO_OF_SENSORS):
        progress_bars.append(tqdm(total=160, desc=f'PZ {i+1}', ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'))
    
    # run for 1 minute
    start_time = time.time()

    # do something
    while True:
        try:
            msg = q.get()

            sensor_id = msg.sensor_id
            if msg.sensor_type is SensorType.PIEZO:
                sensor_id += NO_OF_SENSORS

            value = msg.value
            if msg.sensor_type is SensorType.PIEZO:
                value *= 160
            else:
                value *= 1000

            progress_bars[sensor_id].n = value
            progress_bars[sensor_id].refresh()

        except Empty:
            pass

    # graceful shutdown
    sensor.stop()
    thread.join()