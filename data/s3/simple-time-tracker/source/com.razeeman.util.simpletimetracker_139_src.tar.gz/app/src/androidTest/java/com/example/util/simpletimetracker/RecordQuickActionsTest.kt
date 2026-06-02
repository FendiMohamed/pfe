package com.example.util.simpletimetracker

import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.feature_statistics_detail.R
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.tryAction
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.Matchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.TimeUnit

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RecordQuickActionsTest : BaseUiTest() {

    @Test
    fun recordQuickActions() {
        val name = "Test"
        val tag = "Tag"

        // Add data
        testUtils.addActivity(name)
        testUtils.addRecord(name)
        testUtils.addRecordTag(tag)

        // Check
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(name), isCompletelyDisplayed()))

        checkViewIsDisplayed(withText(R.string.shortcut_navigation_statistics))
        checkViewIsDisplayed(withText(R.string.archive_dialog_delete))
        checkViewIsDisplayed(withText(R.string.change_record_continue))
        checkViewIsDisplayed(withText(R.string.change_record_repeat))
        checkViewIsDisplayed(withText(R.string.change_record_duplicate))
        checkViewIsDisplayed(withText(R.string.change_record_move))
        checkViewIsDisplayed(withText(R.string.change_record_multiselect))
        checkViewIsDisplayed(withText(R.string.data_edit_change_activity))
        checkViewIsDisplayed(withText(R.string.data_edit_change_tag))
        checkViewDoesNotExist(withText(R.string.change_record_merge))
        checkViewDoesNotExist(withText(R.string.notification_record_type_stop))
    }

    @Test
    fun untrackedRecordQuickActions() {
        val name = "Test"

        // Add data
        runBlocking { prefsInteractor.setShowUntrackedInRecords(true) }
        testUtils.addActivity(name)
        val yesterday = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(1)
        testUtils.addRecord(typeName = name, timeStarted = yesterday, timeEnded = yesterday)

        // Check statistics navigation
        NavUtils.openRecordsScreen()
        longClickOnView(
            allOf(
                withText(com.example.util.simpletimetracker.core.R.string.untracked_time_name),
                isCompletelyDisplayed(),
            ),
        )

        checkViewIsDisplayed(withText(R.string.shortcut_navigation_statistics))
        checkViewDoesNotExist(withText(R.string.archive_dialog_delete))
        checkViewDoesNotExist(withText(R.string.change_record_continue))
        checkViewDoesNotExist(withText(R.string.change_record_repeat))
        checkViewDoesNotExist(withText(R.string.change_record_duplicate))
        checkViewDoesNotExist(withText(R.string.change_record_move))
        checkViewIsDisplayed(withText(R.string.change_record_multiselect))
        checkViewIsDisplayed(withText(R.string.data_edit_change_activity))
        checkViewDoesNotExist(withText(R.string.data_edit_change_tag))
        checkViewIsDisplayed(withText(R.string.change_record_merge))
        checkViewDoesNotExist(withText(R.string.notification_record_type_stop))
    }

    @Test
    fun runningRecordQuickActions() {
        val name = "Test"
        val tag = "Tag"

        // Add data
        testUtils.addActivity(name)
        testUtils.addRecordTag(tag)
        Thread.sleep(1000)
        tryAction { clickOnViewWithText(name) }

        // Check
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(name), isCompletelyDisplayed()))

        checkViewIsDisplayed(withText(R.string.shortcut_navigation_statistics))
        checkViewIsDisplayed(withText(R.string.archive_dialog_delete))
        checkViewDoesNotExist(withText(R.string.change_record_continue))
        checkViewDoesNotExist(withText(R.string.change_record_repeat))
        checkViewIsDisplayed(withText(R.string.change_record_duplicate))
        checkViewDoesNotExist(withText(R.string.change_record_move))
        checkViewIsDisplayed(withText(R.string.change_record_multiselect))
        checkViewIsDisplayed(withText(R.string.data_edit_change_activity))
        checkViewIsDisplayed(withText(R.string.data_edit_change_tag))
        checkViewDoesNotExist(withText(R.string.change_record_merge))
        checkViewIsDisplayed(withText(R.string.notification_record_type_stop))
    }
}
