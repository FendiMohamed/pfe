package com.example.util.simpletimetracker.utils

import java.util.Calendar

fun Calendar.getMillis(
    hour: Int,
    minute: Int = 0,
    seconds: Int = 0,
    millis: Int = 0,
): Long {
    set(Calendar.HOUR_OF_DAY, hour)
    set(Calendar.MINUTE, minute)
    set(Calendar.SECOND, seconds)
    set(Calendar.MILLISECOND, millis)
    return timeInMillis
}
