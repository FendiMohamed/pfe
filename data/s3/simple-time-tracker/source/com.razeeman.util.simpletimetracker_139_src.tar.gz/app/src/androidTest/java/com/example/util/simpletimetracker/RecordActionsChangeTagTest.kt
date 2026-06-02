package com.example.util.simpletimetracker

import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.typeTextIntoView
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
class RecordActionsChangeTagTest : BaseUiTest() {

    @Test
    fun visibility() {
        val recordWithTags = "recordWithTags"
        val recordWithNoTags = "recordWithNoTags"
        val runningWithTags = "runningWithTags"
        val runningWithNoTags = "runningWithNoTags"
        val recordTag = "recordTag"
        val runningTag = "runningTag"

        // Setup
        testUtils.addActivity(recordWithTags)
        testUtils.addActivity(recordWithNoTags)
        testUtils.addActivity(runningWithTags)
        testUtils.addActivity(runningWithNoTags)
        testUtils.addRecordTag(recordTag, typeName = recordWithTags)
        testUtils.addRecordTag(runningTag, typeName = runningWithTags)
        testUtils.addRunningRecord(runningWithTags)
        testUtils.addRunningRecord(runningWithNoTags)
        testUtils.addRecord(recordWithTags)
        testUtils.addRecord(recordWithNoTags)
        calendar.timeInMillis = System.currentTimeMillis()
        testUtils.addRecord(
            typeName = recordWithTags,
            timeStarted = calendar.timeInMillis - TimeUnit.DAYS.toMillis(1),
            timeEnded = calendar.timeInMillis - TimeUnit.DAYS.toMillis(1),
        )
        Thread.sleep(1000)

        // Running record with tags - shown
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(runningWithTags), isCompletelyDisplayed()))
        checkViewIsDisplayed(withText(coreR.string.data_edit_change_tag))
        pressBack()

        // Running records with no tags - not shown
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(runningWithNoTags), isCompletelyDisplayed()))
        checkViewDoesNotExist(withText(coreR.string.data_edit_change_tag))
        pressBack()

        // Record with tags - shown
        longClickOnView(allOf(withText(recordWithTags), isCompletelyDisplayed()))
        checkViewIsDisplayed(withText(coreR.string.data_edit_change_tag))
        pressBack()

        // Record with no tags - not shown
        longClickOnView(allOf(withText(recordWithNoTags), isCompletelyDisplayed()))
        checkViewDoesNotExist(withText(coreR.string.data_edit_change_tag))
        pressBack()

        // Untracked - not shown
        longClickOnView(allOf(withText(coreR.string.untracked_time_name), isCompletelyDisplayed()))
        checkViewDoesNotExist(withText(coreR.string.data_edit_change_tag))
    }

    @Test
    fun record() {
        val name1 = "Name1"
        val color1 = firstColor
        val icon1 = firstIcon
        val comment = "Some_comment"
        val tag = "Tag"
        val tagGeneral = "TagGeneral"
        val fullName1 = "$name1 - $tag, $tagGeneral"
        val fullName2 = "$name1 - $tagGeneral"
        val calendar = Calendar.getInstance()

        // Setup
        val current = calendar.timeInMillis
        val difference = TimeUnit.MINUTES.toMillis(30)
        val timeStartedTimestamp = current - difference
        val timeStartedPreview = timeStartedTimestamp.formatTime()
        val timeEndedPreview = current.formatTime()
        val timeRangePreview = difference.formatInterval()

        testUtils.addActivity(name = name1, color = color1, icon = icon1)
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
        clickOnViewWithText(R.string.data_edit_change_tag)
        clickOnViewWithText(tag)
        clickOnViewWithText(R.string.change_record_save)

        tryAction {
            checkRecord(
                name = fullName2,
                color = color1,
                icon = icon1,
                timeStartedPreview = timeStartedPreview,
                timeEndedPreview = timeEndedPreview,
                timeRangePreview = timeRangePreview,
                comment = comment,
            )
        }
    }

    @Test
    fun runningRecord() {
        val name1 = "Name1"
        val color1 = firstColor
        val icon1 = firstIcon
        val comment = "Some_comment"
        val tag = "Tag"
        val tagGeneral = "TagGeneral"
        val fullName1 = "$name1 - $tag, $tagGeneral"
        val fullName2 = "$name1 - $tagGeneral"
        val calendar = Calendar.getInstance()

        // Setup
        val current = calendar.timeInMillis
        val difference = TimeUnit.MINUTES.toMillis(30)
        val timeStartedTimestamp = current - difference
        val timeStartedPreview = timeStartedTimestamp.formatTime()

        testUtils.addActivity(name = name1, color = color1, icon = icon1)
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
        clickOnViewWithText(R.string.data_edit_change_tag)
        clickOnViewWithText(tag)
        clickOnViewWithText(R.string.change_record_save)

        tryAction {
            checkRunningRecord(
                name = fullName2,
                color = color1,
                icon = icon1,
                timeStartedPreview = timeStartedPreview,
                comment = comment,
            )
        }
    }

    @Test
    fun withTagValue() {
        val name1 = "Name1"
        val name2 = "Name2"
        val tag1 = "Tag1"
        val tag2 = "Tag2"
        val value1 = "1"
        val value2 = "2"

        fun checkRecord(name: String) {
            checkViewIsDisplayed(
                allOf(
                    withId(baseR.id.viewRecordItem),
                    hasDescendant(withText(name)),
                    isCompletelyDisplayed(),
                ),
            )
        }

        fun checkRunningRecord(name: String) {
            checkViewIsDisplayed(
                allOf(
                    withId(baseR.id.viewRunningRecordItem),
                    hasDescendant(withText(name)),
                    isCompletelyDisplayed(),
                ),
            )
        }

        // Setup
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addRecordTag(tag1, name1, hasTagValue = true)
        testUtils.addRecordTag(tag2, name2, hasTagValue = true)
        testUtils.addRecord(name1)
        testUtils.addRunningRecord(name2)

        // Change record
        NavUtils.openRecordsScreen()
        checkRecord(name1)
        longClickOnView(allOf(withText(name1), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.data_edit_change_tag)
        clickOnViewWithText(tag1)
        typeTextIntoView(R.id.etCommentItemField, value1)
        closeSoftKeyboard()
        clickOnViewWithText(R.string.duration_dialog_save)
        clickOnViewWithText(R.string.duration_dialog_save)
        tryAction { checkRecord("$name1 - $tag1 ($value1)") }

        // Running record
        checkRunningRecord(name2)
        longClickOnView(allOf(withText(name2), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.data_edit_change_tag)
        clickOnViewWithText(tag2)
        typeTextIntoView(R.id.etCommentItemField, value2)
        closeSoftKeyboard()
        clickOnViewWithText(R.string.duration_dialog_save)
        clickOnViewWithText(R.string.duration_dialog_save)
        tryAction { checkRunningRecord("$name2 - $tag2 ($value2)") }
    }

    @Test
    fun changeMultiselect() {
        val nameTracked = "NameTracked"
        val nameRunning = "NameRunning"
        val tag1 = "Tag1"
        val tag2 = "Tag2"
        val tagGeneral = "TagGeneral"
        val fullNameTracked = "$nameTracked - $tag1"
        val fullNameRunning = "$nameRunning - $tag2"

        testUtils.addActivity(nameTracked)
        testUtils.addActivity(nameRunning)
        testUtils.addRecordTag(tag1, typeName = nameTracked)
        testUtils.addRecordTag(tag2, typeName = nameRunning)
        testUtils.addRecordTag(tagGeneral)
        testUtils.addRecord(nameTracked, tagNames = listOf(tag1))
        testUtils.addRunningRecord(nameRunning, tagNames = listOf(tag2))

        // Check record
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordItem),
                hasDescendant(withText(fullNameTracked)),
                isCompletelyDisplayed(),
            ),
        )
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRunningRecordItem),
                hasDescendant(withText(fullNameRunning)),
                isCompletelyDisplayed(),
            ),
        )

        // Change
        longClickOnView(allOf(withText(fullNameTracked), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(fullNameRunning), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(fullNameRunning), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.data_edit_change_tag)
        checkViewDoesNotExist(withText(tag1))
        checkViewDoesNotExist(withText(tag2))
        clickOnViewWithText(tagGeneral)
        clickOnViewWithText(R.string.change_record_save)

        tryAction {
            checkViewIsDisplayed(
                allOf(
                    withId(baseR.id.viewRecordItem),
                    hasDescendant(withText("$nameTracked - $tagGeneral")),
                    isCompletelyDisplayed(),
                ),
            )
            checkViewIsDisplayed(
                allOf(
                    withId(baseR.id.viewRunningRecordItem),
                    hasDescendant(withText("$nameRunning - $tagGeneral")),
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
