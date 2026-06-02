package com.example.util.simpletimetracker

import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.hasSibling
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withSubstring
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.feature_statistics_detail.R
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.Matchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.TimeUnit

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RecordActionsMultiselectTest : BaseUiTest() {

    @Test
    fun selecting() {
        val nameTracked1 = "TestTracked1"
        val nameTracked2 = "TestTracked2"
        val nameRunning = "TestRunning"

        // Add data
        val current = System.currentTimeMillis()
        testUtils.addActivity(nameTracked1)
        testUtils.addActivity(nameTracked2)
        testUtils.addActivity(nameRunning)
        testUtils.addRecord(
            typeName = nameTracked1,
            timeStarted = current - TimeUnit.MINUTES.toMillis(3),
            timeEnded = current - TimeUnit.MINUTES.toMillis(2),
        )
        testUtils.addRecord(
            typeName = nameTracked2,
            timeStarted = current - TimeUnit.MINUTES.toMillis(3),
            timeEnded = current - TimeUnit.MINUTES.toMillis(2),
        )
        testUtils.addRunningRecord(nameRunning)

        // Check
        NavUtils.openRecordsScreen()
        checkViewDoesNotExist(withId(R.id.ivRecordSelectedItemCheck))

        // Check selecting
        longClickOnView(allOf(withText(nameTracked1), isCompletelyDisplayed()))
        checkViewDoesNotExist(withSubstring(getString(R.string.something_selected)))
        clickOnViewWithText(R.string.change_record_multiselect)
        checkViewIsDisplayed(
            allOf(
                withId(R.id.ivRecordSelectedItemCheck),
                hasSibling(allOf(withId(R.id.viewRecordItem), hasDescendant(withText(nameTracked1)))),
            ),
        )
        longClickOnView(allOf(withText(nameTracked1), isCompletelyDisplayed()))
        checkViewIsDisplayed(withSubstring("1"))
        pressBack()

        clickOnView(allOf(withText(nameTracked2), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(nameTracked2), isCompletelyDisplayed()))
        checkViewIsDisplayed(withSubstring("2"))
        pressBack()
        checkViewIsDisplayed(
            allOf(
                withId(R.id.ivRecordSelectedItemCheck),
                hasSibling(allOf(withId(R.id.viewRecordItem), hasDescendant(withText(nameTracked2)))),
            ),
        )

        clickOnView(allOf(withText(nameRunning), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(nameRunning), isCompletelyDisplayed()))
        checkViewIsDisplayed(withSubstring("3"))
        pressBack()
        checkViewIsDisplayed(
            allOf(
                withId(R.id.ivRecordSelectedItemCheck),
                hasSibling(allOf(withId(R.id.viewRunningRecordItem), hasDescendant(withText(nameRunning)))),
            ),
        )

        clickOnView(allOf(withText(R.string.untracked_time_name), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(R.string.untracked_time_name), isCompletelyDisplayed()))
        checkViewIsDisplayed(withSubstring("4"))
        pressBack()
        checkViewIsDisplayed(
            allOf(
                withId(R.id.ivRecordSelectedItemCheck),
                hasSibling(allOf(withId(R.id.viewRecordItem), hasDescendant(withText(R.string.untracked_time_name)))),
            ),
        )

        // Deselect
        clickOnView(allOf(withText(nameTracked2), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(nameTracked1), isCompletelyDisplayed()))
        checkViewIsDisplayed(withSubstring("3"))
        pressBack()
        checkViewDoesNotExist(
            allOf(
                withId(R.id.ivRecordSelectedItemCheck),
                hasSibling(allOf(withId(R.id.viewRecordItem), hasDescendant(withText(nameTracked2)))),
            ),
        )

        // Cancel
        longClickOnView(allOf(withText(nameTracked1), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.cancel)
        checkViewDoesNotExist(withId(R.id.ivRecordSelectedItemCheck))
        longClickOnView(allOf(withText(nameTracked1), isCompletelyDisplayed()))
        checkViewDoesNotExist(withSubstring(getString(R.string.something_selected)))
    }

    @Test
    fun disablingOnSwipe() {
        val name = "Test"

        // Add data
        testUtils.addActivity(name)
        testUtils.addRecord(name)

        // Check
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(name), isCompletelyDisplayed()))
        checkViewDoesNotExist(withSubstring(getString(R.string.something_selected)))
        clickOnViewWithText(R.string.change_record_multiselect)
        checkViewIsDisplayed(
            allOf(
                withId(R.id.ivRecordSelectedItemCheck),
                hasSibling(allOf(withId(R.id.viewRecordItem), hasDescendant(withText(name)))),
            ),
        )
        NavUtils.openRunningRecordsScreen()
        NavUtils.openRecordsScreen()
        checkViewDoesNotExist(withId(R.id.ivRecordSelectedItemCheck))
        longClickOnView(allOf(withText(name), isCompletelyDisplayed()))
        checkViewDoesNotExist(withSubstring(getString(R.string.something_selected)))
    }

    @Test
    fun actionsAvailability() {
        val nameTracked = "TestTracked"
        val nameRunning = "TestRunning"
        val nameTag = "TestTag"

        // Add data
        val current = System.currentTimeMillis()
        testUtils.addActivity(nameTracked)
        testUtils.addActivity(nameRunning)
        testUtils.addRecordTag(nameTag)
        testUtils.addRecord(
            typeName = nameTracked,
            timeStarted = current - TimeUnit.MINUTES.toMillis(3),
            timeEnded = current - TimeUnit.MINUTES.toMillis(2),
        )
        testUtils.addRunningRecord(nameRunning)
        NavUtils.openRecordsScreen()

        // Check tracked
        longClickOnView(allOf(withText(nameTracked), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(nameTracked), isCompletelyDisplayed()))

        checkViewDoesNotExist(withText(R.string.shortcut_navigation_statistics))
        checkViewIsDisplayed(withText(R.string.archive_dialog_delete))
        checkViewDoesNotExist(withText(R.string.change_record_continue))
        checkViewDoesNotExist(withText(R.string.change_record_repeat))
        checkViewIsDisplayed(withText(R.string.change_record_duplicate))
        checkViewIsDisplayed(withText(R.string.change_record_move))
        checkViewIsDisplayed(withText(R.string.change_record_multiselect))
        checkViewIsDisplayed(withText(R.string.data_edit_change_activity))
        checkViewIsDisplayed(withText(R.string.data_edit_change_tag))
        checkViewDoesNotExist(withText(R.string.change_record_merge))
        checkViewDoesNotExist(withText(R.string.notification_record_type_stop))

        // Check running
        clickOnViewWithText(R.string.cancel)
        longClickOnView(allOf(withText(nameRunning), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(nameRunning), isCompletelyDisplayed()))

        checkViewDoesNotExist(withText(R.string.shortcut_navigation_statistics))
        checkViewDoesNotExist(withText(R.string.archive_dialog_delete))
        checkViewDoesNotExist(withText(R.string.change_record_continue))
        checkViewDoesNotExist(withText(R.string.change_record_repeat))
        checkViewDoesNotExist(withText(R.string.change_record_duplicate))
        checkViewDoesNotExist(withText(R.string.change_record_move))
        checkViewIsDisplayed(withText(R.string.change_record_multiselect))
        checkViewIsDisplayed(withText(R.string.data_edit_change_activity))
        checkViewIsDisplayed(withText(R.string.data_edit_change_tag))
        checkViewDoesNotExist(withText(R.string.change_record_merge))
        checkViewDoesNotExist(withText(R.string.notification_record_type_stop))

        // Check untracked
        clickOnViewWithText(R.string.cancel)
        longClickOnView(allOf(withText(R.string.untracked_time_name), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(R.string.untracked_time_name), isCompletelyDisplayed()))

        checkViewDoesNotExist(withText(R.string.shortcut_navigation_statistics))
        checkViewDoesNotExist(withText(R.string.archive_dialog_delete))
        checkViewDoesNotExist(withText(R.string.change_record_continue))
        checkViewDoesNotExist(withText(R.string.change_record_repeat))
        checkViewDoesNotExist(withText(R.string.change_record_duplicate))
        checkViewDoesNotExist(withText(R.string.change_record_move))
        checkViewIsDisplayed(withText(R.string.change_record_multiselect))
        checkViewIsDisplayed(withText(R.string.data_edit_change_activity))
        checkViewDoesNotExist(withText(R.string.data_edit_change_tag))
        checkViewDoesNotExist(withText(R.string.change_record_merge))
        checkViewDoesNotExist(withText(R.string.notification_record_type_stop))

        // Check all
        clickOnViewWithText(R.string.cancel)
        longClickOnView(allOf(withText(nameTracked), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(nameRunning), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(R.string.untracked_time_name), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(nameTracked), isCompletelyDisplayed()))

        checkViewDoesNotExist(withText(R.string.shortcut_navigation_statistics))
        checkViewDoesNotExist(withText(R.string.archive_dialog_delete))
        checkViewDoesNotExist(withText(R.string.change_record_continue))
        checkViewDoesNotExist(withText(R.string.change_record_repeat))
        checkViewDoesNotExist(withText(R.string.change_record_duplicate))
        checkViewDoesNotExist(withText(R.string.change_record_move))
        checkViewIsDisplayed(withText(R.string.change_record_multiselect))
        checkViewIsDisplayed(withText(R.string.data_edit_change_activity))
        checkViewDoesNotExist(withText(R.string.data_edit_change_tag))
        checkViewDoesNotExist(withText(R.string.change_record_merge))
        checkViewDoesNotExist(withText(R.string.notification_record_type_stop))
    }
}
