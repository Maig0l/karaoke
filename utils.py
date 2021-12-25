def convertSecondsToTime(duration_sec: int):
    minutes = duration_sec // 60
    remainder = duration_sec - (minutes * 60)
    return f"{minutes:02}:{remainder:02}"

def makeTimeStamp(position, range):
    positionHuman = convertSecondsToTime(position)
    rangeHuman = convertSecondsToTime(range)
    return f"{positionHuman} / {rangeHuman}"
