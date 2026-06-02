package com.example.util.simpletimetracker.utils

import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.TextView
import androidx.annotation.ColorInt
import androidx.annotation.PluralsRes
import androidx.cardview.widget.CardView
import androidx.core.content.ContextCompat
import androidx.test.espresso.Root
import androidx.test.espresso.matcher.BoundedMatcher
import androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withTagValue
import com.example.util.simpletimetracker.R
import com.example.util.simpletimetracker.feature_base_adapter.InfiniteRecyclerAdapter
import com.google.android.material.button.MaterialButton
import com.google.android.material.slider.Slider
import org.hamcrest.CoreMatchers.allOf
import org.hamcrest.CoreMatchers.equalTo
import org.hamcrest.Description
import org.hamcrest.Matcher
import org.hamcrest.TypeSafeMatcher
import kotlin.math.roundToInt

fun withCardColor(expectedId: Int): Matcher<View> =
    object : BoundedMatcher<View, CardView>(CardView::class.java) {
        override fun matchesSafely(view: CardView): Boolean {
            val colorInt: Int = ContextCompat.getColor(view.context, expectedId)
            return view.cardBackgroundColor.defaultColor == colorInt
        }

        override fun describeTo(description: Description) {
            description.appendText("with card color: ")
            description.appendValue(expectedId)
        }
    }

fun withCardColorInt(@ColorInt colorInt: Int): Matcher<View> =
    object : BoundedMatcher<View, CardView>(CardView::class.java) {
        override fun matchesSafely(view: CardView): Boolean {
            return view.cardBackgroundColor.defaultColor == colorInt
        }

        override fun describeTo(description: Description) {
            description.appendText("with card color int: ")
            description.appendValue(colorInt)
        }
    }

// TODO doesn't work.
fun withButtonColor(expectedId: Int): Matcher<View> =
    object : BoundedMatcher<View, MaterialButton>(MaterialButton::class.java) {
        override fun matchesSafely(view: MaterialButton): Boolean {
            val colorInt: Int = ContextCompat.getColor(view.context, expectedId)
            return view.backgroundTintList?.defaultColor == colorInt
        }

        override fun describeTo(description: Description) {
            description.appendText("with button color: ")
            description.appendValue(expectedId)
        }
    }

fun withTag(tagValueMatcher: Any?): Matcher<View> =
    withTagValue(equalTo(tagValueMatcher))

fun withNullTag(): Matcher<View> {
    return object : TypeSafeMatcher<View>() {
        override fun matchesSafely(view: View?): Boolean {
            return view?.tag == null
        }

        override fun describeTo(description: Description) {
            description.appendText("view with null tag")
        }
    }
}

fun isToast(): Matcher<Root> {
    return object : TypeSafeMatcher<Root>() {
        override fun matchesSafely(item: Root): Boolean {
            val type: Int = item.windowLayoutParams.get().type
            return type == WindowManager.LayoutParams.TYPE_TOAST
        }

        override fun describeTo(description: Description) {
            description.appendText("is toast")
        }
    }
}

fun withPluralText(@PluralsRes expectedId: Int, quantity: Int, vararg: Any? = null): Matcher<View> =
    object : BoundedMatcher<View, TextView>(TextView::class.java) {
        override fun matchesSafely(view: TextView): Boolean {
            val text: String = view.context.resources.getQuantityString(expectedId, quantity, vararg)
            return view.text == text
        }

        override fun describeTo(description: Description) {
            description.appendText("with plural text: ")
            description.appendValue(expectedId)
            description.appendText(" and quantity: ")
            description.appendValue(quantity)
        }
    }

fun withSliderValue(expectedValue: Int): Matcher<View> =
    object : BoundedMatcher<View, Slider>(Slider::class.java) {
        override fun matchesSafely(slider: Slider): Boolean {
            return slider.value.roundToInt() == expectedValue
        }

        override fun describeTo(description: Description) {
            description.appendText("expected: $expectedValue")
        }
    }

fun nthChildOf(parentMatcher: Matcher<View?>, childPosition: Int): Matcher<View> {
    return object : TypeSafeMatcher<View>() {
        override fun describeTo(description: Description) {
            description.appendText("with $childPosition child view of type parentMatcher")
        }

        override fun matchesSafely(view: View): Boolean {
            if (view.parent !is ViewGroup) {
                return parentMatcher.matches(view.parent)
            }
            val group: ViewGroup = view.parent as ViewGroup
            return parentMatcher.matches(view.parent) && group.getChildAt(childPosition).equals(view)
        }
    }
}

fun dateSelectorMatcher(position: Int): Matcher<View> {
    return allOf(
        isCompletelyDisplayed(),
        withTag(InfiniteRecyclerAdapter.TEST_TAG + position),
    )
}

fun selectedDateMatcher(): Matcher<View> {
    return allOf(
        isCompletelyDisplayed(),
        withId(R.id.viewDateSelectorBackgroundSelected),
    )
}