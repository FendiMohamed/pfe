package com.example.util.simpletimetracker

import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithId
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.withCardColor
import com.example.util.simpletimetracker.utils.withTag
import dagger.hilt.android.testing.HiltAndroidTest
import org.hamcrest.Matchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import com.example.util.simpletimetracker.core.R as coreR
import com.example.util.simpletimetracker.feature_base_adapter.R as baseR
import com.example.util.simpletimetracker.feature_change_record.R as changeRecordR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class DeleteRecordTest : BaseUiTest() {

    @Test
    fun deleteRecord() {
        val name = "Name"
        val color = firstColor
        val icon = firstIcon

        // Add activity
        testUtils.addActivity(name = name, color = color, icon = icon)

        // Add record
        NavUtils.openRecordsScreen()
        NavUtils.addRecord(name)

        // Delete item
        clickOnView(allOf(withText(name), isCompletelyDisplayed()))
        checkViewIsDisplayed(withId(changeRecordR.id.btnChangeRecordDelete))
        clickOnViewWithId(changeRecordR.id.btnChangeRecordDelete)

        // Check message
        checkViewIsDisplayed(
            allOf(
                withText(getString(coreR.string.record_removed, "($name)")),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )

        // Record is deleted
        checkViewDoesNotExist(allOf(withText(name), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withCardColor(color), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withTag(icon), isCompletelyDisplayed()))

        // Check undo
        clickOnViewWithText(coreR.string.record_removed_undo)

        // Record is back
        checkRecord(name = name, color = color, icon = icon)
    }

    @Test
    fun deleteRecordQuickAction() {
        val name = "Name"
        val color = firstColor
        val icon = firstIcon

        // Add activity
        testUtils.addActivity(name = name, color = color, icon = icon)
        testUtils.addRecord(typeName = name)

        // Delete item
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(name), isCompletelyDisplayed()))
        checkViewIsDisplayed(withText(R.string.archive_dialog_delete))
        clickOnViewWithText(R.string.archive_dialog_delete)

        // Check message
        checkViewIsDisplayed(
            allOf(
                withText(getString(coreR.string.record_removed, "($name)")),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )

        // Record is deleted
        checkViewDoesNotExist(allOf(withText(name), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withCardColor(color), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withTag(icon), isCompletelyDisplayed()))

        // Check undo
        clickOnViewWithText(coreR.string.record_removed_undo)

        // Record is back
        checkRecord(name = name, color = color, icon = icon)
    }

    @Test
    fun deleteRecordMultiselectQuickAction() {
        val name1 = "Name1"
        val name2 = "Name2"
        val color1 = firstColor
        val icon1 = firstIcon
        val color2 = lastColor
        val icon2 = lastIcon

        // Add activity
        testUtils.addActivity(name = name1, color = color1, icon = icon1)
        testUtils.addActivity(name = name2, color = color2, icon = icon2)
        testUtils.addRecord(typeName = name1)
        testUtils.addRecord(typeName = name2)

        // Delete item
        NavUtils.openRecordsScreen()
        longClickOnView(allOf(withText(name1), isCompletelyDisplayed()))
        clickOnViewWithText(R.string.change_record_multiselect)
        longClickOnView(allOf(withText(name2), isCompletelyDisplayed()))
        longClickOnView(allOf(withText(name2), isCompletelyDisplayed()))
        checkViewIsDisplayed(withText(R.string.archive_dialog_delete))
        clickOnViewWithText(R.string.archive_dialog_delete)

        // Check message
        checkViewIsDisplayed(
            allOf(
                withText(getString(coreR.string.record_removed, "(2)")),
                withId(com.google.android.material.R.id.snackbar_text),
            ),
        )

        // Record is deleted
        checkViewDoesNotExist(allOf(withText(name1), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withText(name2), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withCardColor(color1), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withCardColor(color2), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withTag(icon1), isCompletelyDisplayed()))
        checkViewDoesNotExist(allOf(withTag(icon2), isCompletelyDisplayed()))

        // Check undo
        clickOnViewWithText(coreR.string.record_removed_undo)

        // Record is back
        checkRecord(name = name1, color = color1, icon = icon1)
        checkRecord(name = name2, color = color2, icon = icon2)
    }

    private fun checkRecord(
        name: String,
        color: Int,
        icon: Int,
    ) {
        checkViewIsDisplayed(
            allOf(
                withId(baseR.id.viewRecordItem),
                withCardColor(color),
                hasDescendant(withText(name)),
                hasDescendant(withTag(icon)),
                isCompletelyDisplayed(),
            ),
        )
    }
}
