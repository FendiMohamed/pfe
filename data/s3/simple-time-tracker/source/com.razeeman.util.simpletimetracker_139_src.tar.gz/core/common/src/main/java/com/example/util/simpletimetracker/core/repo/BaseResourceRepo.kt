package com.example.util.simpletimetracker.core.repo

import androidx.annotation.PluralsRes
import androidx.annotation.StringRes

// TODO remove, move ResourceRepo here
interface BaseResourceRepo {

    fun getString(@StringRes stringResId: Int): String

    fun getString(@StringRes stringResId: Int, vararg args: Any): String

    fun getQuantityString(@PluralsRes stringResId: Int, quantity: Int): String

    fun getQuantityString(@PluralsRes stringResId: Int, quantity: Int, vararg args: Any): String
}