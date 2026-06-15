package com.example.util.simpletimetracker

import android.view.View
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.assertion.PositionAssertions.isCompletelyBelow
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import com.example.util.simpletimetracker.utils.checkViewDoesNotExist
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.scrollRecyclerToView
import com.example.util.simpletimetracker.utils.withTag
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.Matcher

object SuggestionsTestUtils {

    fun checkType(
        name: String,
        visible: Boolean,
    ) {
        val matcher = suggestionTypeMatcher(name)
        if (visible) {
            scrollRecyclerToView(R.id.rvActivitySuggestionsList, matcher)
            checkViewIsDisplayed(matcher)
        } else {
            checkViewDoesNotExist(matcher)
        }
    }

    fun checkSuggestion(
        forType: String,
        textMatcher: Matcher<View>,
        tag: Any?,
        visible: Boolean,
    ): Matcher<View> {
        val typeMatcher = suggestionTypeMatcher(forType)
        val matcher = suggestionMatcher(textMatcher, tag)
        if (visible) {
            scrollRecyclerToView(R.id.rvActivitySuggestionsList, matcher)
            checkViewIsDisplayed(matcher)
            onView(matcher).check(isCompletelyBelow(typeMatcher))
        } else {
            checkViewDoesNotExist(matcher)
        }
        return matcher
    }

    private fun suggestionTypeMatcher(name: String): Matcher<View> {
        return allOf(
            withId(R.id.viewRecordTypeItem),
            hasDescendant(withText(name)),
        )
    }

    fun suggestionMatcher(
        textMatcher: Matcher<View>,
        tag: Any?,
    ): Matcher<View> {
        return allOf(
            withId(R.id.cvActivitySuggestionListItemContent),
            withTag(tag ?: Any()),
            hasDescendant(textMatcher),
        )
    }
}
