plugins {
    alias(libs.plugins.gradleApplication) apply false
    alias(libs.plugins.gradleLibrary) apply false
    alias(libs.plugins.kotlin) apply false
    alias(libs.plugins.kotlinParcelize) apply false
    alias(libs.plugins.kotlinLibrary) apply false
    alias(libs.plugins.ktlint) apply false
    alias(libs.plugins.hilt) apply false
    alias(libs.plugins.ksp) apply false
    alias(libs.plugins.room) apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }

    apply(plugin = rootProject.libs.plugins.ktlint.get().pluginId)
}

tasks {
    val clean by registering(Delete::class) {
        delete(buildDir)
    }
}
