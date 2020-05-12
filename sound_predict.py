import librosa, numpy as np
import librosa.display, time
import matplotlib.pyplot as pyplot

# 此程序借鉴了librosa官方示例中的Viterbi decoding示例：
# https://librosa.github.io/librosa/auto_examples/plot_viterbi.html#sphx-glr-auto-examples-plot-viterbi-py 
# 仅用于练手，作者：Sudo, SorehaitACE


all_res = []

def combine_intervals(start:list, end:list):
    need_remove = []
    needRecheck = False
    for i in range(len(start) - 1):
        if start[i+1] - end[i] <= 0.05:
            if start[i+1] - end[i] <= 0:
                needRecheck = True
                need_remove.append([end[i], start[i+1]])
            elif end[i+1] - start[i] < 8:
                needRecheck = True
                need_remove.append([end[i], start[i+1]])
    if needRecheck:
        for each_pair in need_remove:
            end.remove(each_pair[0])
            start.remove(each_pair[1])
        return combine_intervals(start, end)
    else:
        return (start, end)


def calc(d, transition, i):
    S_full, phase = librosa.magphase(librosa.stft(d,center=False))
    rms = librosa.feature.rms(y=d)[0]
    r_normalized = (rms - 0.02) / np.std(rms)
    p = np.exp(r_normalized) / (1 + np.exp(r_normalized))
    full_p = np.vstack([1 - p, p])
    states = librosa.sequence.viterbi_discriminative(full_p, transition)
    all_res[i] = states


def start(y, sr):
    transition = librosa.sequence.transition_loop(2, [0.5, 0.7])
    count = len(y) // (3*sr)
    print(count)
    for i in range(count + 1):
        all_res.append(0)
    start = time.time()
    if count != 0:
        for i in range(count):
            calc(y[i*3*sr:(i+1)*3*sr], transition, i)
    
        calc(y[count*3*sr:], transition, count)
    else:
        calc(y, transition, 0)
    print(time.time() - start)

if __name__ == "__main__":
    path = '.\\file\\test.mp4'
    start_time = time.time()
    y,sr = librosa.load(path)
    print(f"LOADING takes {time.time()-start_time} seconds")
    rms = librosa.feature.rms(y=y)[0]
    all_times = librosa.frames_to_time(np.arange(len(rms)))
    start(y, sr)
    true_result = []
    for i in range(len(all_res)):
        true_result.extend(all_res[i])
    starts = []
    ends = []

    if true_result[0] == 1:
        starts.append(round(all_times[0],2))

    for i in range(len(all_times) - 1):
        if true_result[i] == 0 and true_result[i + 1] == 1:
            starts.append(round(all_times[i],2))
        elif true_result[i] == 1 and true_result[i + 1] == 0:
            ends.append(round(all_times[i],2))

    if true_result[len(all_times) - 1] == 1:
        ends.append(round(all_times[len(all_times) - 1]))
    
    for i in range(len(starts)):
        # 因为取log原因，需要更加提前，否则开头位置不正
        starts[i] -= 0.040
        if starts[i] < 0:
            starts[i] = 0
        ends[i] += 0.1
    
    real_start, real_end = combine_intervals(starts, ends)

    subtitleHead = '''\
        [V4+ Styles]
        Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

        [Events]
        Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

        '''

    sub = subtitleHead
    for i in range(len(real_start)):
        if real_end[i] - real_start[i] > 0.5:
            sub += f'Dialogue: 0,{real_start[i]},{real_end[i]},Default,,0,0,0,,第{i}行\n'
    with open('result.ass','w',encoding='utf-8') as f:
        f.write(sub)
    
    
