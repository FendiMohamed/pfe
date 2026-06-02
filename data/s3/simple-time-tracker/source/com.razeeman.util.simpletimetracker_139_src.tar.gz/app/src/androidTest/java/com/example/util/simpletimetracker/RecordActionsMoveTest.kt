package com.example.util.simpletimetracker

import android.view.View
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.contrib.PickerActions
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withClassName
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.feature_dialogs.R
import com.example.util.simpletimetracker.feature_dialogs.dateTime.CustomDatePicker
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnCurrentDate
import com.example.util.simpletimetracker.utils.clickOnPrevDate
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithId
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.nestedScrollTo
import com.example.util.simpletimetracker.utils.scrollRecyclerToView
import com.example.util.simpletimetracker.utils.setPickerTime
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.withCardColor
import com.example.util.simpletimetracker.utils.withTag
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.CoreMatchers.equalTo
import org.hamcrest.Matcher
import org.junit.Test
import org.junit.runner.RunWith
import java.util.Calendar
import java.util.concurrent.TimeUnit
import com.example.util.simpletimetracker.core.R as coreR
import com.example.util.simpletimetracker.feature_base_adapter.R as baseR
import com.example.util.simpletimetracker.feature_change_record.R as changeRecordR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RecordActionsMoveTest : BaseUiTest() {

    @Test
    fun moveVisibility() {
        val name = "Name"

        // Setup
        testUtils.addActivity(name)
        testUtils.addRecord(name)
        testUtils.addRunningRecord(name)
        Thread.sleep(1000)

        // Running record - not shown
        tryAction {
            longClickOnView(
                allOf(withId(baseR.id.viewRunningRecordItem), hasDescendant(withText(name)), isCompletelyDisplayed()),
            )
        }
        onView(withText(coreR.string.change_record_actions_hint)).perform(nestedScrollTo())
        clickOnViewWithText(coreR.string.change_record_actions_hint)
        checkViewDoesNotExist(withText(coreR.string.change_record_move))
        pressBack()
        pressBack()

        // Record - shown
        NavUtils.openRecordsScreen()
        clickOnView(
            allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name)), isCompletelyDisplayed()),
        )
        onView(withText(coreR.string.change_record_actions_hint)).perform(nestedScrollTo())
        clickOnViewWithText(coreR.string.change_record_actions_hint)
        scrollRecyclerToView(
            changeRecordR.id.rvChangeRecordAction,
            hasDescendant(withText(coreR.string.change_record_move)),
        )
        checkViewIsDisplayed(withText(coreR.string.change_record_move))
    }

    @Test
    fun moveRecord() {
        val name = "Name"
        val color = firstColor
        val icon = firstIcon
        val comment = "Some_comment"
        val tag = "Tag"
        val fullName = "$name - $tag"
        val calendar = Calendar.getInstance()
            .apply { set(Calendar.HOUR_OF_DAY, 12) }

        // Setup
        var current = calendar.timeInMillis
        val difference = TimeUnit.MINUTES.toMillis(30)
        var timeStartedTimestamp = current - difference
        var timeStartedPreview = timeStartedTimestamp.formatTime()
        var timeEndedPreview = current.formatTime()
        var timeRangePreview = difference.formatInterval()

        testUtils.addActivity(name = name, color = color, icon = icon)
        testUtils.addRecordTag(tag)
        testUtils.addRecord(
            typeName = name,
            timeStarted = timeStartedTimestamp,
            timeEnded = current,
            tagNames = listOf(tag),
            comment = comment,
        )

        // Check record
        NavUtils.openRecordsScreen()
        checkRecord(
            name = fullName,
            timeStartedPreview = timeStartedPreview,
            timeEndedPreview = timeEndedPreview,
            timeRangePreview = timeRangePreview,
            comment = comment,
        )

        // Move time
        clickOnViewWithText(fullName)
        onView(withText(coreR.string.change_record_actions_hint)).perform(nestedScrollTo())
        clickOnViewWithText(coreR.string.change_record_actions_hint)
        scrollRecyclerToView(
            changeRecordR.id.rvChangeRecordAction,
            hasDescendant(withText(coreR.string.change_record_move)),
        )
        clickOnViewWithText(coreR.string.change_record_move)
        setPickerTime(9, 15)
        clickOnViewWithId(R.id.btnDateTimeDialogPositive)

        // Check
        current = calendar.apply {
            set(Calendar.HOUR_OF_DAY, 9)
            set(Calendar.MINUTE, 15)
        }.timeInMillis
        timeStartedTimestamp = current
        val timeEndedTimestamp = current + difference
        timeStartedPreview = timeStartedTimestamp.formatTime()
        timeEndedPreview = timeEndedTimestamp.formatTime()
        timeRangePreview = difference.formatInterval()
        tryAction {
            checkRecord(
                name = fullName,
                timeStartedPreview = timeStartedPreview,
                timeEndedPreview = timeEndedPreview,
                timeRangePreview = timeRangePreview,
                comment = comment,
            )
        }

        // Move date
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH) - 1

        clickOnViewWithText(fullName)
        onView(withText(coreR.string.change_record_actions_hint)).perform(nestedScrollTo())
        clickOnViewWithText(coreR.string.change_record_actions_hint)
        scrollRecyclerToView(
            changeRecordR.id.rvChangeRecordAction,
            hasDescendant(withText(coreR.string.change_record_move)),
        )
        clickOnViewWithText(coreR.string.change_record_move)
        clickOnViewWithText(coreR.string.date_time_dialog_date)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name)))
            .perform(PickerActions.setDate(year, month + 1, day))
        clickOnViewWithId(R.id.btnDateTimeDialogPositive)

        // Check
        tryAction {
            checkViewDoesNotExist(
                allOf(
                    withId(baseR.id.viewRecordItem),
                    hasDescendant(withText(fullName)),
                    isCompletelyDisplayed(),
                ),
            )
        }
        clickOnPrevDate()
        tryAction {
            checkRecord(
                name = fullName,
                timeStartedPreview = timeStartedPreview,
                timeEndedPreview = timeEndedPreview,
                timeRangePreview = timeRangePreview,
                comment = comment,
            )
        }
    }

    @Test
    fun moveFromQuickActions() {
        val name = "Name"

        // Setup
        testUtils.addActivity(name)
        testUtils.addRecord(name)

        // Check record
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(getRecordMatcher(name))

        // Move
        longClickOnView(allOf(withText(name), isCompletelyDisplayed()))
        clickOnViewWithText(coreR.string.change_record_move)
        val calendar = Calendar.getInstance()
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH) - 1
        clickOnViewWithText(coreR.string.date_time_dialog_date)
        onView(withClassName(equalTo(CustomDatePicker::class.java.name)))
            .perform(PickerActions.setDate(year, month + 1, day))
        clickOnViewWithId(R.id.btnDateTimeDialogPositive)

        // Check
        tryAction { checkViewDoesNotExist(getRecordMatcher(name)) }
        clickOnPrevDate()
        tryAction { checkViewIsDisplayed(getRecordMatcher(name)) }
    }

    @Test
    fun moveMultiselectFromQuickActions() {
        val name1 = "Name1"
        val name2 = "Name2"

        // Setup
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addRecord(name1)
        testUtils.addRecord(name2)

        // Check record
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(getRecordMatcher(name1))
        checkViewIsDisplayed(getRecordMatcher(name2))

        // Move
        longClickOnView(allOf(withText(name1), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(name2), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(name2), isCompletelyDisplayed()))
        clickOnViewWithText(coreR.string.change_record_move)
        val calendar = Calendar.getInstance()
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH) - 1
        onView(withClassName(equalTo(CustomDatePicker::class.java.name)))
            .perform(PickerActions.setDate(year, month + 1, day))
        clickOnViewWithId(R.id.btnDateTimeDialogPositive)

        // Check
        tryAction { checkViewDoesNotExist(getRecordMatcher(name1)) }
        tryAction { checkViewDoesNotExist(getRecordMatcher(name2)) }
        clickOnCurrentDate(-1)
        tryAction { checkViewIsDisplayed(getRecordMatcher(name1)) }
        tryAction { checkViewIsDisplayed(getRecordMatcher(name2)) }
    }

    private fun getRecordMatcher(type: String): Matcher<View> {
        return allOf(
            withId(baseR.id.viewRecordItem),
            hasDescendant(withText(type)),
            isCompletelyDisplayed(),
        )
    }

    @Suppress("SameParameterValue")
    private fun checkRecord(
        name: String,
        timeStartedPreview: String,
        timeEndedPreview: String,
        timeRangePreview: String,
        comment: String,
    ) {
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordItem),
                withCardColor(firstColor),
                hasDescendant(withText(name)),
                hasDescendant(withTag(firstIcon)),
                hasDescendant(withText(timeStartedPreview)),
                hasDescendant(withText(timeEndedPreview)),
                hasDescendant(withText(timeRangePreview)),
                hasDescendant(withText(comment)),
                isCompletelyDisplayed(),
            ),
        )
    }
}
