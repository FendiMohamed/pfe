package com.example.util.simpletimetracker

import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isDescendantOfA
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withSubstring
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnRecyclerItem
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.tryAction
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.Matchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import java.util.Calendar
import java.util.concurrent.TimeUnit
import com.example.util.simpletimetracker.feature_change_record.R as changeRecordR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RetroactiveTrackingModeTest : BaseUiTest() {

    @Test
    fun empty() {
        runBlocking {
            prefsInteractor.setAllowMultitasking(false)
            prefsInteractor.setRetroactiveTrackingMode(true)
        }

        val type1 = "type1"
        val type2 = "type2"

        // Add data
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        Thread.sleep(1000)

        // Check
        tryAction { checkViewIsDisplayed(withText(R.string.retroactive_tracking_mode_hint)) }
        checkViewDoesNotExist(withText(R.string.untracked_time_name))
        checkViewDoesNotExist(withText(R.string.statistics_detail_last_record))

        // Select
        clickOnViewWithText(type1)

        // Check
        checkUntracked("0$secondString")
        checkLast(type1, "5$minuteString")
    }

    @Test
    fun tracking() {
        runBlocking {
            prefsInteractor.setAllowMultitasking(false)
            prefsInteractor.setRetroactiveTrackingMode(true)
        }

        val type1 = "type1"
        val type2 = "type2"

        // Add data
        val calendar: Calendar = Calendar.getInstance()
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addRecord(
            typeName = type1,
            timeStarted = calendar.timeInMillis - TimeUnit.HOURS.toMillis(3),
            timeEnded = calendar.timeInMillis - TimeUnit.HOURS.toMillis(1),
        )
        Thread.sleep(1000)

        // Check
        checkUntracked("1$hourString")
        checkLast(type1, "2$hourString")

        // Track
        clickOnViewWithText(type2)
        checkUntracked("0$secondString")
        checkLast(type2, "1$hourString")
    }

    @Test
    fun edit() {
        runBlocking {
            prefsInteractor.setAllowMultitasking(false)
            prefsInteractor.setRetroactiveTrackingMode(true)
        }

        val type1 = "type1"
        val type2 = "type2"

        // Add data
        val calendar: Calendar = Calendar.getInstance()
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addRecord(
            typeName = type1,
            timeStarted = calendar.timeInMillis - TimeUnit.HOURS.toMillis(5),
            timeEnded = calendar.timeInMillis - TimeUnit.HOURS.toMillis(1),
        )
        Thread.sleep(1000)

        // Check
        checkUntracked("1$hourString")
        checkLast(type1, "4$hourString")

        // Change last
        longClickOnView(
            allOf(
                withId(changeRecordR.id.viewRecordItem),
                hasDescendant(withText(type1)),
            ),
        )
        repeat(2) {
            clickOnView(
                allOf(
                    isDescendantOfA(withId(changeRecordR.id.containerChangeRecordTimeEndedAdjust)),
                    withText("-30"),
                ),
            )
        }
        clickOnViewWithText(R.string.change_record_save)

        // Check
        checkUntracked("2$hourString")
        checkLast(type1, "3$hourString")

        // Change untracked
        longClickOnView(
            allOf(
                withId(changeRecordR.id.viewRunningRecordItem),
                hasDescendant(withText(R.string.untracked_time_name)),
            ),
        )
        clickOnViewWithText(com.example.util.simpletimetracker.core.R.string.change_record_type_field)
        clickOnRecyclerItem(changeRecordR.id.rvChangeRecordType, withText(type2))
        clickOnViewWithText(R.string.change_record_save)

        // Check
        checkUntracked("1$secondString")
        checkLast(type2, "2$hourString")
    }

    @Test
    fun multitasking() {
        runBlocking {
            prefsInteractor.setAllowMultitasking(false)
            prefsInteractor.setRetroactiveTrackingMode(true)
        }

        val type1 = "type1"
        val type2 = "type2"

        // Add data
        val calendar: Calendar = Calendar.getInstance()
        testUtils.addActivity(type1)
        testUtils.addActivity(type2)
        testUtils.addRecord(
            typeName = type1,
            timeStarted = calendar.timeInMillis - TimeUnit.HOURS.toMillis(3),
            timeEnded = calendar.timeInMillis - TimeUnit.HOURS.toMillis(1),
        )
        Thread.sleep(1000)

        // Check
        checkUntracked("1$hourString")
        checkLast(type1, "2$hourString")

        // Check message
        NavUtils.openSettingsScreen()
        scrollSettingsRecyclerToText(R.string.settings_allow_multitasking)
        clickOnSettingsCheckboxBesideText(R.string.settings_allow_multitasking)
        NavUtils.openRunningRecordsScreen()
        checkViewIsDisplayed(withText(R.string.settings_retroactive_multitasking_hint))
        clickOnViewWithText(R.string.ok)
        NavUtils.openSettingsScreen()
        NavUtils.openRunningRecordsScreen()
        checkViewDoesNotExist(withText(R.string.settings_retroactive_multitasking_hint))

        // Track
        clickOnViewWithText(type2)
        checkUntracked("0$secondString")
        checkLast(type1, "3$hourString")
        checkLast(type2, "1$hourString")
    }

    private fun checkUntracked(text: String) {
        checkViewIsDisplayed(
            allOf(
                withId(changeRecordR.id.viewRunningRecordItem),
                hasDescendant(withText(R.string.untracked_time_name)),
                hasDescendant(withSubstring(text)),
            ),
        )
    }

    private fun checkLast(
        type: String,
        text: String,
    ) {
        checkViewIsDisplayed(
            allOf(
                withId(changeRecordR.id.viewRecordItem),
                hasDescendant(withText(type)),
                hasDescendant(withSubstring(text)),
            ),
        )
    }
}
