import librosa
import numpy
from os import path


def msToHMS(ms):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    m = str(m).rjust(2, '0')
    s = str(s).rjust(2, '0')
    ms = str(ms).rjust(3, '0')
    return f'{h}:{m}:{s}.{ms}'

print('请注意：这只是一个辅助工具，请务必修轴。')

while True:
    soundFile = input('把音频文件拖入此窗口/手动打路径，然后回车\n')
    soundDir, soundName = path.split(soundFile)
    soundName = soundName.split('.')[0]
    subFile = f'{soundDir}\\{soundName}.ass'
    soundThreshold = float(input('请输入音频敏感度，越小越敏感，建议值：0.025\n'))
    timeThreshold = int(input('请输入时间阈值，过小可能导致闪轴，单位ms，建议值：300\n')) #ms
    timeExtend = int(input('请输入时间后延值，单位ms，建议值：200\n')) #ms
    timeAdvance = int(input('请输入时间提前值，单位ms，建议值：50\n'))
    subtitleHead = '''\
        [V4+ Styles]
        Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

        [Events]
        Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

        '''

    y, sr = librosa.load(soundFile)
    y = y.tolist()

    count = 0
    time = []
    for i in y:
        count += 1
        if abs(i) >= soundThreshold:
            time.append(count/sr*1000) #second -> ms

    count = 0
    startPointRecorded = False
    timeRange = []
    temp = []
    for i in time:
        if not startPointRecorded:
            start = round(i) - timeAdvance
            if start < 0:
                start = 0
            temp.append(start)
            startPointRecorded = True
        try: #if last item
            time[count+1]
        except IndexError:
            temp.append(round(i)+timeExtend)
            timeRange.append(temp)
            break
        if time[count+1] - time[count] >= timeThreshold:
            temp.append(round(i)+timeExtend)
            timeRange.append(temp)
            temp = []
            startPointRecorded = False
        count += 1

    sub = subtitleHead
    for i in timeRange:
        start = i[0]
        end = i[1]
        sub += f'Dialogue: 0,{msToHMS(start)},{msToHMS(end)},Default,,0,0,0,,\n'

    with open(subFile, 'w+') as f:
        f.write(sub)

    print('字幕文件已保存至：', subFile)
