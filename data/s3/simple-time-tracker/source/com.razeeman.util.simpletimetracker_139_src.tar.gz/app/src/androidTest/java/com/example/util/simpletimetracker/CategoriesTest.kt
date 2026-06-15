package com.example.util.simpletimetracker

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.Espresso.pressBack
import androidx.test.espresso.assertion.PositionAssertions.isCompletelyBelow
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.SuggestionsTestUtils.suggestionMatcher
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.checkViewIsNotDisplayed
import com.example.util.simpletimetracker.utils.clickOnViewWithId
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.longClickOnViewWithId
import com.example.util.simpletimetracker.utils.scrollRecyclerToView
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.typeTextIntoView
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import com.example.util.simpletimetracker.feature_categories.R as categoriesR
import com.example.util.simpletimetracker.feature_dialogs.R as dialogsR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class CategoriesTest : BaseUiTest() {

    @Test
    fun filtering() {
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"
        val type4 = "type4"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val tag3 = "tag3"
        val category1 = "category1"
        val category2 = "category2"
        val category3 = "category3"

        // Add data
        testUtils.addCategory(category1)
        testUtils.addCategory(category2)
        testUtils.addCategory(category3)
        testUtils.addActivity(type1)
        testUtils.addActivity(type2, categories = listOf(category2))
        testUtils.addActivity(type3, categories = listOf(category3))
        testUtils.addActivity(type4, categories = listOf(category2, category3))
        testUtils.addRecordTag(tag1)
        testUtils.addRecordTag(tag2, typeName = type2)
        testUtils.addRecordTag(tag3, typeName = type3)

        // Check
        NavUtils.openSettingsScreen()
        NavUtils.openCategoriesScreen()
        checkTagVisible(tag1, tag2, tag3, category1, category2, category3)

        longClickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(type1)
        clickOnViewWithText(R.string.change_record_save)
        checkTagNotVisible(tag1, tag2, tag3, category1, category2, category3)

        longClickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(type1)
        clickOnViewWithText(type2)
        clickOnViewWithText(R.string.change_record_save)
        checkTagVisible(tag2, category2)
        checkTagNotVisible(tag1, tag3, category1, category3)

        longClickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(type2)
        clickOnViewWithText(type3)
        clickOnViewWithText(R.string.change_record_save)
        checkTagVisible(tag3, category3)
        checkTagNotVisible(tag1, tag2, category1, category2)

        longClickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(type2)
        clickOnViewWithText(R.string.change_record_save)
        checkTagVisible(tag2, tag3, category2, category3)
        checkTagNotVisible(tag1, category1)

        longClickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(type2)
        clickOnViewWithText(type3)
        clickOnViewWithText(R.string.change_record_save)
        checkTagVisible(tag1, tag2, tag3, category1, category2, category3)
    }

    @Test
    fun search() {
        val tag1 = "tag1"
        val tag2 = "tag2 test2"
        val tag3 = "tag3 test3"
        val category1 = "category1"
        val category2 = "category2 test2"
        val category3 = "category3 test3"

        // Add data
        testUtils.addCategory(category1)
        testUtils.addCategory(category2)
        testUtils.addCategory(category3)
        testUtils.addRecordTag(tag1)
        testUtils.addRecordTag(tag2)
        testUtils.addRecordTag(tag3)

        // Check
        NavUtils.openSettingsScreen()
        NavUtils.openCategoriesScreen()
        checkTagVisible(tag1, tag2, tag3, category1, category2, category3)

        // Search
        clickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(R.string.enable_search_hint)

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, tag1)
        tryAction {
            checkTagVisible(tag1)
            checkTagNotVisible(tag2, tag3, category1, category2, category3)
        }

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, tag2)
        tryAction {
            checkTagVisible(tag2)
            checkTagNotVisible(tag1, tag3, category1, category2, category3)
        }

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, category1)
        tryAction {
            checkTagVisible(category1)
            checkTagNotVisible(tag1, tag2, tag3, category2, category3)
        }

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, category2)
        tryAction {
            checkTagVisible(category2)
            checkTagNotVisible(tag1, tag2, tag3, category1, category3)
        }

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, "1")
        tryAction {
            checkTagVisible(tag1, category1)
            checkTagNotVisible(tag2, tag3, category2, category3)
        }

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, "test2")
        tryAction {
            checkTagVisible(tag2, category2)
            checkTagNotVisible(tag1, tag3, category1, category3)
        }

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, "test")
        tryAction {
            checkTagVisible(tag2, tag3, category2, category3)
            checkTagNotVisible(tag1, category1)
        }

        typeTextIntoView(categoriesR.id.etCategoriesSearchField, "something")
        tryAction {
            checkTagNotVisible(tag1, tag2, tag3, category1, category2, category3)
        }

        // Disable
        clickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(R.string.enable_search_hint)
        tryAction {
            checkViewIsNotDisplayed(withId(categoriesR.id.etCategoriesSearchField))
            checkTagVisible(tag1, tag2, tag3, category1, category2, category3)
        }
    }

    @Test
    fun showRelations() {
        val category1 = "category1"
        val category2 = "category2"
        val category3 = "category3"
        val tag1 = "tag1"
        val tag2 = "tag2"
        val tag3 = "tag3"
        val type1 = "type1"
        val type2 = "type2"
        val type3 = "type3"
        val type4 = "type4"

        fun getRecordsCount(count: Int): String {
            return getString(
                R.string.separator_template,
                getString(R.string.archive_tagged_records_count),
                count,
            )
        }

        // Add data
        testUtils.addCategory(category1)
        testUtils.addCategory(category2)
        testUtils.addCategory(category3)
        testUtils.addActivity(type1, categories = listOf(category1))
        testUtils.addActivity(type2, categories = listOf(category1))
        testUtils.addActivity(type3)
        testUtils.addActivity(type4, categories = listOf(category2))
        testUtils.addRecordTag(tag1, typeName = type2, defaultTypes = listOf(type3))
        testUtils.addRecordTag(tag2, typeName = type4)
        testUtils.addRecordTag(tag3)
        repeat(2) { testUtils.addRecord(type2, tagNames = listOf(tag1)) }
        repeat(4) { testUtils.addRecord(type4, tagNames = listOf(tag2)) }
        val categoriesMap = runBlocking { testUtils.categoryInteractor.getAll().associate { it.name to it.id } }
        val tagsMap = runBlocking { testUtils.recordTagInteractor.getAll().associate { it.name to it.id } }

        // Enable relations
        NavUtils.openSettingsScreen()
        NavUtils.openCategoriesScreen()
        clickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(R.string.categories_show_relations)
        Thread.sleep(1000)

        // Check
        checkTagVisible(category1)
        checkRelation(
            relationNames = listOf(type1, type2),
            parentName = category1,
            nameToIdMap = categoriesMap,
        )
        checkTagVisible(category2)
        checkRelation(
            relationNames = listOf(type4),
            parentName = category2,
            nameToIdMap = categoriesMap,
        )
        checkTagVisible(category3)
        checkRelation(
            relationNames = listOf(getString(R.string.record_types_empty)),
            parentName = category3,
            nameToIdMap = categoriesMap,
        )
        checkTagVisible(tag1)
        checkRelation(
            relationNames = listOf(type2, getString(R.string.change_record_tag_default_hint), type3, getRecordsCount(2)),
            parentName = tag1,
            nameToIdMap = tagsMap,
        )
        checkTagVisible(tag2)
        checkRelation(
            relationNames = listOf(type4, getRecordsCount(4)),
            parentName = tag2,
            nameToIdMap = tagsMap,
        )
        checkTagVisible(tag3)
        checkRelation(
            relationNames = listOf(getString(R.string.change_record_tag_type_general), getRecordsCount(0)),
            parentName = tag3,
            nameToIdMap = tagsMap,
        )

        // Persistence
        pressBack()
        NavUtils.openRecordsScreen()
        NavUtils.openSettingsScreen()
        NavUtils.openCategoriesScreen()
        checkTagVisible(category1)
        checkRelation(
            relationNames = listOf(type1, type2),
            parentName = category1,
            nameToIdMap = categoriesMap,
        )

        // Search
        clickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(R.string.enable_search_hint)
        typeTextIntoView(categoriesR.id.etCategoriesSearchField, type3)
        tryAction {
            checkTagVisible(tag1)
            checkTagNotVisible(category1, category2, tag2)
            checkRelationVisible(type2, type3)
            checkRelationNotVisible(type1, type4)
        }

        // Filter
        typeTextIntoView(categoriesR.id.etCategoriesSearchField, "")
        longClickOnViewWithId(categoriesR.id.btnCategoriesOptions)
        clickOnViewWithText(type2)
        clickOnViewWithText(R.string.change_record_save)
        tryAction {
            checkTagVisible(category1)
            checkRelation(
                relationNames = listOf(type1, type2),
                parentName = category1,
                nameToIdMap = categoriesMap,
            )
            checkTagVisible(tag1)
            checkRelation(
                relationNames = listOf(type2, getString(R.string.change_record_tag_default_hint), type3),
                parentName = tag1,
                nameToIdMap = tagsMap,
            )
            checkTagNotVisible(category2, tag2)
        }
    }

    private fun checkTagVisible(vararg name: String) {
        name.forEach {
            scrollRecyclerToView(
                R.id.rvCategoriesList,
                hasDescendant(withText(it)),
            )
            checkViewIsDisplayed(
                allOf(
                    withId(dialogsR.id.viewCategoryItem),
                    hasDescendant(withText(it)),
                    isCompletelyDisplayed(),
                ),
            )
        }
    }

    private fun checkTagNotVisible(vararg name: String) {
        name.forEach {
            checkViewDoesNotExist(
                allOf(
                    withId(dialogsR.id.viewCategoryItem),
                    hasDescendant(withText(it)),
                    isCompletelyDisplayed(),
                ),
            )
        }
    }

    private fun checkRelation(
        relationNames: List<String>,
        parentName: String,
        nameToIdMap: Map<String, Long>,
    ) {
        val tag = nameToIdMap[parentName]
        val parentMatcher = allOf(
            withId(R.id.viewCategoryItem),
            hasDescendant(withText(parentName)),
        )
        relationNames.forEach { relationName ->
            val matcher = suggestionMatcher(withText(relationName), tag)
            scrollRecyclerToView(R.id.rvCategoriesList, matcher)
            checkViewIsDisplayed(matcher)
            onView(matcher).check(isCompletelyBelow(parentMatcher))
        }
    }

    @Suppress("SameParameterValue")
    private fun checkRelationVisible(vararg name: String) {
        name.forEach {
            checkViewIsDisplayed(
                allOf(
                    withId(R.id.cvActivitySuggestionListItemContent),
                    hasDescendant(withText(it)),
                    isCompletelyDisplayed(),
                ),
            )
        }
    }

    @Suppress("SameParameterValue")
    private fun checkRelationNotVisible(vararg name: String) {
        name.forEach {
            checkViewDoesNotExist(
                allOf(
                    withId(R.id.cvActivitySuggestionListItemContent),
                    hasDescendant(withText(it)),
                    isCompletelyDisplayed(),
                ),
            )
        }
    }
}
