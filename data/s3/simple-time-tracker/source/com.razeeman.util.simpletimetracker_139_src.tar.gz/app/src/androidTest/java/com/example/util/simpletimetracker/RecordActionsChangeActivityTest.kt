package com.example.util.simpletimetracker

import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.core.extension.setToStartOfDay
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.nthChildOf
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.withCardColor
import com.example.util.simpletimetracker.utils.withTag
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.CoreMatchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import java.util.Calendar
import java.util.concurrent.TimeUnit
import com.example.util.simpletimetracker.core.R as coreR
import com.example.util.simpletimetracker.feature_base_adapter.R as baseR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RecordActionsChangeActivityTest : BaseUiTest() {

    @Test
    fun visibility() {
        val name1 = "Name1"
        val name2 = "Name2"

        // Setup
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addRecord(name1)
        calendar.timeInMillis = System.currentTimeMillis()
        testUtils.addRecord(
            typeName = name1,
            timeStarted = calendar.timeInMillis - TimeUnit.DAYS.toMillis(1),
            timeEnded = calendar.timeInMillis - TimeUnit.DAYS.toMillis(1),
        )
        testUtils.addRunningRecord(name2)
        Thread.sleep(1000)

        // Running record - shown
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(name2), isCompletelyDisplayed()))
        checkViewIsDisplayed(withText(coreR.string.data_edit_change_activity))
        pressBack()

        // Record - shown
        longClickOnView(allOf(withText(name1), isCompletelyDisplayed()))
        checkViewIsDisplayed(withText(coreR.string.data_edit_change_activity))
        pressBack()

        // Untracked - shown
        longClickOnView(allOf(withText(coreR.string.untracked_time_name), isCompletelyDisplayed()))
        checkViewIsDisplayed(withText(coreR.string.data_edit_change_activity))
    }

    @Test
    fun record() {
        val name1 = "Name1"
        val name2 = "Name2"
        val color1 = firstColor
        val color2 = lastColor
        val icon1 = firstIcon
        val icon2 = lastIcon
        val comment = "Some_comment"
        val tag = "Tag"
        val tagGeneral = "TagGeneral"
        val fullName1 = "$name1 - $tag, $tagGeneral"
        val fullName2 = "$name2 - $tagGeneral"
        val calendar = Calendar.getInstance()

        // Setup
        val current = calendar.timeInMillis
        val difference = TimeUnit.MINUTES.toMillis(30)
        val timeStartedTimestamp = current - difference
        val timeStartedPreview = timeStartedTimestamp.formatTime()
        val timeEndedPreview = current.formatTime()
        val timeRangePreview = difference.formatInterval()

        testUtils.addActivity(name = name1, color = color1, icon = icon1)
        testUtils.addActivity(name = name2, color = color2, icon = icon2)
        testUtils.addRecordTag(tag, typeName = name1)
        testUtils.addRecordTag(tagGeneral)
        testUtils.addRecord(
            typeName = name1,
            timeStarted = timeStartedTimestamp,
            timeEnded = current,
            tagNames = listOf(tag, tagGeneral),
            comment = comment,
        )

        // Check record
        NavUtils.openRecordsScreen()
        checkRecord(
            name = fullName1,
            color = color1,
            icon = icon1,
            timeStartedPreview = timeStartedPreview,
            timeEndedPreview = timeEndedPreview,
            timeRangePreview = timeRangePreview,
            comment = comment,
        )

        // Change
        longClickOnView(allOf(withText(fullName1), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.data_edit_change_activity)
        clickOnViewWithText(name2)

        tryAction {
            checkRecord(
                name = fullName2,
                color = color2,
                icon = icon2,
                timeStartedPreview = timeStartedPreview,
                timeEndedPreview = timeEndedPreview,
                timeRangePreview = timeRangePreview,
                comment = comment,
            )
        }
    }

    @Test
    fun untrackedRecord() {
        val name1 = "Name1"
        val color1 = firstColor
        val icon1 = firstIcon
        val calendar = Calendar.getInstance()

        // Setup
        testUtils.addActivity(name = name1, color = color1, icon = icon1)
        val current = calendar.timeInMillis
        val yesterday = current - TimeUnit.DAYS.toMillis(1)
        testUtils.addRecord(typeName = name1, timeStarted = yesterday, timeEnded = yesterday)

        val startOfDay = calendar.apply { setToStartOfDay() }.timeInMillis
        val timeStartedPreview = startOfDay.formatTime()
        val timeEndedPreview = current.formatTime()
        val difference = current - startOfDay
        val timeRangePreview = difference.formatInterval()

        // Check record
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordItem),
                hasDescendant(withText(coreR.string.untracked_time_name)),
                hasDescendant(withText(timeStartedPreview)),
                hasDescendant(withText(timeEndedPreview)),
                hasDescendant(withText(timeRangePreview)),
                isCompletelyDisplayed(),
            ),
        )

        // Change
        longClickOnView(withText(coreR.string.untracked_time_name))
        clickOnViewWithText(R.string.data_edit_change_activity)
        clickOnViewWithText(name1)

        tryAction {
            checkRecord(
                name = name1,
                color = color1,
                icon = icon1,
                timeStartedPreview = timeStartedPreview,
                timeEndedPreview = timeEndedPreview,
                timeRangePreview = timeRangePreview,
                comment = "",
            )
        }
    }

    @Test
    fun runningRecord() {
        val name1 = "Name1"
        val name2 = "Name2"
        val color1 = firstColor
        val color2 = lastColor
        val icon1 = firstIcon
        val icon2 = lastIcon
        val comment = "Some_comment"
        val tag = "Tag"
        val tagGeneral = "TagGeneral"
        val fullName1 = "$name1 - $tag, $tagGeneral"
        val fullName2 = "$name2 - $tagGeneral"
        val calendar = Calendar.getInstance()

        // Setup
        val current = calendar.timeInMillis
        val difference = TimeUnit.MINUTES.toMillis(30)
        val timeStartedTimestamp = current - difference
        val timeStartedPreview = timeStartedTimestamp.formatTime()

        testUtils.addActivity(name = name1, color = color1, icon = icon1)
        testUtils.addActivity(name = name2, color = color2, icon = icon2)
        testUtils.addRecordTag(tag, typeName = name1)
        testUtils.addRecordTag(tagGeneral)
        testUtils.addRunningRecord(
            typeName = name1,
            timeStarted = timeStartedTimestamp,
            tagNames = listOf(tag, tagGeneral),
            comment = comment,
        )

        // Check record
        NavUtils.openRecordsScreen()
        checkRunningRecord(
            name = fullName1,
            color = color1,
            icon = icon1,
            timeStartedPreview = timeStartedPreview,
            comment = comment,
        )

        // Change
        longClickOnView(allOf(withText(fullName1), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.data_edit_change_activity)
        clickOnViewWithText(name2)

        tryAction {
            checkRunningRecord(
                name = fullName2,
                color = color2,
                icon = icon2,
                timeStartedPreview = timeStartedPreview,
                comment = comment,
            )
        }
    }

    @Test
    fun changeMultiselect() {
        val name1 = "Name1"
        val name2 = "Name2"
        val name3 = "Name3"
        val calendar = Calendar.getInstance()

        // Setup
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addActivity(name3)

        testUtils.addRunningRecord(name1)
        testUtils.addRecord(
            typeName = name2,
            timeStarted = calendar.timeInMillis - TimeUnit.MINUTES.toMillis(3),
            timeEnded = calendar.timeInMillis - TimeUnit.MINUTES.toMillis(2),
        )

        // Check
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRunningRecordItem),
                hasDescendant(withText(name1)),
                nthChildOf(withId(R.id.rvRecordsList), 0),
                isCompletelyDisplayed(),
            ),
        )
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordItem),
                hasDescendant(withText(R.string.untracked_time_name)),
                nthChildOf(withId(R.id.rvRecordsList), 1),
                isCompletelyDisplayed(),
            ),
        )
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordItem),
                hasDescendant(withText(name2)),
                nthChildOf(withId(R.id.rvRecordsList), 2),
                isCompletelyDisplayed(),
            ),
        )

        // Change
        longClickOnView(allOf(withText(name1), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(name2), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(R.string.untracked_time_name), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(R.string.untracked_time_name), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.data_edit_change_activity)
        clickOnViewWithText(name3)

        tryAction {
            checkViewIsDisplayed(
                allOf(
                    withId(baseR.id.viewRunningRecordItem),
                    hasDescendant(withText(name3)),
                    nthChildOf(withId(R.id.rvRecordsList), 0),
                    isCompletelyDisplayed(),
                ),
            )
            checkViewIsDisplayed(
                allOf(
                    withId(baseR.id.viewRecordItem),
                    hasDescendant(withText(name3)),
                    nthChildOf(withId(R.id.rvRecordsList), 1),
                    isCompletelyDisplayed(),
                ),
            )
            checkViewIsDisplayed(
                allOf(
                    withId(baseR.id.viewRecordItem),
                    hasDescendant(withText(name3)),
                    nthChildOf(withId(R.id.rvRecordsList), 2),
                    isCompletelyDisplayed(),
                ),
            )
        }
    }

    @Suppress("SameParameterValue")
    private fun checkRecord(
        name: String,
        color: Int,
        icon: Int,
        timeStartedPreview: String,
        timeEndedPreview: String,
        timeRangePreview: String,
        comment: String,
    ) {
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordItem),
                withCardColor(color),
                hasDescendant(withText(name)),
                hasDescendant(withTag(icon)),
                hasDescendant(withText(timeStartedPreview)),
                hasDescendant(withText(timeEndedPreview)),
                hasDescendant(withText(timeRangePreview)),
                hasDescendant(withText(comment)),
                isCompletelyDisplayed(),
            ),
        )
    }

    @Suppress("SameParameterValue")
    private fun checkRunningRecord(
        name: String,
        color: Int,
        icon: Int,
        timeStartedPreview: String,
        comment: String,
    ) {
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRunningRecordItem),
                withCardColor(color),
                hasDescendant(withText(name)),
                hasDescendant(withTag(icon)),
                hasDescendant(withText(timeStartedPreview)),
                hasDescendant(withText(comment)),
                isCompletelyDisplayed(),
            ),
        )
    }
}
