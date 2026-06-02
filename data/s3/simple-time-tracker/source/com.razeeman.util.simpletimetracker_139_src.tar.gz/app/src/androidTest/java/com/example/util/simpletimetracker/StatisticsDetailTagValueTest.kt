package com.example.util.simpletimetracker

import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.isDescendantOfA
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.espresso.Espresso.pressBack
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.util.simpletimetracker.domain.statistics.model.ChartFilterType
import com.example.util.simpletimetracker.feature_statistics_detail.adapter.StatisticsDetailBlock
import com.example.util.simpletimetracker.utils.BaseUiTest
import com.example.util.simpletimetracker.utils.NavUtils
import com.example.util.simpletimetracker.utils.checkViewIsDisplayed
import com.example.util.simpletimetracker.utils.clickOnCurrentDate
import com.example.util.simpletimetracker.utils.clickOnView
import com.example.util.simpletimetracker.utils.clickOnViewWithText
import com.example.util.simpletimetracker.utils.tryAction
import com.example.util.simpletimetracker.utils.withTag
import dagger.hilt.android.testing.HiltAndroidTest
import kotlinx.coroutines.runBlocking
import org.hamcrest.CoreMatchers.allOf
import org.junit.Test
import org.junit.runner.RunWith
import java.util.Calendar
import java.util.concurrent.TimeUnit
import com.example.util.simpletimetracker.core.R as coreR

@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class StatisticsDetailTagValueTest : BaseUiTest() {

    @Test
    fun statistics() {
        val name = "TypeName"
        val tag = "TagName"

        // Add activity
        testUtils.addActivity(name)
        testUtils.addRecordTag(tag, name, hasTagValue = true)
        runBlocking { prefsInteractor.setChartFilterType(ChartFilterType.RECORD_TAG) }

        // Add records
        var calendar = Calendar.getInstance()
            .apply { set(Calendar.HOUR_OF_DAY, 15) }
        testUtils.addRecord(
            typeName = name,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(1),
            tagNamesWithValues = listOf(tag to 1.5),
        )
        testUtils.addRecord(
            typeName = name,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(2),
            tagNamesWithValues = listOf(tag to -0.5),
        )
        calendar = Calendar.getInstance()
            .apply { add(Calendar.YEAR, -10) }
        testUtils.addRecord(
            typeName = name,
            timeStarted = calendar.timeInMillis,
            timeEnded = calendar.timeInMillis + TimeUnit.HOURS.toMillis(3),
            tagNamesWithValues = listOf(tag to -0.5),
        )

        // Check detailed statistics
        NavUtils.openStatisticsScreen()
        tryAction { clickOnView(allOf(withText(tag), isCompletelyDisplayed())) }
        clickOnCurrentDate()
        clickOnViewWithText(coreR.string.range_overall)

        // Bar chart
        scrollStatDetailRecyclerToTag(StatisticsDetailBlock.TagValuesChartData)
        checkViewIsDisplayed(
            allOf(withTag(StatisticsDetailBlock.TagValuesChartData), isCompletelyDisplayed()),
        )

        // By totals
        clickOnChartGrouping(coreR.string.statistics_detail_chart_daily)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.1", "1")
        checkTotals("1", "1", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.02", "1")
        checkTotals("1", "1", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.01", "1")
        checkTotals("1", "1", "1")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_weekly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_weekly, "0.1", "1")
        checkTotals("1", "1", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_weekly, "0.02", "1")
        checkTotals("1", "1", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_weekly, "0.01", "1")
        checkTotals("1", "1", "1")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_monthly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_monthly, "0.1", "1")
        checkTotals("1", "1", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_monthly, "0.02", "1")
        checkTotals("1", "1", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_monthly, "0.01", "1")
        checkTotals("1", "1", "1")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_yearly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0.1", "1")
        checkTotals("1", "1", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0.01", "0.25")
        checkTotals("-0.5", "0.5", "1")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0.005", "0.25")
        checkTotals("-0.5", "0.5", "1")

        // By average
        clickOnChartMode(R.string.statistics_detail_average_record)
        clickOnChartGrouping(coreR.string.statistics_detail_chart_daily)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.05", "0.5")
        checkTotals("0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.01", "0.5")
        checkTotals("0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.005", "0.5")
        checkTotals("0.5", null, "0.5")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_weekly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_weekly, "0.05", "0.5")
        checkTotals("0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_weekly, "0.01", "0.5")
        checkTotals("0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_weekly, "0.005", "0.5")
        checkTotals("0.5", null, "0.5")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_monthly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_monthly, "0.05", "0.5")
        checkTotals("0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_monthly, "0.01", "0.5")
        checkTotals("0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_monthly, "0.005", "0.5")
        checkTotals("0.5", null, "0.5")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_yearly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0.05", "0.5")
        checkTotals("0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0", "0")
        checkTotals("-0.5", null, "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0", "0")
        checkTotals("-0.5", null, "0.5")

        // Multiply by duration, total
        clickOnChartMode(R.string.statistics_detail_total_duration)
        clickOnMultiplyDuration(R.string.statistics_detail_tag_values_multiply_duration)
        clickOnChartGrouping(coreR.string.statistics_detail_chart_daily)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.05", "0.5")
        checkTotals("0.5", "0.5", "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.01", "0.5")
        checkTotals("0.5", "0.5", "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.005", "0.5")
        checkTotals("0.5", "0.5", "0.5")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_yearly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0.05", "0.5")
        checkTotals("0.5", "0.5", "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "-0.02", "-0.5")
        checkTotals("-1.5", "-1", "0.5")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "-0.01", "-0.5")
        checkTotals("-1.5", "-1", "0.5")

        // Multiply by duration, average
        clickOnChartMode(R.string.statistics_detail_average_record)
        clickOnChartGrouping(coreR.string.statistics_detail_chart_daily)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.025", "0.25")
        checkTotals("0.25", null, "0.25")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.005", "0.25")
        checkTotals("0.25", null, "0.25")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_daily, "0.002", "0.25")
        checkTotals("0.25", null, "0.25")

        clickOnChartGrouping(coreR.string.statistics_detail_chart_yearly)
        clickOnChartLength(coreR.string.statistics_detail_length_ten)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "0.025", "0.25")
        checkTotals("0.25", null, "0.25")
        clickOnChartLength(coreR.string.statistics_detail_length_fifty)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "-0.025", "-0.625")
        checkTotals("-1.5", null, "0.25")
        clickOnChartLength(coreR.string.statistics_detail_length_hundred)
        checkRangeAverages(coreR.string.statistics_detail_chart_yearly, "-0.013", "-0.625")
        checkTotals("-1.5", null, "0.25")
    }

    private fun clickOnChartGrouping(withTextId: Int) {
        scrollStatDetailRecyclerToTag(StatisticsDetailBlock.TagValuesChartGrouping)
        clickOnView(
            allOf(
                isDescendantOfA(withTag(StatisticsDetailBlock.TagValuesChartGrouping)),
                withText(withTextId),
            ),
        )
    }

    private fun clickOnChartLength(withTextId: Int) {
        scrollStatDetailRecyclerToTag(StatisticsDetailBlock.TagValuesChartLength)
        clickOnView(
            allOf(
                isDescendantOfA(withTag(StatisticsDetailBlock.TagValuesChartLength)),
                withText(withTextId),
            ),
        )
    }

    private fun clickOnChartMode(withTextId: Int) {
        clickOnTagValuesSettings()
        try {
            checkViewIsDisplayed(withText(withTextId))
        } catch (_: Exception) {
            clickOnSettingsSelectorBesideText(R.string.statistics_detail_tag_values_hint)
        }
        pressBack()
    }

    @Suppress("SameParameterValue")
    private fun clickOnMultiplyDuration(withTextId: Int) {
        clickOnTagValuesSettings()
        clickOnSettingsCheckboxBesideText(withTextId)
        pressBack()
    }

    private fun clickOnTagValuesSettings() {
        scrollStatDetailRecyclerToTag(StatisticsDetailBlock.TagValuesSettings)
        clickOnView(
            allOf(
                isDescendantOfA(withTag(StatisticsDetailBlock.TagValuesSettings)),
                withText(R.string.shortcut_navigation_settings),
            ),
        )
    }

    private fun BaseUiTest.checkRangeAverages(
        rangeId: Int,
        average: String = "",
        averageNonEmpty: String,
    ) {
        checkRangeAverages(
            block = StatisticsDetailBlock.TagValuesRangeAverages,
            rangeId = rangeId,
            average = average,
            averageNonEmpty = averageNonEmpty,
        )
    }

    private fun checkTotals(
        min: String,
        total: String?,
        max: String,
    ) {
        scrollStatDetailRecyclerToTag(StatisticsDetailBlock.TagValuesTotals)
        checkCard(coreR.string.records_filter_duration_min, min)
        total?.let { checkCard(coreR.string.statistics_detail_total_duration, total) }
        checkCard(coreR.string.records_filter_duration_max, max)
    }
}
