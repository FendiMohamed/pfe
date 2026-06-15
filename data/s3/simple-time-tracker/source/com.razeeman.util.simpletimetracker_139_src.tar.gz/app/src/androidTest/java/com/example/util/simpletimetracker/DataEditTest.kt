package com.example.util.simpletimetracker

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.swipeUp
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isChecked
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.isDescendantOfA
import androidx.test.espresso.matcher.ViewMatchers.isEnabled
import androidx.test.espresso.matcher.ViewMatchers.isNotChecked
import androidx.test.espresso.matcher.ViewMatchers.isNotEnabled
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withSubstring
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.core.extension.setToStartOfDay
import com.example.util.simpletimetracker.core.extension.setWeekToFirstDay
import com.example.util.simpletimetracker.feature_base_adapter.R
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnCurrentDate
import com.example.util.simpletimetracker.utils.clickOnPrevDate
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithId
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.nestedScrollTo
import com.example.util.simpletimetracker.utils.nthChildOf
import com.example.util.simpletimetracker.utils.recyclerItemCount
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
import com.example.util.simpletimetracker.feature_data_edit.R as dataEditR
import com.example.util.simpletimetracker.feature_records.R as recordsR
import com.example.util.simpletimetracker.feature_records_filter.R as recordsFilterR

@Suppress("SameParameterValue")
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class DataEditTest : BaseUiTest() {

    @Test
    fun changeButtonState() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"

        // Add data
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addRecord(name1)

        // Check
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))

        onView(withId(dataEditR.id.checkboxDataEditChangeActivity))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(name2)
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))

        onView(withText(coreR.string.data_edit_select_records))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(coreR.string.activity_hint)
        clickOnView(allOf(isDescendantOfA(withId(R.id.viewRecordTypeItem)), withText(name2)))
        pressBack()
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))

        onView(withText(coreR.string.data_edit_select_records))
            .perform(nestedScrollTo(), click())
        clickOnView(allOf(isDescendantOfA(withId(R.id.viewRecordTypeItem)), withText(name1)))
        pressBack()
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isEnabled()))

        onView(withId(dataEditR.id.checkboxDataEditChangeActivity))
            .perform(nestedScrollTo(), click())
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
    }

    @Test
    fun changeType() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"
        val comment1 = "comment1"
        val comment2 = "comment2"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val tag3 = "tag3"

        // Add data
        testUtils.addActivity(name1, color = firstColor, icon = firstIcon)
        testUtils.addActivity(name2, color = lastColor, icon = lastIcon)

        testUtils.addRecordTag(tag1, name1)
        testUtils.addRecordTag(tag2, name2)
        testUtils.addRecordTag(tag3)

        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)

        // Check before
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = "$name1 - $tag1, $tag3",
            color = firstColor,
            icon = firstIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        clickOnViewWithText(coreR.string.data_edit_select_records)
        clickOnViewWithText(coreR.string.activity_hint)
        clickOnView(allOf(isDescendantOfA(withId(R.id.viewRecordTypeItem)), withText(name1)))
        pressBack()

        // Check
        checkViewIsDisplayed(
            allOf(withId(dataEditR.id.tvDataEditSelectedRecords), withSubstring("2")),
        )
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity))
            .perform(nestedScrollTo()).check(matches(isNotChecked()))
        clickOnViewWithId(dataEditR.id.checkboxDataEditChangeActivity)
        pressBack()
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity))
            .perform(nestedScrollTo()).check(matches(isNotChecked()))

        // Change
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(name2)
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity))
            .perform(nestedScrollTo()).check(matches(isChecked()))
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo())
        onView(withId(dataEditR.id.nsvDataEdit))
            .perform(swipeUp())
        onView(withText(coreR.string.data_edit_button_change))
            .perform(click())
        clickOnViewWithText(coreR.string.ok)
        Thread.sleep(1000)

        // Check
        checkViewIsDisplayed(
            allOf(
                withText(coreR.string.data_edit_success_message),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = "$name2 - $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )
    }

    @Test
    fun changeComment() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"
        val comment1 = "comment1"
        val comment2 = "comment2"
        val comment3 = "comment3"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val tag3 = "tag3"

        // Add data
        testUtils.addActivity(name1, color = firstColor, icon = firstIcon)
        testUtils.addActivity(name2, color = lastColor, icon = lastIcon)

        testUtils.addRecordTag(tag1, name1)
        testUtils.addRecordTag(tag2, name2)
        testUtils.addRecordTag(tag3)

        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)

        // Check before
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = "$name1 - $tag1, $tag3",
            color = firstColor,
            icon = firstIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        clickOnViewWithText(coreR.string.data_edit_select_records)
        clickOnViewWithText(coreR.string.activity_hint)
        clickOnView(allOf(isDescendantOfA(withId(R.id.viewRecordTypeItem)), withText(name1)))
        pressBack()

        // Check
        checkViewIsDisplayed(
            allOf(withId(dataEditR.id.tvDataEditSelectedRecords), withSubstring("2")),
        )
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditChangeComment))
            .perform(nestedScrollTo()).check(matches(isNotChecked()))

        // Change
        onView(withId(dataEditR.id.checkboxDataEditChangeComment))
            .perform(nestedScrollTo(), click())
        typeTextIntoView(dataEditR.id.etDataEditChangeComment, comment3)
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditChangeComment))
            .perform(nestedScrollTo()).check(matches(isChecked()))
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(coreR.string.ok)
        Thread.sleep(1000)

        // Check
        checkViewIsDisplayed(
            allOf(
                withText(coreR.string.data_edit_success_message),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = "$name1 - $tag1, $tag3",
            color = firstColor,
            icon = firstIcon,
            comment = comment3,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )
    }

    @Test
    fun addTags() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"
        val comment1 = "comment1"
        val comment2 = "comment2"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val tag3 = "tag3"

        // Add data
        testUtils.addActivity(name1, color = firstColor, icon = firstIcon)
        testUtils.addActivity(name2, color = lastColor, icon = lastIcon)

        testUtils.addRecordTag(tag1, name1)
        testUtils.addRecordTag(tag2, name2)
        testUtils.addRecordTag(tag3)

        testUtils.addRecord(name1, comment = comment1)
        testUtils.addRecord(name1, comment = comment1)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)

        // Check before
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = name1,
            color = firstColor,
            icon = firstIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        clickOnViewWithText(coreR.string.data_edit_select_records)
        clickOnViewWithText(coreR.string.activity_hint)
        clickOnView(allOf(isDescendantOfA(withId(R.id.viewRecordTypeItem)), withText(name1)))
        pressBack()

        // Check
        checkViewIsDisplayed(
            allOf(withId(dataEditR.id.tvDataEditSelectedRecords), withSubstring("2")),
        )
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditAddTag))
            .perform(nestedScrollTo()).check(matches(isNotChecked()))
        clickOnViewWithId(dataEditR.id.checkboxDataEditAddTag)
        pressBack()
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditAddTag))
            .perform(nestedScrollTo()).check(matches(isNotChecked()))

        // Change
        onView(withId(dataEditR.id.checkboxDataEditAddTag))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(tag1)
        clickOnViewWithText(tag3)
        clickOnViewWithText(coreR.string.records_filter_select)
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditAddTag))
            .perform(nestedScrollTo()).check(matches(isChecked()))
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(coreR.string.ok)
        Thread.sleep(1000)

        // Check
        checkViewIsDisplayed(
            allOf(
                withText(coreR.string.data_edit_success_message),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = "$name1 - $tag1, $tag3",
            color = firstColor,
            icon = firstIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )
    }

    @Test
    fun removeTags() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"
        val comment1 = "comment1"
        val comment2 = "comment2"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val tag3 = "tag3"

        // Add data
        testUtils.addActivity(name1, color = firstColor, icon = firstIcon)
        testUtils.addActivity(name2, color = lastColor, icon = lastIcon)

        testUtils.addRecordTag(tag1, name1)
        testUtils.addRecordTag(tag2, name2)
        testUtils.addRecordTag(tag3)

        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)

        // Check before
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = "$name1 - $tag1, $tag3",
            color = firstColor,
            icon = firstIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        clickOnViewWithText(coreR.string.data_edit_select_records)
        clickOnViewWithText(coreR.string.activity_hint)
        clickOnView(allOf(isDescendantOfA(withId(R.id.viewRecordTypeItem)), withText(name1)))
        pressBack()

        // Check
        checkViewIsDisplayed(
            allOf(withId(dataEditR.id.tvDataEditSelectedRecords), withSubstring("2")),
        )
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag))
            .perform(nestedScrollTo()).check(matches(isNotChecked()))
        clickOnViewWithId(dataEditR.id.checkboxDataEditRemoveTag)
        pressBack()
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag))
            .perform(nestedScrollTo()).check(matches(isNotChecked()))

        // Change
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(tag1)
        clickOnViewWithText(tag3)
        clickOnViewWithText(coreR.string.records_filter_select)
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag))
            .perform(nestedScrollTo()).check(matches(isChecked()))
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(coreR.string.ok)
        Thread.sleep(1000)

        // Check
        checkViewIsDisplayed(
            allOf(
                withText(coreR.string.data_edit_success_message),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = name1,
            color = firstColor,
            icon = firstIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )
    }

    @Test
    fun delete() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"
        val comment1 = "comment1"
        val comment2 = "comment2"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val tag3 = "tag3"

        // Add data
        testUtils.addActivity(name1, color = firstColor, icon = firstIcon)
        testUtils.addActivity(name2, color = lastColor, icon = lastIcon)

        testUtils.addRecordTag(tag1, name1)
        testUtils.addRecordTag(tag2, name2)
        testUtils.addRecordTag(tag3)

        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name1, tagNames = listOf(tag1, tag3), comment = comment1)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)
        testUtils.addRecord(name2, tagNames = listOf(tag2, tag3), comment = comment2)

        // Check before
        NavUtils.openRecordsScreen()
        checkRecord(
            indexes = listOf(0, 1),
            name = "$name1 - $tag1, $tag3",
            color = firstColor,
            icon = firstIcon,
            comment = comment1,
        )
        checkRecord(
            indexes = listOf(2, 3, 4),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        clickOnViewWithText(coreR.string.data_edit_select_records)
        clickOnViewWithText(coreR.string.activity_hint)
        clickOnView(allOf(isDescendantOfA(withId(R.id.viewRecordTypeItem)), withText(name1)))
        pressBack()

        // Check
        checkViewIsDisplayed(
            allOf(withId(dataEditR.id.tvDataEditSelectedRecords), withSubstring("2")),
        )
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isNotEnabled()))

        // Select other changes
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(name2)
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity)).check(matches(isChecked()))

        onView(withId(dataEditR.id.checkboxDataEditChangeComment))
            .perform(nestedScrollTo(), click())
        typeTextIntoView(dataEditR.id.etDataEditChangeComment, "temp")
        onView(withId(dataEditR.id.checkboxDataEditChangeComment)).check(matches(isChecked()))

        onView(withId(dataEditR.id.checkboxDataEditAddTag))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(tag2)
        clickOnViewWithText(coreR.string.records_filter_select)
        onView(withId(dataEditR.id.checkboxDataEditAddTag)).check(matches(isChecked()))

        onView(withId(dataEditR.id.checkboxDataEditRemoveTag))
            .perform(nestedScrollTo())
        onView(withId(dataEditR.id.nsvDataEdit))
            .perform(swipeUp())
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag))
            .perform(click())
        clickOnViewWithText(tag3)
        clickOnViewWithText(coreR.string.records_filter_select)
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag)).check(matches(isChecked()))

        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditDeleteRecords))
            .perform(nestedScrollTo(), click())

        // Other changes is reset
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity)).perform(nestedScrollTo())
        onView(withId(dataEditR.id.checkboxDataEditChangeActivity)).check(matches(isNotChecked()))
        onView(withId(dataEditR.id.checkboxDataEditChangeComment)).perform(nestedScrollTo())
        onView(withId(dataEditR.id.checkboxDataEditChangeComment)).check(matches(isNotChecked()))
        onView(withId(dataEditR.id.checkboxDataEditAddTag)).perform(nestedScrollTo())
        onView(withId(dataEditR.id.checkboxDataEditAddTag)).check(matches(isNotChecked()))
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag)).perform(nestedScrollTo())
        onView(withId(dataEditR.id.checkboxDataEditRemoveTag)).check(matches(isNotChecked()))

        // Change
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo()).check(matches(isEnabled()))
        onView(withId(dataEditR.id.checkboxDataEditDeleteRecords)).perform(nestedScrollTo())
        onView(withId(dataEditR.id.checkboxDataEditDeleteRecords)).check(matches(isChecked()))
        onView(withText(coreR.string.data_edit_button_change))
            .perform(nestedScrollTo(), click())
        clickOnViewWithText(coreR.string.ok)
        Thread.sleep(1000)

        // Check
        checkViewIsDisplayed(
            allOf(
                withText(coreR.string.data_edit_success_message),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )
        NavUtils.openRecordsScreen()
        onView(allOf(withId(recordsR.id.rvRecordsList), isCompletelyDisplayed()))
            .check(recyclerItemCount(4))
        checkRecord(
            indexes = listOf(0, 1, 2),
            name = "$name2 - $tag2, $tag3",
            color = lastColor,
            icon = lastIcon,
            comment = comment2,
        )
    }

    @Test
    fun deleteAllToday() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"
        val name3 = "TypeName3"

        // Add data
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addActivity(name3)
        val timeToday = calendar.apply { set(Calendar.HOUR_OF_DAY, 15) }.timeInMillis
        testUtils.addRecord(typeName = name1, timeStarted = timeToday, timeEnded = timeToday)
        testUtils.addRecord(typeName = name2, timeStarted = timeToday, timeEnded = timeToday)
        testUtils.addRecord(
            typeName = name3,
            timeStarted = timeToday - TimeUnit.DAYS.toMillis(1),
            timeEnded = timeToday - TimeUnit.DAYS.toMillis(1),
        )

        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name1))))
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name2))))
        clickOnCurrentDate(-1)
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name3))))
        clickOnCurrentDate(-2)

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        onView(
            allOf(
                withSubstring(getString(R.string.archive_dialog_delete)),
                withSubstring(getString(R.string.title_today)),
                withSubstring("2"),
                withSubstring(getQuantityString(R.plurals.statistics_detail_times_tracked, 2)),
            ),
        ).perform(nestedScrollTo())
        onView(withId(dataEditR.id.nsvDataEdit)).perform(swipeUp())

        // Check filter
        clickOnViewWithId(dataEditR.id.btnDataEditDeleteTodayRecordsView)
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterTitle), withSubstring("2")))
        pressBack()

        // Delete
        clickOnViewWithId(dataEditR.id.btnDataEditDeleteTodayRecords)
        clickOnViewWithText(coreR.string.ok)
        clickOnView(
            allOf(
                withText(coreR.string.data_edit_success_message),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )

        // Check
        NavUtils.openRecordsScreen()
        checkViewDoesNotExist(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name1))))
        checkViewDoesNotExist(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name2))))
        clickOnPrevDate()
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name3))))
    }

    @Test
    fun deleteAllRecords() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"

        // Add data
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addRecord(name1)
        testUtils.addRecord(name2)
        Thread.sleep(1000)

        // Check before
        tryAction { checkViewIsDisplayed(allOf(withId(R.id.viewRecordTypeItem), hasDescendant(withText(name1)))) }
        checkViewIsDisplayed(allOf(withId(R.id.viewRecordTypeItem), hasDescendant(withText(name2))))
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name1))))
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name2))))

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        onView(withText(R.string.data_edit_button_delete_records)).perform(nestedScrollTo())
        onView(withId(dataEditR.id.nsvDataEdit)).perform(swipeUp())
        onView(withText(R.string.data_edit_button_delete_records)).perform(click())
        clickOnViewWithText(coreR.string.ok)

        // Check
        NavUtils.openRunningRecordsScreen()
        checkViewIsDisplayed(allOf(withId(R.id.viewRecordTypeItem), hasDescendant(withText(name1))))
        checkViewIsDisplayed(allOf(withId(R.id.viewRecordTypeItem), hasDescendant(withText(name2))))
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(withSubstring(getString(R.string.no_records_exist)))
    }

    @Test
    fun deleteAllData() {
        val name1 = "TypeName1"
        val name2 = "TypeName2"

        // Add data
        testUtils.addActivity(name1)
        testUtils.addActivity(name2)
        testUtils.addRecord(name1)
        testUtils.addRecord(name2)
        Thread.sleep(1000)

        // Check before
        tryAction { checkViewIsDisplayed(allOf(withId(R.id.viewRecordTypeItem), hasDescendant(withText(name1)))) }
        checkViewIsDisplayed(allOf(withId(R.id.viewRecordTypeItem), hasDescendant(withText(name2))))
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name1))))
        checkViewIsDisplayed(allOf(withId(baseR.id.viewRecordItem), hasDescendant(withText(name2))))

        // Select
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        onView(withText(R.string.data_edit_button_delete_data))
            .perform(nestedScrollTo())
        onView(withId(dataEditR.id.nsvDataEdit))
            .perform(swipeUp())
        onView(withText(R.string.data_edit_button_delete_data))
            .perform(click())
        clickOnViewWithText(coreR.string.ok)

        // Check
        NavUtils.openRunningRecordsScreen()
        checkViewIsDisplayed(
            withText(
                getString(
                    R.string.running_records_types_empty,
                    getString(R.string.running_records_add_type),
                    getString(R.string.running_records_add_default),
                ),
            ),
        )
        NavUtils.openRecordsScreen()
        checkViewIsDisplayed(withSubstring(getString(R.string.no_records_exist)))
    }

    @Test
    fun selectByDate() {
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        clickOnViewWithText(coreR.string.data_edit_select_records)
        clickOnViewWithText(coreR.string.date_time_dialog_date)

        // Check ranges
        clickOnViewWithText(R.string.title_today)
        var calendar = Calendar.getInstance().apply {
            timeInMillis = System.currentTimeMillis()
            setToStartOfDay()
        }
        var timeStarted = calendar.timeInMillis.formatDateTimeYear()
        var timeEnded = (calendar.timeInMillis + TimeUnit.DAYS.toMillis(1)).formatDateTimeYear()
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeEnded), withText(timeEnded)))

        clickOnViewWithText(R.string.title_this_week)
        calendar = Calendar.getInstance().apply {
            timeInMillis = System.currentTimeMillis()
            setToStartOfDay()
            setWeekToFirstDay()
        }
        timeStarted = calendar.timeInMillis.formatDateTimeYear()
        timeEnded = (calendar.timeInMillis + TimeUnit.DAYS.toMillis(7)).formatDateTimeYear()
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeEnded), withText(timeEnded)))

        clickOnViewWithText(R.string.title_this_month)
        calendar = Calendar.getInstance().apply {
            timeInMillis = System.currentTimeMillis()
            setToStartOfDay()
            set(Calendar.DAY_OF_MONTH, 1)
        }
        timeStarted = calendar.timeInMillis.formatDateTimeYear()
        calendar.apply {
            add(Calendar.MONTH, 1)
        }
        timeEnded = calendar.timeInMillis.formatDateTimeYear()
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeEnded), withText(timeEnded)))

        clickOnViewWithText(R.string.title_this_year)
        calendar = Calendar.getInstance().apply {
            timeInMillis = System.currentTimeMillis()
            setToStartOfDay()
            set(Calendar.DAY_OF_YEAR, 1)
        }
        timeStarted = calendar.timeInMillis.formatDateTimeYear()
        calendar.apply {
            add(Calendar.YEAR, 1)
        }
        timeEnded = calendar.timeInMillis.formatDateTimeYear()
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeEnded), withText(timeEnded)))

        clickOnViewWithText(R.string.range_overall)
        calendar = Calendar.getInstance().apply {
            timeInMillis = 0
        }
        timeStarted = calendar.timeInMillis.formatDateTimeYear()
        calendar.apply {
            timeInMillis = System.currentTimeMillis()
        }
        timeEnded = calendar.timeInMillis.formatDateTimeYear()
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeEnded), withText(timeEnded)))

        clickOnViewWithText(getQuantityString(R.plurals.range_last, 7, 7))
        calendar = Calendar.getInstance().apply {
            timeInMillis = System.currentTimeMillis()
            setToStartOfDay()
        }
        timeStarted = (calendar.timeInMillis - TimeUnit.DAYS.toMillis(6)).formatDateTimeYear()
        timeEnded = (calendar.timeInMillis + TimeUnit.DAYS.toMillis(1)).formatDateTimeYear()
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeEnded), withText(timeEnded)))

        clickOnView(allOf(isDescendantOfA(withId(R.id.viewFilterItem)), withText(R.string.range_custom)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeStarted), withText(timeStarted)))
        checkViewIsDisplayed(allOf(withId(recordsFilterR.id.tvRecordsFilterRangeTimeEnded), withText(timeEnded)))
    }

    @Test
    fun duplicate() {
        val type = "type"

        // Add data
        testUtils.addActivity(
            name = type,
            color = firstColor,
            icon = firstIcon,
            goals = listOf(GoalsTestUtils.getDailyDurationGoal(TimeUnit.MINUTES.toSeconds(1))),
        )

        // Duplicate
        NavUtils.openSettingsScreen()
        NavUtils.openDataEditScreen()
        onView(withText(coreR.string.change_record_duplicate)).perform(nestedScrollTo())
        clickOnViewWithText(coreR.string.change_record_duplicate)
        clickOnViewWithText(type)
        clickOnViewWithText(R.string.ok)

        // Check
        tryAction {
            checkViewIsDisplayed(
                allOf(
                    withId(coreR.id.viewRecordTypeItem),
                    hasDescendant(withText(type)),
                    hasDescendant(withTag(firstIcon)),
                    hasDescendant(withCardColor(firstColor)),
                ),
            )
        }
        checkViewIsDisplayed(
            allOf(
                withId(coreR.id.viewRecordTypeItem),
                hasDescendant(withText("$type (2)")),
                hasDescendant(withTag(firstIcon)),
                hasDescendant(withCardColor(firstColor)),
            ),
        )
    }

    private fun checkRecord(
        indexes: List<Int>,
        name: String,
        color: Int,
        icon: Int,
        comment: String,
    ) {
        indexes.forEach { index ->
            checkViewIsDisplayed(
                allOf(
                    nthChildOf(withId(recordsR.id.rvRecordsList), index),
                    withId(baseR.id.viewRecordItem),
                    withCardColor(color),
                    hasDescendant(withText(name)),
                    hasDescendant(withTag(icon)),
                    hasDescendant(withText(comment)),
                    isCompletelyDisplayed(),
                ),
            )
        }
    }
}
