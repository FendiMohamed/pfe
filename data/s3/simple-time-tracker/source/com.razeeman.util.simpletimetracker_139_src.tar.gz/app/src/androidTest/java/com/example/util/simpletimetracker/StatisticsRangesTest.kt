package com.example.util.simpletimetracker

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.contrib.PickerActions.setDate
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withClassName
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withSubstring
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.DateSelectorUtils.toWeekTitle
import com.example.util.simpletimetracker.domain.daysOfWeek.model.DayOfWeek
import com.example.util.simpletimetracker.domain.extension.padDuration
import com.example.util.simpletimetracker.domain.statistics.model.RangeLength
import com.example.util.simpletimetracker.feature_dialogs.dateTime.CustomDatePicker
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnCurrentDate
import com.example.util.simpletimetracker.utils.clickOnCurrentSelectedDate
import com.example.util.simpletimetracker.utils.clickOnPrevDate
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithId
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.dateSelectorMatcher
import com.example.util.simpletimetracker.utils.longClickOnCurrentDate
import com.example.util.simpletimetracker.utils.longClickOnCurrentSelectedDate
import com.example.util.simpletimetracker.utils.selectedDateMatcher
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.withPluralText
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.CoreMatchers.equalTo
import org.junit.Test
import org.junit.runner.RunWith
import java.util.Calendar
import java.util.concurrent.TimeUnit
import com.example.util.simpletimetracker.core.R as coreR
import com.example.util.simpletimetracker.feature_base_adapter.R as baseR
import com.example.util.simpletimetracker.feature_dialogs.R as dialogsR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class StatisticsRangesTest : BaseUiTest() {

    @Test
    fun statisticsRanges() {
        val name = "Test"
        val calendar = Calendar.getInstance()

        // Add data
        testUtils.addActivity(name)
        testUtils.addRecord(
            typeName = name,
            timeStarted = calendar.timeInMillis - TimeUnit.MINUTES.toMillis(1),
            timeEnded = calendar.timeInMillis,
        )

        // Statistics day range
        NavUtils.openStatisticsScreen()
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_day)
        checkViewIsDisplayed(allOf(withText(name), isCompletelyDisplayed()))
        clickOnCurrentDate(-1)
        clickOnCurrentDate(-2)
        longClickOnCurrentDate(-2)
        clickOnCurrentDate(1)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))
        clickOnCurrentDate(2)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))

        // Switch to week range
        clickOnCurrentDate(2)
        checkViewIsDisplayed(withText(coreR.string.range_select_day))
        clickOnViewWithText(coreR.string.range_week)
        checkViewIsDisplayed(allOf(withText(name), isCompletelyDisplayed()))
        clickOnCurrentDate(-1)
        clickOnCurrentDate(-2)
        longClickOnCurrentDate(-2)
        clickOnCurrentDate(1)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))
        clickOnCurrentDate(2)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))

        // Switch to month range
        clickOnCurrentDate(2)
        checkViewIsDisplayed(withText(coreR.string.range_select_week))
        clickOnViewWithText(coreR.string.range_month)
        checkViewIsDisplayed(allOf(withText(name), isCompletelyDisplayed()))
        clickOnCurrentDate(-1)
        clickOnCurrentDate(-2)
        longClickOnCurrentDate(-2)
        clickOnCurrentDate(1)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))
        clickOnCurrentDate(2)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))

        // Switch to year range
        clickOnCurrentDate(2)
        checkViewIsDisplayed(withText(coreR.string.range_select_month))
        clickOnViewWithText(coreR.string.range_year)
        checkViewIsDisplayed(allOf(withText(name), isCompletelyDisplayed()))
        clickOnCurrentDate(-1)
        clickOnCurrentDate(-2)
        longClickOnCurrentDate(-2)
        clickOnCurrentDate(1)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))
        clickOnCurrentDate(2)
        checkViewIsDisplayed(allOf(withText(coreR.string.no_data), isCompletelyDisplayed()))

        // Switch to overall range
        clickOnCurrentDate(2)
        checkViewIsDisplayed(withText(coreR.string.range_select_year))
        clickOnViewWithText(coreR.string.range_overall)
        Thread.sleep(1000)
        checkViewIsDisplayed(allOf(withText(name), isCompletelyDisplayed()))
        checkViewDoesNotExist(dateSelectorMatcher(-1))
        checkViewDoesNotExist(dateSelectorMatcher(1))

        // Switch to custom range
        clickOnCurrentDate()
        checkViewDoesNotExist(withText(coreR.string.range_select_day))
        checkViewDoesNotExist(withText(coreR.string.range_select_week))
        checkViewDoesNotExist(withText(coreR.string.range_select_month))
        checkViewDoesNotExist(withText(coreR.string.range_select_year))
        clickOnViewWithText(coreR.string.range_custom)
        tryAction { clickOnViewWithId(dialogsR.id.btnCustomRangeSelection) }
        checkViewIsDisplayed(allOf(withText(name), isCompletelyDisplayed()))
        checkViewIsDisplayed(dateSelectorMatcher(-1))
        checkViewIsDisplayed(dateSelectorMatcher(1))

        // Switch to last days range
        clickOnCurrentDate()
        checkViewDoesNotExist(withText(coreR.string.range_select_day))
        checkViewDoesNotExist(withText(coreR.string.range_select_week))
        checkViewDoesNotExist(withText(coreR.string.range_select_month))
        checkViewDoesNotExist(withText(coreR.string.range_select_year))
        clickOnView(withPluralText(coreR.plurals.range_last, 7, 7))
        clickOnViewWithText(coreR.string.duration_dialog_save)
        checkViewIsDisplayed(allOf(withText(name), isCompletelyDisplayed()))
        checkViewIsDisplayed(dateSelectorMatcher(-1))
        checkViewIsDisplayed(dateSelectorMatcher(1))

        // Switch back to day
        clickOnCurrentDate()
        checkViewDoesNotExist(withText(coreR.string.range_select_day))
        checkViewDoesNotExist(withText(coreR.string.range_select_week))
        checkViewDoesNotExist(withText(coreR.string.range_select_month))
        checkViewDoesNotExist(withText(coreR.string.range_select_year))
        clickOnViewWithText(coreR.string.range_day)
        clickOnCurrentDate()
        checkViewIsDisplayed(withText(coreR.string.range_select_day))
    }

    @Test
    fun selectNearDateForDays() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            add(Calendar.DATE, -1)
        }
        val titlePrev = calendarPrev.get(Calendar.DAY_OF_MONTH).toString()
        val calendarNext = Calendar.getInstance().apply {
            add(Calendar.DATE, 1)
        }
        val titleNext = calendarNext.get(Calendar.DAY_OF_MONTH).toString()

        // Check yesterday
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_day)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_day)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(
            allOf(
                dateSelectorMatcher(-1),
                hasDescendant(withText(titlePrev)),
            ),
        )

        // Check tomorrow
        clickOnCurrentDate(-1)
        clickOnViewWithText(coreR.string.range_select_day)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(
            allOf(
                dateSelectorMatcher(1),
                hasDescendant(withText(titleNext)),
            ),
        )
    }

    @Test
    fun selectFarDateForDays() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            set(Calendar.YEAR, 1950)
            set(Calendar.MONTH, 0)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titlePrev = calendarPrev.get(Calendar.DAY_OF_MONTH).toString()
        val calendarNext = Calendar.getInstance().apply {
            set(Calendar.YEAR, 2050)
            set(Calendar.MONTH, 0)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titleNext = calendarNext.get(Calendar.DAY_OF_MONTH).toString()

        // Check prev date
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_day)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_day)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateSingleItem(titlePrev)

        // Check next date
        clickOnCurrentSelectedDate()
        clickOnViewWithText(coreR.string.range_select_day)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateSingleItem(titleNext)
    }

    @Test
    fun selectNearDateForWeeks() {
        testUtils.setFirstDayOfWeek(DayOfWeek.SUNDAY)
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            add(Calendar.WEEK_OF_YEAR, -1)
        }
        val titlePrev = calendar.let {
            it.timeInMillis = timeMapper.getRangeStartAndEnd(
                rangeLength = RangeLength.Week,
                shift = -1,
                firstDayOfWeek = DayOfWeek.SUNDAY,
                startOfDayShift = 0,
            ).timeStarted
            it.get(Calendar.DAY_OF_MONTH).toString().padDuration()
        }
        val calendarNext = Calendar.getInstance().apply {
            add(Calendar.WEEK_OF_YEAR, 1)
        }
        val titleNext = calendar.let {
            it.timeInMillis = timeMapper.getRangeStartAndEnd(
                rangeLength = RangeLength.Week,
                shift = 1,
                firstDayOfWeek = DayOfWeek.SUNDAY,
                startOfDayShift = 0,
            ).timeStarted
            it.get(Calendar.DAY_OF_MONTH).toString().padDuration()
        }

        // Check prev week
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_week)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(
            allOf(
                dateSelectorMatcher(-1),
                hasDescendant(withText(titlePrev)),
            ),
        )

        // Check next week
        clickOnCurrentDate(-1)
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(
            allOf(
                dateSelectorMatcher(1),
                hasDescendant(withText(titleNext)),
            ),
        )
    }

    @Test
    fun selectFarDateForWeeks() {
        testUtils.setFirstDayOfWeek(DayOfWeek.SUNDAY)
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            add(Calendar.WEEK_OF_YEAR, -2500)
        }
        val titlePrev = toWeekTitle(-2500, DayOfWeek.SUNDAY)
        val calendarNext = Calendar.getInstance().apply {
            add(Calendar.WEEK_OF_YEAR, 2500)
        }
        val titleNext = toWeekTitle(2500, DayOfWeek.SUNDAY)

        // Check prev date
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_week)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateRangeItem(titlePrev)

        // Check next date
        clickOnCurrentSelectedDate()
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateRangeItem(titleNext)
    }

    @Test
    fun selectLastWeekOfYear() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            set(Calendar.YEAR, 1960)
            set(Calendar.MONTH, 11)
            set(Calendar.DAY_OF_MONTH, 31)
        }
        val titlePrev = toWeekDateTitle(calendarPrev.timeInMillis)
        val calendarNext = Calendar.getInstance().apply {
            set(Calendar.YEAR, 2060)
            set(Calendar.MONTH, 11)
            set(Calendar.DAY_OF_MONTH, 31)
        }
        val titleNext = toWeekDateTitle(calendarNext.timeInMillis)

        // Check prev date
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_week)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateRangeItem(titlePrev)

        // Check next date
        clickOnCurrentSelectedDate()
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateRangeItem(titleNext)
    }

    @Test
    fun selectFirstWeekOfYear() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            set(Calendar.YEAR, 1961)
            set(Calendar.MONTH, 1)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titlePrev = toWeekDateTitle(calendarPrev.timeInMillis)
        val calendarNext = Calendar.getInstance().apply {
            set(Calendar.YEAR, 2061)
            set(Calendar.MONTH, 1)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titleNext = toWeekDateTitle(calendarNext.timeInMillis)

        // Check prev date
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_week)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateRangeItem(titlePrev)

        // Check next date
        clickOnCurrentSelectedDate()
        clickOnViewWithText(coreR.string.range_select_week)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateRangeItem(titleNext)
    }

    @Test
    fun selectNearDateForMonths() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            add(Calendar.MONTH, -1)
        }
        val titlePrev = toMonthDateTitle(calendarPrev.timeInMillis)
        val calendarNext = Calendar.getInstance().apply {
            add(Calendar.MONTH, 1)
        }
        val titleNext = toMonthDateTitle(calendarNext.timeInMillis)

        // Check prev months
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_month)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_month)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateSingleItem(titlePrev)

        // Check next month
        clickOnCurrentSelectedDate()
        clickOnViewWithText(coreR.string.range_select_month)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateSingleItem(titleNext)
    }

    @Test
    fun selectFarDateForMonths() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            set(Calendar.YEAR, 1950)
            set(Calendar.MONTH, 0)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titlePrev = toMonthDateTitle(calendarPrev.timeInMillis)
        val calendarNext = Calendar.getInstance().apply {
            set(Calendar.YEAR, 2050)
            set(Calendar.MONTH, 0)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titleNext = toMonthDateTitle(calendarNext.timeInMillis)

        // Check prev date
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_month)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_month)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(allOf(withText(titlePrev), isCompletelyDisplayed()))

        // Check next date
        clickOnCurrentSelectedDate()
        clickOnViewWithText(coreR.string.range_select_month)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(allOf(withText(titleNext), isCompletelyDisplayed()))
    }

    @Test
    fun selectNearDateForYears() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            add(Calendar.YEAR, -1)
        }
        val titlePrev = toYearDateTitle(calendarPrev.timeInMillis)
        val calendarNext = Calendar.getInstance().apply {
            add(Calendar.YEAR, 1)
        }
        val titleNext = toYearDateTitle(calendarNext.timeInMillis)

        // Check prev months
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_year)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_year)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(
            allOf(
                dateSelectorMatcher(-1),
                hasDescendant(withText(titlePrev)),
            ),
        )

        // Check next month
        clickOnCurrentDate(-1)
        clickOnViewWithText(coreR.string.range_select_year)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkViewIsDisplayed(
            allOf(
                dateSelectorMatcher(1),
                hasDescendant(withText(titleNext)),
            ),
        )
    }

    @Test
    fun selectFarDateForYears() {
        NavUtils.openStatisticsScreen()

        val calendarPrev = Calendar.getInstance().apply {
            set(Calendar.YEAR, 1950)
            set(Calendar.MONTH, 0)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titlePrev = toYearDateTitle(calendarPrev.timeInMillis)
        val calendarNext = Calendar.getInstance().apply {
            set(Calendar.YEAR, 2050)
            set(Calendar.MONTH, 0)
            set(Calendar.DAY_OF_MONTH, 1)
        }
        val titleNext = toYearDateTitle(calendarNext.timeInMillis)

        // Check prev date
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_year)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_select_year)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarPrev.get(Calendar.YEAR),
                calendarPrev.get(Calendar.MONTH) + 1,
                calendarPrev.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateSingleItem(titlePrev)

        // Check next date
        clickOnCurrentSelectedDate()
        clickOnViewWithText(coreR.string.range_select_year)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name))).perform(
            setDate(
                calendarNext.get(Calendar.YEAR),
                calendarNext.get(Calendar.MONTH) + 1,
                calendarNext.get(Calendar.DAY_OF_MONTH),
            ),
        )
        clickOnViewWithId(dialogsR.id.btnDateTimeDialogPositive)

        checkDateSingleItem(titleNext)
    }

    @Test
    fun customRange() {
        val name1 = "Test1"
        val name2 = "Test2"

        // Add data
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        var calendar = Calendar.getInstance().apply {
            add(Calendar.DATE, -1)
            set(Calendar.HOUR_OF_DAY, 15)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
        }
        testUtils.addRecord(
            typeName = name1,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(1),
        )
        calendar = Calendar.getInstance().apply {
            add(Calendar.DATE, -2)
            set(Calendar.HOUR_OF_DAY, 15)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
        }
        testUtils.addRecord(
            typeName = name2,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(2),
        )

        // Check custom range not selected
        NavUtils.openStatisticsScreen()
        checkViewDoesNotExist(allOf(withText(name1), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withText(name2), isCompletelyDisplayed()))
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_day)
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_custom)
        pressBack()
        tryAction {
            checkViewDoesNotExist(withId(R.id.containerDateSelectorRange))
        }

        // Select custom range default
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_custom)
        clickOnViewWithId(dialogsR.id.btnCustomRangeSelection)
        val rangeTitle = calendar.apply {
            timeInMillis = System.currentTimeMillis()
        }.get(Calendar.DAY_OF_MONTH).toString()
        checkViewIsDisplayed(
            allOf(
                dateSelectorMatcher(0),
                withId(R.id.containerDateSelectorRange),
                hasDescendant(
                    allOf(
                        withId(R.id.tvDateSelectorBottomText1),
                        withText(rangeTitle),
                    ),
                ),
                hasDescendant(
                    allOf(
                        withId(R.id.tvDateSelectorBottomText2),
                        withText(rangeTitle),
                    ),
                ),
            ),
        )
        checkViewDoesNotExist(allOf(withText(name1), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withText(name2), isCompletelyDisplayed()))

        // Check previous
        clickOnCurrentDate(-1)
        checkStatisticsItem(name = name1, hours = 1)
        checkViewDoesNotExist(allOf(withText(name2), isCompletelyDisplayed()))
        clickOnCurrentDate(-2)
        checkViewDoesNotExist(allOf(withText(name1), isCompletelyDisplayed()))
        checkStatisticsItem(name = name2, hours = 2)
        longClickOnCurrentSelectedDate()

        // Select custom range yesterday
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_custom)
        calendar = Calendar.getInstance().apply {
            add(Calendar.DATE, -1)
        }
        NavUtils.setCustomRange(
            yearStarted = calendar.get(Calendar.YEAR),
            monthStarted = calendar.get(Calendar.MONTH),
            dayStarted = calendar.get(Calendar.DAY_OF_MONTH),
            yearEnded = calendar.get(Calendar.YEAR),
            monthEnded = calendar.get(Calendar.MONTH),
            dayEnded = calendar.get(Calendar.DAY_OF_MONTH),
        )

        // Check statistics
        checkStatisticsItem(nameResId = coreR.string.untracked_time_name, hours = 23)
        checkStatisticsItem(name = name1, hours = 1)
        checkViewDoesNotExist(allOf(withText(name2), isCompletelyDisplayed()))

        // Check previous
        clickOnPrevDate()
        checkViewDoesNotExist(allOf(withText(name1), isCompletelyDisplayed()))
        checkStatisticsItem(name = name2, hours = 2)
        longClickOnCurrentDate()

        // Check time set
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_custom)
        var timeStarted = calendar.timeInMillis.let(timeMapper::formatDateYear)
        var timeEnded = timeStarted

        checkViewIsDisplayed(allOf(withId(dialogsR.id.tvCustomRangeSelectionTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(dialogsR.id.tvCustomRangeSelectionTimeEnded), withText(timeEnded)))

        // Select custom range three days
        var calendarStart = Calendar.getInstance().apply {
            add(Calendar.DATE, -3)
        }
        NavUtils.setCustomRange(
            yearStarted = calendarStart.get(Calendar.YEAR),
            monthStarted = calendarStart.get(Calendar.MONTH),
            dayStarted = calendarStart.get(Calendar.DAY_OF_MONTH),
            yearEnded = calendar.get(Calendar.YEAR),
            monthEnded = calendar.get(Calendar.MONTH),
            dayEnded = calendar.get(Calendar.DAY_OF_MONTH),
        )

        checkStatisticsItem(nameResId = coreR.string.untracked_time_name, hours = 30)
        checkStatisticsItem(name = name1, hours = 1)
        checkStatisticsItem(name = name2, hours = 2)

        // Check previous
        clickOnPrevDate()
        checkViewDoesNotExist(allOf(withText(name1), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withText(name2), isCompletelyDisplayed()))
        longClickOnCurrentDate()

        // Check time set
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_custom)
        timeStarted = calendarStart.timeInMillis.let(timeMapper::formatDateYear)
        timeEnded = calendar.timeInMillis.let(timeMapper::formatDateYear)

        checkViewIsDisplayed(allOf(withId(dialogsR.id.tvCustomRangeSelectionTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(dialogsR.id.tvCustomRangeSelectionTimeEnded), withText(timeEnded)))

        // Select custom range long time ago
        calendar = Calendar.getInstance().apply {
            add(Calendar.DATE, -11)
        }
        calendarStart = Calendar.getInstance().apply {
            add(Calendar.DATE, -20)
        }
        NavUtils.setCustomRange(
            yearStarted = calendarStart.get(Calendar.YEAR),
            monthStarted = calendarStart.get(Calendar.MONTH),
            dayStarted = calendarStart.get(Calendar.DAY_OF_MONTH),
            yearEnded = calendar.get(Calendar.YEAR),
            monthEnded = calendar.get(Calendar.MONTH),
            dayEnded = calendar.get(Calendar.DAY_OF_MONTH),
        )

        checkViewDoesNotExist(allOf(withText(coreR.string.untracked_time_name), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withText(name1), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withText(name2), isCompletelyDisplayed()))

        // Check time set
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_custom)
        timeStarted = calendarStart.timeInMillis.let(timeMapper::formatDateYear)
        timeEnded = calendar.timeInMillis.let(timeMapper::formatDateYear)

        checkViewIsDisplayed(allOf(withId(dialogsR.id.tvCustomRangeSelectionTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(dialogsR.id.tvCustomRangeSelectionTimeEnded), withText(timeEnded)))
    }

    @Test
    fun lastDaysRange() {
        val name1 = "Test1"

        // Add data
        testUtils.addActivity(name1)
        var calendar = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, 15)
        }
        val dateStarted = calendar.get(Calendar.DAY_OF_MONTH).toString().padDuration()
        testUtils.addRecord(
            typeName = name1,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(1),
        )
        calendar = Calendar.getInstance().apply {
            add(Calendar.DATE, -6)
            set(Calendar.HOUR_OF_DAY, 15)
        }
        val dateEnded = calendar.get(Calendar.DAY_OF_MONTH).toString().padDuration()
        testUtils.addRecord(
            typeName = name1,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(1),
        )
        calendar = Calendar.getInstance().apply {
            add(Calendar.DATE, -7)
            set(Calendar.HOUR_OF_DAY, 15)
        }
        testUtils.addRecord(
            typeName = name1,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(1),
        )

        // Select range
        NavUtils.openStatisticsScreen()
        clickOnCurrentDate()
        clickOnView(withPluralText(coreR.plurals.range_last, 7, 7))
        clickOnViewWithText(coreR.string.duration_dialog_save)
        checkViewIsDisplayed(
            allOf(
                withId(R.id.containerDateSelectorRange),
                hasDescendant(withText(dateStarted)),
                hasDescendant(withText(dateEnded)),
            ),
        )
        checkStatisticsItem(name = name1, hours = 2)

        // Check previous
        clickOnPrevDate()
        checkStatisticsItem(name = name1, hours = 1)
    }

    private fun checkStatisticsItem(
        name: String = "",
        nameResId: Int? = null,
        hours: Int,
    ) {
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewStatisticsItem),
                hasDescendant(if (nameResId != null) withText(nameResId) else withText(name)),
                hasDescendant(withSubstring("$hours$hourString 0$minuteString")),
                isCompletelyDisplayed(),
            ),
        )
    }

    private fun checkDateSingleItem(title: String) {
        checkViewIsDisplayed(
            allOf(
                withId(R.id.containerDateSelectorDay),
                hasDescendant(selectedDateMatcher()),
                hasDescendant(withText(title)),
            ),
        )
    }

    private fun checkDateRangeItem(title: Pair<String, String>) {
        checkViewIsDisplayed(
            allOf(
                withId(R.id.containerDateSelectorRange),
                hasDescendant(selectedDateMatcher()),
                hasDescendant(withText(title.first)),
                hasDescendant(withText(title.second)),
            ),
        )
    }

    private fun toWeekDateTitle(timestamp: Long): Pair<String, String> {
        return toWeekTitle(
            shift = timeMapper.toTimestampShift(
                fromTime = System.currentTimeMillis(),
                toTime = timestamp,
                range = RangeLength.Week,
                firstDayOfWeek = DayOfWeek.SUNDAY,
            ).toInt(),
            firstDayOfWeek = DayOfWeek.SUNDAY,
        )
    }

    private fun toMonthDateTitle(timestamp: Long): String {
        return timeMapper.formatShortMonth(timestamp)
    }

    private fun toYearDateTitle(timestamp: Long): String {
        return calendar.apply {
            timeInMillis = timestamp
        }.get(Calendar.YEAR).toString()
    }
}
