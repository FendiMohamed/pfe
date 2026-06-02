package com.example.util.simpletimetracker

import com.example.util.simpletimetracker.domain.daysOfWeek.model.DayOfWeek
import com.example.util.simpletimetracker.domain.extension.padDuration
import com.example.util.simpletimetracker.utils.BaseUiTest
import java.util.Calendar

object DateSelectorUtils {

    fun BaseUiTest.toWeekTitle(
        shift: Int,
        firstDayOfWeek: DayOfWeek,
    ): Pair<String, String> {
        val range = timeMapper.toWeekDateTimestamp(
            weeksFromToday = shift,
            startOfDayShift = 0,
            firstDayOfWeek = firstDayOfWeek,
        )
        return calendar
            .apply { timeInMillis = range.first }
            .get(Calendar.DAY_OF_MONTH).toString().padDuration() to
            calendar.apply { timeInMillis = range.second }
                .get(Calendar.DAY_OF_MONTH).toString().padDuration()
    }
}