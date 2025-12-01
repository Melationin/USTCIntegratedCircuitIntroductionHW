import PyLTSpice
import PyLTSpice as spice
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import csv


runner = spice.SimRunner(output_folder='.\\result')
netList = spice.SpiceEditor("Draft7.net")

@st.cache_data
def getData(C = 1e-9,MaxTime = 3e-3,NMOSW = 0.25 * 1e-6,PMOSW = 0.25 * 1e-6):
    netList.set_parameters(C=C)
    netList.set_parameters(MaxTime=MaxTime)
    netList.set_parameters(nmosw=NMOSW)
    netList.set_parameters(pmosw = PMOSW)
    task= runner.run(netList)
    task.join()
    raw_file,log_file = task.get_results()
    raw_data = PyLTSpice.RawRead(raw_file)
    time = raw_data.get_trace("time")
    vin_cap = raw_data.get_trace('V(Vin)')
    vout_cap = raw_data.get_trace('V(Vout)')
    sorted_pairs = [x for x in  sorted(zip(time, vin_cap, vout_cap)) if x[0]>=0 ]
    time, vin_cap, vout_cap = zip(*sorted_pairs)
    return (time,vin_cap,vout_cap)

VIH = 3.5
VIL = 1.5

def analyze_signal_transition(begin_time, data):

    if not data or len(data) < 3:
        raise ValueError("数据格式错误")

    time_arr = np.array(data[0])
    volt_arr = np.array(data[2])

    start_idx = np.searchsorted(time_arr, begin_time)
    start_idx = max(1, start_idx)

    if start_idx >= len(time_arr):
        return None, None

    t_roi = time_arr[start_idx - 1:]
    v_roi = volt_arr[start_idx - 1:]

    def get_interpolated_time(idx, threshold_val):
        v1, v2 = v_roi[idx - 1], v_roi[idx]
        t1, t2 = t_roi[idx - 1], t_roi[idx]
        if v2 == v1: return t1
        fraction = (threshold_val - v1) / (v2 - v1)
        return t1 + fraction * (t2 - t1)

    events = []

    for i in range(1, len(v_roi)):
        v_prev = v_roi[i - 1]
        v_curr = v_roi[i]

        if (v_prev <= VIH < v_curr) or (v_prev >= VIH > v_curr):
            t_cross = get_interpolated_time(i, VIH)
            direction = 'up' if v_curr > v_prev else 'down'
            events.append({'thresh': 'VIH', 'dir': direction, 'time': t_cross})

        if (v_prev <= VIL < v_curr) or (v_prev >= VIL > v_curr):
            t_cross = get_interpolated_time(i, VIL)
            direction = 'up' if v_curr > v_prev else 'down'
            events.append({'thresh': 'VIL', 'dir': direction, 'time': t_cross})

    fall_times = []
    rise_times = []

    last_vih_down_time = None
    last_vil_up_time = None

    for e in events:
        # --- 下降沿逻辑 ---
        if e['thresh'] == 'VIH' and e['dir'] == 'down':
            # 记录下降的起始点
            last_vih_down_time = e['time']

        elif e['thresh'] == 'VIL' and e['dir'] == 'down':
            # 只有当我们之前见过 VIH down，且中间没有被打断时，才算有效下降
            if last_vih_down_time is not None:
                dt = e['time'] - last_vih_down_time
                if dt > 0:
                    fall_times.append(dt)
                last_vih_down_time = None  # 配对消耗掉，重置

        # --- 上升沿逻辑 ---
        elif e['thresh'] == 'VIL' and e['dir'] == 'up':
            # 记录上升的起始点
            last_vil_up_time = e['time']

        elif e['thresh'] == 'VIH' and e['dir'] == 'up':
            if last_vil_up_time is not None:
                dt = e['time'] - last_vil_up_time
                if dt > 0:
                    rise_times.append(dt)
                last_vil_up_time = None

        if e['dir'] == 'up' and last_vih_down_time is not None:
            last_vih_down_time = None
        if e['dir'] == 'down' and last_vil_up_time is not None:
            last_vil_up_time = None

    def clean_stats(times_list): #数据过滤
        if not times_list:
            return None
        arr = np.array(times_list)
        if len(arr) < 3: return np.mean(arr)

        mean = np.mean(arr)
        std = np.std(arr)
        filtered = arr[np.abs(arr - mean) <= 2 * std]
        if len(filtered) == 0: return mean
        return np.mean(filtered)

    avg_fall = clean_stats(fall_times)
    avg_rise = clean_stats(rise_times)

    return avg_fall, avg_rise

@st.cache_data
def read_csv(filename):
    c = []
    up_time = []
    down_time = []

    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            c.append(float(row[0]))
            up_time.append(float(row[1]))
            down_time.append(float(row[2]))
        return (c, up_time, down_time)









if False:
    #TestC = [0.002*i  for i in range(1,50)] + [0.1+ 0.1*i  for i in range(1,50)] + [5+ 0.5*i  for i in range(1,50)]+[30+ 1*i  for i in range(1,25)]

    TestW = [i*5 for i in range(1, 100)]

    upData =[]
    downData = []
    csvData = []

    csvData.append(['NMOSW(nm)', '上升沿(us)', '下降沿(us)'])
    for W in TestW:
        t = analyze_signal_transition( 1e-3,getData(NMOSW = W*1e-9,MaxTime = 10e-3))
        if t != None and t[0] != None and t[1] != None:
            downData.append(t[0])
            upData.append(t[1])
            csvData.append([W,t[1]*1e6,t[0]*1e6])
            plt.rcParams["font.sans-serif"] = ["SimHei"]
            plt.rcParams["axes.unicode_minus"] = False
            plt.title('信号时序分析')
            plt.xlabel('NMOSW (nm)')
            plt.ylabel('上升/下降时间 (s)')
            plt.plot(TestW[0:len(downData)], downData, label="下降时间")
            plt.plot(TestW[0:len(upData)], upData, label="上升时间")
            plt.legend()
            plt.show()
    with open("NMOSW.csv", 'w', newline='') as csvfile:
         writer = csv.writer(csvfile)
         writer.writerows(csvData)
