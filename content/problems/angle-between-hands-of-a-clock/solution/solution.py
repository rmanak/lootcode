def angleClock(hour, minutes):
    minute_angle = minutes * 6
    hour_angle = (hour % 12) * 30 + minutes * 0.5
    diff = abs(hour_angle - minute_angle)
    return round(min(diff, 360 - diff), 5)
