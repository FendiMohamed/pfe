package com.example.util.simpletimetracker

import android.view.View
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.contrib.RecyclerViewActions.scrollTo
import androidx.test.espresso.matcher.ViewMatchers.hasDescendant
import androidx.test.espresso.matcher.ViewMatchers.hasSibling
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.isDescendantOfA
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import com.example.util.simpletimetracker.core.R
import com.example.util.simpletimetracker.feature_base_adapter.BaseRecyclerViewHolder
import com.example.util.simpletimetracker.feature_statistics_detail.adapter.StatisticsDetailBlock
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.collapseToolbar
import com.example.util.simpletimetracker.utils.withTag
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.Matcher
import com.example.util.simpletimetracker.feature_statistics_detail.R as statDetailR

// Scroll

fun scrollStatDetailRecyclerToTag(tag: Any) {
    scrollStatDetailRecyclerToView(withTag(tag))
}

fun scrollStatDetailRecycler(matcher: Matcher<View>) {
    scrollStatDetailRecyclerToView(matcher)
}

// Click

fun clickOnStatDetailRecycler(matcher: Matcher<View>) {
    clickOnStatDetailRecyclerItem(matcher)
}

// Custom

fun BaseUiTest.checkRangeAverages(
    block: StatisticsDetailBlock,
    rangeId: Int,
    average: String = "",
    checkAverage: Boolean = true,
    averageNonEmpty: String,
) {
    val range = getString(rangeId)
    val title = getString(R.string.statistics_detail_range_averages_title, range)

    scrollStatDetailRecyclerToTag(block)
    checkViewIsDisplayed(
        allOf(
            withTag(block),
            hasDescendant(withText(title)),
            if (checkAverage) {
                hasDescendant(
                    allOf(
                        withText(R.string.statistics_detail_range_averages),
                        hasSibling(withText(average)),
                    ),
                )
            } else {
                hasDescendant(withText(title))
            },
            hasDescendant(
                allOf(
                    withText(R.string.statistics_detail_range_averages_non_empty),
                    hasSibling(withText(averageNonEmpty)),
                ),
            ),
            isCompletelyDisplayed(),
        ),
    )
}

fun checkCard(cardTitleId: Int, text: String) {
    checkViewIsDisplayed(
        allOf(
            withText(cardTitleId),
            hasSibling(withText(text)),
            isCompletelyDisplayed(),
        ),
    )
}

// Private

private fun scrollStatDetailRecyclerToView(matcher: Matcher<View>) {
    onView(withId(statDetailR.id.rvStatisticsDetailContent))
        .perform(collapseToolbar())
    onView(withId(statDetailR.id.rvStatisticsDetailContent))
        .perform(scrollTo<BaseRecyclerViewHolder>(matcher))
}

private fun clickOnStatDetailRecyclerItem(matcher: Matcher<View>) {
    clickOnView(allOf(isDescendantOfA(withId(statDetailR.id.rvStatisticsDetailContent)), matcher))
}
