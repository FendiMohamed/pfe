import com.example.util.simpletimetracker.Base
import com.example.util.simpletimetracker.applyAndroidLibrary

plugins {
    alias(libs.plugins.gradleLibrary)
    alias(libs.plugins.kotlin)
    alias(libs.plugins.kotlinParcelize)
}

applyAndroidLibrary()

android {
    namespace = "${Base.namespace}.core.common"
}

dependencies {
    api(project(":domain:common"))
    implementation(project(":resources"))

    implementation(libs.google.dagger)
}
