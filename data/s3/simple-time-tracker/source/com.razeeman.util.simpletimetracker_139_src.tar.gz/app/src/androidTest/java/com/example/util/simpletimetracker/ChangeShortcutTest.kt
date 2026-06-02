package com.example.util.simpletimetracker

import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.checkViewIsNotDisplayed
import com.example.util.simpletimetracker.utils.clickOnRecyclerItem
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithId
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.scrollRecyclerToView
import com.example.util.simpletimetracker.utils.tryAction
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.CoreMatchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import com.example.util.simpletimetracker.core.R as coreR
import com.example.util.simpletimetracker.feature_base_adapter.R as baseR
import com.example.util.simpletimetracker.feature_change_shortcut.R as changeShortcutR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class ChangeShortcutTest : BaseUiTest() {

    @Test
    fun navigationAdd() {
        // Check buttons
        openShortcutsScreen()
        clickOnViewWithText(coreR.string.running_records_add_type)
        checkViewIsDisplayed(withId(changeShortcutR.id.btnChangeShortcutSave))
        checkViewIsNotDisplayed(withId(changeShortcutR.id.btnChangeShortcutDelete))
    }

    @Test
    fun navigationEdit() {
        val name = "name"

        // Add data
        testUtils.addActivity(name)
        testUtils.addShortcut(name)

        // Check buttons
        openShortcutsScreen()
        clickShortcut(name)
        checkViewIsDisplayed(withId(changeShortcutR.id.btnChangeShortcutDelete))
    }

    @Test
    fun navigationFromTimers() {
        val name = "name"

        // Add data
        testUtils.addActivity(name)
        testUtils.addShortcut(name)
        Thread.sleep(1000)

        // Open edit
        NavUtils.openRunningRecordsScreen()
        longClickOnView(
            allOf(
                withId(baseR.id.viewRecordShortcutItem),
                hasDescendant(withText(name)),
            ),
        )
        checkViewIsDisplayed(withId(changeShortcutR.id.btnChangeShortcutDelete))
    }

    @Test
    fun createRecordShortcut() {
        val name = "name"

        // Add data
        testUtils.addActivity(name)

        // Check record
        openShortcutsScreen()
        clickOnViewWithText(coreR.string.running_records_add_type)
        selectRecordType(name)
        clickOnViewWithId(changeShortcutR.id.btnChangeShortcutSave)

        // Check saved
        tryAction { checkShortcut(name) }
    }

    @Test
    fun createSettingShortcut() {
        // Check setting
        openShortcutsScreen()
        clickOnViewWithText(coreR.string.running_records_add_type)
        clickOnViewWithText(coreR.string.shortcut_navigation_settings)
        clickOnViewWithId(changeShortcutR.id.fieldChangeShortcutSettingAction)
        clickOnRecyclerItem(
            changeShortcutR.id.rvChangeShortcutSettingAction,
            withText(coreR.string.settings_allow_multitasking),
        )
        clickOnViewWithId(changeShortcutR.id.btnChangeShortcutSave)

        // Check saved
        tryAction { checkShortcut(getString(coreR.string.settings_allow_multitasking)) }
    }

    @Test
    fun edit() {
        val nameBefore = "name1"
        val nameAfter = "name2"

        // Add data
        testUtils.addActivity(nameBefore)
        testUtils.addActivity(nameAfter)
        testUtils.addShortcut(nameBefore)

        // Update
        openShortcutsScreen()
        clickShortcut(nameBefore)
        selectRecordType(nameAfter)
        clickOnViewWithId(changeShortcutR.id.btnChangeShortcutSave)

        // Check updated
        tryAction { checkShortcut(nameAfter) }
        checkViewDoesNotExist(
            allOf(
                withId(baseR.id.viewRecordShortcutItem),
                hasDescendant(withText(nameBefore)),
            ),
        )
    }

    @Test
    fun delete() {
        val name = "name"

        // Add data
        testUtils.addActivity(name)
        testUtils.addShortcut(name)

        // Delete
        openShortcutsScreen()
        clickShortcut(name)
        clickOnViewWithId(changeShortcutR.id.btnChangeShortcutDelete)
        clickOnViewWithText(R.string.ok)

        // Check
        checkViewDoesNotExist(
            allOf(
                withId(baseR.id.viewRecordShortcutItem),
                hasDescendant(withText(name)),
            ),
        )
    }

    private fun openShortcutsScreen() {
        NavUtils.openSettingsScreen()
        NavUtils.openSettingsAdditional()
        NavUtils.openShortcutsScreen()
    }

    private fun selectRecordType(name: String) {
        clickOnViewWithId(changeShortcutR.id.fieldChangeShortcutType)
        scrollRecyclerToView(
            changeShortcutR.id.rvChangeShortcutType,
            hasDescendant(withText(name)),
        )
        clickOnRecyclerItem(changeShortcutR.id.rvChangeShortcutType, withText(name))
    }

    private fun clickShortcut(name: String) {
        clickOnView(
            allOf(
                withId(baseR.id.viewRecordShortcutItem),
                hasDescendant(withText(name)),
            ),
        )
    }

    private fun checkShortcut(name: String) {
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordShortcutItem),
                hasDescendant(withText(name)),
            ),
        )
    }
}
