package com.example.util.simpletimetracker

import android.view.View
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isDescendantOfA
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.feature_change_record_tag.R
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnRecyclerItem
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnView
import com.example.util.simpletimetracker.utils.scrollRecyclerInPagerToView
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.typeTextIntoView
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.Matcher
import org.junit.Test
import org.junit.runner.RunWith
import com.example.util.simpletimetracker.core.R as coreR
import com.example.util.simpletimetracker.feature_change_record.R as changeRecordR
import com.example.util.simpletimetracker.feature_change_running_record.R as changeRunningRecordR
import com.example.util.simpletimetracker.feature_records.R as recordsR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RecordTagValueTest : BaseUiTest() {

    @Test
    fun start() {
        val typeName1 = "TypeName1"
        val typeName2 = "TypeName2"
        val typeName3 = "TypeName3"
        val tagNoValue = "TagNoValue"
        val tagWithValue = "TagValue"
        val tagWithValueWithSuffix = "TagValueWithSuffix"
        val suffix = "kg"
        val value1 = "1"
        val value2 = "2"
        val fullName = "$typeName1 - $tagNoValue"
        val fullNameWithValue = "$typeName2 - $tagWithValue ($value1)"
        val fullNameWithValueAndSuffix = "$typeName3 - $tagWithValueWithSuffix ($value2 $suffix)"

        fun checkRunningRecord(name: String) {
            checkViewIsDisplayed(
                allOf(
                    isDescendantOfA(withId(R.id.viewRunningRecordItem)),
                    withText(name),
                ),
            )
        }

        // Add data
        runBlocking { prefsInteractor.setShowRecordTagSelection(true) }
        testUtils.addActivity(typeName1)
        testUtils.addActivity(typeName2)
        testUtils.addActivity(typeName3)
        testUtils.addRecordTag(tagNoValue, typeName1)
        testUtils.addRecordTag(tagWithValue, typeName2, hasTagValue = true)
        testUtils.addRecordTag(tagWithValueWithSuffix, typeName3, hasTagValue = true, tagValueSuffix = suffix)
        Thread.sleep(1000)

        // Add no value
        tryAction { clickOnViewWithText(typeName1) }
        tryAction { clickOnViewWithText(tagNoValue) }
        clickOnViewWithText(R.string.duration_dialog_save)
        tryAction { checkRunningRecord(fullName) }

        // Add with value
        clickOnViewWithText(typeName2)
        tryAction { clickOnViewWithText(tagWithValue) }
        typeTextIntoView(R.id.etCommentItemField, value1)
        closeSoftKeyboard()
        clickOnViewWithText(R.string.duration_dialog_save)
        checkViewIsDisplayed(withText("$tagWithValue ($value1)"))
        clickOnViewWithText(R.string.duration_dialog_save)
        tryAction { checkRunningRecord(fullNameWithValue) }

        // Add with value and suffix
        clickOnViewWithText(typeName3)
        tryAction { clickOnViewWithText(tagWithValueWithSuffix) }
        typeTextIntoView(R.id.etCommentItemField, value2)
        closeSoftKeyboard()
        clickOnViewWithText(R.string.duration_dialog_save)
        checkViewIsDisplayed(withText("$tagWithValueWithSuffix ($value2 $suffix)"))
        clickOnViewWithText(R.string.duration_dialog_save)
        tryAction { checkRunningRecord(fullNameWithValueAndSuffix) }
    }

    @Test
    fun changeRecord() {
        val name = "Test1"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val fullName1 = "$name - $tag1"

        // Add activities
        testUtils.addActivity(name)
        testUtils.addRecordTag(tag1, name)
        testUtils.addRecordTag(tag2, name, hasTagValue = true)
        testUtils.addRecord(name, tagNames = listOf(tag1))

        // Open record
        NavUtils.openRecordsScreen()
        clickOnView(withText(fullName1))
        checkPreviewUpdated(hasDescendant(withText(fullName1)))

        // Change value
        clickOnViewWithText(coreR.string.change_record_tag_field)
        clickOnRecyclerItem(changeRecordR.id.rvChangeRecordCategories, withText(tag1))
        clickOnRecyclerItem(changeRecordR.id.rvChangeRecordCategories, withText(tag2))
        typeTextIntoView(R.id.etCommentItemField, "1")
        closeSoftKeyboard()
        clickOnViewWithText(coreR.string.change_record_type_save)
        checkViewIsDisplayed(allOf(withId(R.id.viewCategoryItem), hasDescendant(withText("$tag2 (1)"))))
        checkPreviewUpdated(hasDescendant(withText("$name - $tag2 (1)")))

        // Change value
        clickOnRecyclerItem(changeRecordR.id.rvChangeRecordCategories, withText("$tag2 (1)"))
        clickOnRecyclerItem(changeRecordR.id.rvChangeRecordCategories, withText(tag2))
        typeTextIntoView(R.id.etCommentItemField, "2")
        closeSoftKeyboard()
        clickOnViewWithText(coreR.string.change_record_type_save)
        checkViewIsDisplayed(allOf(withId(R.id.viewCategoryItem), hasDescendant(withText("$tag2 (2)"))))
        checkPreviewUpdated(hasDescendant(withText("$name - $tag2 (2)")))

        // Record updated
        clickOnViewWithText(coreR.string.change_record_type_save)
        checkViewDoesNotExist(withText(fullName1))
        checkViewIsDisplayed(withText("$name - $tag2 (2)"))
    }

    @Test
    fun changeRunningRecord() {
        val name = "Test1"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val fullName1 = "$name - $tag1"

        // Add activities
        testUtils.addActivity(name)
        testUtils.addRecordTag(tag1, name)
        testUtils.addRecordTag(tag2, name, hasTagValue = true)
        testUtils.addRunningRecord(name, tagNames = listOf(tag1))
        Thread.sleep(1000)

        // Open record
        tryAction { longClickOnView(withText(fullName1)) }
        checkRunningPreviewUpdated(hasDescendant(withText(fullName1)))

        // Change value
        clickOnViewWithText(coreR.string.change_record_tag_field)
        clickOnRecyclerItem(changeRecordR.id.rvChangeRecordCategories, withText(tag1))
        clickOnRecyclerItem(changeRecordR.id.rvChangeRecordCategories, withText(tag2))
        typeTextIntoView(R.id.etCommentItemField, "1")
        closeSoftKeyboard()
        clickOnViewWithText(coreR.string.change_record_type_save)
        checkViewIsDisplayed(allOf(withId(R.id.viewCategoryItem), hasDescendant(withText("$tag2 (1)"))))
        checkRunningPreviewUpdated(hasDescendant(withText("$name - $tag2 (1)")))

        // Record updated
        clickOnViewWithText(coreR.string.change_record_type_save)
        checkViewDoesNotExist(withText(fullName1))
        checkViewIsDisplayed(withText("$name - $tag2 (1)"))
    }

    @Test
    fun valueFormatting() {
        val typeName = "typeName"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val suffix = "kg"

        val data = listOf(
            tag1 to 1.0 to "$typeName - $tag1 (1)",
            tag2 to 1.0 to "$typeName - $tag2 (1 $suffix)",
            tag1 to 2.3 to "$typeName - $tag1 (2.3)",
            tag2 to 2.3 to "$typeName - $tag2 (2.3 $suffix)",
            tag1 to 4.0000005 to "$typeName - $tag1 (4.0000005)",
            tag2 to 4.0000005 to "$typeName - $tag2 (4.0000005 $suffix)",
            tag1 to -1.0 to "$typeName - $tag1 (-1)",
            tag2 to -1.0 to "$typeName - $tag2 (-1 $suffix)",
            tag1 to -2.3 to "$typeName - $tag1 (-2.3)",
            tag2 to -2.3 to "$typeName - $tag2 (-2.3 $suffix)",
            tag1 to -4.0000005 to "$typeName - $tag1 (-4.0000005)",
            tag2 to -4.0000005 to "$typeName - $tag2 (-4.0000005 $suffix)",
        )

        // Add data
        testUtils.addActivity(typeName)
        testUtils.addRecordTag(tag1, typeName, hasTagValue = true)
        testUtils.addRecordTag(tag2, typeName, hasTagValue = true, tagValueSuffix = suffix)
        data.forEach { (tag, _) ->
            testUtils.addRecord(typeName, tagNamesWithValues = listOf(tag))
        }

        // Check
        NavUtils.openRecordsScreen()
        data.forEach { (_, name) ->
            scrollRecyclerInPagerToView(
                recordsR.id.rvRecordsList,
                allOf(withId(R.id.viewRecordItem), hasDescendant(withText(name))),
            )
            checkViewIsDisplayed(withText(name))
        }
    }

    private fun checkPreviewUpdated(matcher: Matcher<View>) =
        checkViewIsDisplayed(allOf(withId(changeRecordR.id.previewChangeRecord), matcher))

    private fun checkRunningPreviewUpdated(matcher: Matcher<View>) =
        checkViewIsDisplayed(allOf(withId(changeRunningRecordR.id.previewChangeRunningRecord), matcher))
}
