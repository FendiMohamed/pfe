package com.example.util.simpletimetracker

import android.view.View
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.PositionAssertions.isCompletelyLeftOf
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.SuggestionsTestUtils.checkSuggestion
import com.example.util.simpletimetracker.SuggestionsTestUtils.checkType
import com.example.util.simpletimetracker.feature_base_adapter.recordTypeSuggestion.RecordTypeSuggestionViewData
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.Direction
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.drag
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.withTag
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.Matcher
import org.junit.Test
import org.junit.runner.RunWith

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class SuggestionsTest : BaseUiTest() {

    @Test
    fun selectActivities() {
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"

        // Add data
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addActivity(type3)

        // Navigate
        NavUtils.openSettingsScreen()
        NavUtils.openSettingsAdditional()
        NavUtils.openSuggestions()

        // Select one
        clickOnViewWithText(R.string.change_record_message_choose_type)
        checkViewIsDisplayed(withText(type1))
        checkViewIsDisplayed(withText(type2))
        checkViewIsDisplayed(withText(type3))
        clickOnViewWithText(type1)
        clickOnViewWithText(R.string.change_record_save)

        checkType(type1, true)
        checkType(type2, false)
        checkType(type3, false)

        // Select other
        clickOnViewWithText(R.string.change_record_message_choose_type)
        clickOnViewWithText(type1)
        clickOnViewWithText(type2)
        clickOnViewWithText(type3)
        clickOnViewWithText(R.string.change_record_save)

        checkType(type1, false)
        checkType(type2, true)
        checkType(type3, true)

        // Check that is saved
        clickOnViewWithText(R.string.change_category_save)
        NavUtils.openSuggestions()
        checkType(type1, false)
        checkType(type2, true)
        checkType(type3, true)
    }

    @Test
    fun addSuggestions() {
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"
        val type4 = "type4"

        // Add data
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addActivity(type3)
        testUtils.addActivity(type4)
        testUtils.addSuggestion(type1)
        testUtils.addSuggestion(type2)
        testUtils.addSuggestion(type3)
        val typesMap = runBlocking { recordTypeRepo.getAll().associate { it.name to it.id } }

        // Navigate
        NavUtils.openSettingsScreen()
        NavUtils.openSettingsAdditional()
        NavUtils.openSuggestions()

        checkType(type1, true)
        checkType(type2, true)
        checkType(type3, true)
        checkType(type4, false)

        // Add suggestions
        checkSuggestion(type1, withText(R.string.running_records_add_type), typesMap[type1], true)
            .performClick()
        clickOnViewWithText(type2)
        clickOnViewWithText(R.string.change_record_save)
        checkSuggestion(type1, withText(type2), typesMap[type1], true)

        checkSuggestion(type2, withText(R.string.running_records_add_type), typesMap[type2], true)
            .performClick()
        clickOnViewWithText(type1)
        clickOnViewWithText(type3)
        clickOnViewWithText(R.string.change_record_save)
        checkSuggestion(type2, withText(type1), typesMap[type2], true)
        checkSuggestion(type2, withText(type3), typesMap[type2], true)

        checkSuggestion(type3, withText(type1), typesMap[type3], false)
        checkSuggestion(type3, withText(type2), typesMap[type3], false)
        checkSuggestion(type3, withText(type3), typesMap[type3], false)

        // Check that is saved
        clickOnViewWithText(R.string.change_record_save)
        NavUtils.openSuggestions()
        checkSuggestion(type1, withText(type2), typesMap[type1], true)
        checkSuggestion(type2, withText(type1), typesMap[type2], true)
        checkSuggestion(type2, withText(type3), typesMap[type2], true)
    }

    @Test
    fun fromStatistics() {
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"

        // Add data
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addActivity(type3)

        val currentTime = System.currentTimeMillis()
        testUtils.addRecord(type1, currentTime - 10, currentTime - 10)
        testUtils.addRecord(type2, currentTime - 9, currentTime - 9)
        testUtils.addRecord(type1, currentTime - 8, currentTime - 8)
        testUtils.addRecord(type3, currentTime - 7, currentTime - 7)
        testUtils.addRecord(type1, currentTime - 6, currentTime - 6)
        testUtils.addRecord(type3, currentTime - 5, currentTime - 5)
        testUtils.addSuggestion(type1)
        testUtils.addSuggestion(type2)
        testUtils.addSuggestion(type3)
        val typesMap = runBlocking { recordTypeRepo.getAll().associate { it.name to it.id } }

        // Navigate
        NavUtils.openSettingsScreen()
        NavUtils.openSettingsAdditional()
        NavUtils.openSuggestions()

        // Check
        clickOnViewWithText(R.string.activity_suggestions_calculate)

        checkSuggestion(type1, withText(type1), typesMap[type1], false)
        var type2Matcher = checkSuggestion(type1, withText(type2), typesMap[type1], true)
        var type3Matcher = checkSuggestion(type1, withText(type3), typesMap[type1], true)
        onView(type3Matcher).check(isCompletelyLeftOf(type2Matcher))

        checkSuggestion(type2, withText(type1), typesMap[type2], true)
        checkSuggestion(type2, withText(type2), typesMap[type2], false)
        checkSuggestion(type2, withText(type3), typesMap[type2], false)

        checkSuggestion(type3, withText(type1), typesMap[type3], true)
        checkSuggestion(type3, withText(type2), typesMap[type3], false)
        checkSuggestion(type3, withText(type3), typesMap[type3], false)

        // Check buttons
        pressBack()
        NavUtils.openSuggestions()

        checkSuggestion(type1, withText(type1), typesMap[type1], false)
        checkSuggestion(type1, withText(type2), typesMap[type1], false)
        checkSuggestion(type1, withText(type3), typesMap[type1], false)
        checkSuggestion(type1, withText(R.string.shortcut_navigation_statistics), typesMap[type1], true)
            .performClick()
        tryAction { checkSuggestion(type1, withText(type1), typesMap[type1], false) }
        type2Matcher = checkSuggestion(type1, withText(type2), typesMap[type1], true)
        type3Matcher = checkSuggestion(type1, withText(type3), typesMap[type1], true)
        onView(type3Matcher).check(isCompletelyLeftOf(type2Matcher))

        Thread.sleep(500)
        checkSuggestion(type2, withText(type1), typesMap[type2], false)
        checkSuggestion(type2, withText(type2), typesMap[type2], false)
        checkSuggestion(type2, withText(type3), typesMap[type2], false)
        checkSuggestion(type2, withText(R.string.shortcut_navigation_statistics), typesMap[type2], true)
            .performClick()
        tryAction { checkSuggestion(type2, withText(type1), typesMap[type2], true) }
        checkSuggestion(type2, withText(type2), typesMap[type2], false)
        checkSuggestion(type2, withText(type3), typesMap[type2], false)

        Thread.sleep(500)
        checkSuggestion(type3, withText(type1), typesMap[type3], false)
        checkSuggestion(type3, withText(type2), typesMap[type3], false)
        checkSuggestion(type3, withText(type3), typesMap[type3], false)
        checkSuggestion(type3, withText(R.string.shortcut_navigation_statistics), typesMap[type3], true)
            .performClick()
        tryAction { checkSuggestion(type3, withText(type1), typesMap[type3], true) }
        checkSuggestion(type3, withText(type2), typesMap[type3], false)
        checkSuggestion(type3, withText(type3), typesMap[type3], false)
    }

    @Test
    fun reorder() {
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"

        // Add data
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addActivity(type3)
        testUtils.addSuggestion(type1, listOf(type2, type3))
        val typesMap = runBlocking { recordTypeRepo.getAll().associate { it.name to it.id } }

        // Navigate
        NavUtils.openSettingsScreen()
        NavUtils.openSettingsAdditional()
        NavUtils.openSuggestions()

        // Check
        var type2Matcher = checkSuggestion(type1, withText(type2), typesMap[type1], true)
        var type3Matcher = checkSuggestion(type1, withText(type3), typesMap[type1], true)
        onView(type2Matcher).check(isCompletelyLeftOf(type3Matcher))

        // Reorder
        onView(type3Matcher).perform(drag(Direction.LEFT, 300))
        Thread.sleep(500)
        onView(type3Matcher).check(isCompletelyLeftOf(type2Matcher))
        clickOnViewWithText(R.string.change_record_save)

        // Check that is saved
        NavUtils.openSuggestions()
        onView(type3Matcher).check(isCompletelyLeftOf(type2Matcher))

        // Check on main
        pressBack()
        NavUtils.openRunningRecordsScreen()
        checkViewDoesNotExist(typeMatcher(type1))
        checkViewDoesNotExist(typeMatcher(type2))
        checkViewDoesNotExist(typeMatcher(type3))
        clickOnViewWithText(type1)
        type2Matcher = typeMatcher(type2)
        type3Matcher = typeMatcher(type3)
        tryAction { checkViewIsDisplayed(type2Matcher) }
        checkViewIsDisplayed(type3Matcher)
        onView(type3Matcher).check(isCompletelyLeftOf(type2Matcher))
    }

    @Test
    fun mainTab() {
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"

        // Add data
        runBlocking { prefsInteractor.setAllowMultitasking(false) }
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addActivity(type3)
        testUtils.addSuggestion(type1, listOf(type2, type3))
        testUtils.addSuggestion(type2, listOf(type3))
        testUtils.addSuggestion(type3, listOf(type1, type2))
        Thread.sleep(1000)

        // Check
        checkViewDoesNotExist(typeMatcher(type1))
        checkViewDoesNotExist(typeMatcher(type2))
        checkViewDoesNotExist(typeMatcher(type3))

        clickOnViewWithText(type1)
        checkRunningRecord(type1)
        checkViewDoesNotExist(typeMatcher(type1))
        checkViewIsDisplayed(typeMatcher(type2))
        checkViewIsDisplayed(typeMatcher(type3))

        typeMatcher(type2).performClick()
        checkRunningRecord(type2)
        checkViewDoesNotExist(typeMatcher(type1))
        checkViewDoesNotExist(typeMatcher(type2))
        checkViewIsDisplayed(typeMatcher(type3))

        typeMatcher(type3).performClick()
        checkRunningRecord(type3)
        checkViewIsDisplayed(typeMatcher(type1))
        checkViewIsDisplayed(typeMatcher(type2))
        checkViewDoesNotExist(typeMatcher(type3))
    }

    @Test
    fun multitasking() {
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"
        val type4 = "type4"

        // Add data
        runBlocking { prefsInteractor.setAllowMultitasking(true) }
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addActivity(type3)
        testUtils.addActivity(type4)
        testUtils.addSuggestion(type1, listOf(type3))
        testUtils.addSuggestion(type2, listOf(type4))
        Thread.sleep(1000)

        // Check
        checkViewDoesNotExist(typeMatcher(type1))
        checkViewDoesNotExist(typeMatcher(type2))
        checkViewDoesNotExist(typeMatcher(type3))
        checkViewDoesNotExist(typeMatcher(type4))

        clickOnViewWithText(type1)
        checkRunningRecord(type1)
        checkViewDoesNotExist(typeMatcher(type1))
        checkViewDoesNotExist(typeMatcher(type2))
        checkViewIsDisplayed(typeMatcher(type3))
        checkViewDoesNotExist(typeMatcher(type4))

        clickOnViewWithText(type2)
        checkRunningRecord(type1)
        checkRunningRecord(type2)
        checkViewDoesNotExist(typeMatcher(type1))
        checkViewDoesNotExist(typeMatcher(type2))
        checkViewIsDisplayed(typeMatcher(type3))
        checkViewIsDisplayed(typeMatcher(type4))
    }

    private fun Matcher<View>.performClick() {
        onView(this).perform(click())
    }

    private fun typeMatcher(name: String): Matcher<View> {
        return allOf(
            withId(R.id.viewRecordTypeItem),
            withTag(RecordTypeSuggestionViewData.TEST_TAG),
            hasDescendant(withText(name)),
        )
    }

    private fun checkRunningRecord(name: String) {
        checkViewIsDisplayed(allOf(withId(R.id.viewRunningRecordItem), hasDescendant(withText(name))))
    }
}
