package com.example.util.simpletimetracker.navigation

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.os.Build
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts.RequestPermission
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import com.example.util.simpletimetracker.core.extension.allowDiskRead
import com.example.util.simpletimetracker.core.provider.ApplicationDataProvider
import com.example.util.simpletimetracker.navigation.params.action.ActionParams
import com.example.util.simpletimetracker.navigation.params.action.CreateFileParams
import com.example.util.simpletimetracker.navigation.params.action.OpenFileParams
import com.example.util.simpletimetracker.navigation.params.action.OpenLinkParams
import com.example.util.simpletimetracker.navigation.params.action.OpenMarketParams
import com.example.util.simpletimetracker.navigation.params.action.OpenSystemSettings
import com.example.util.simpletimetracker.navigation.params.action.RequestPermissionParams
import com.example.util.simpletimetracker.navigation.params.action.SendEmailParams
import com.example.util.simpletimetracker.navigation.params.action.ShareFileParams
import timber.log.Timber
import javax.inject.Inject
import androidx.core.net.toUri

class ActionResolverImpl @Inject constructor(
    private val resultContainer: ResultContainer,
    private val applicationDataProvider: ApplicationDataProvider,
) : ActionResolver {

    private var createFileResultLauncher: ActivityResultLauncher<Intent>? = null
    private var openFileResultLauncher: ActivityResultLauncher<Intent>? = null
    private var requestPermissionLauncher: ActivityResultLauncher<String>? = null

    override fun registerResultListeners(activity: ComponentActivity) {
        createFileResultLauncher = activity.registerForActivityResult(RequestCode.REQUEST_CODE_CREATE_FILE)
        openFileResultLauncher = activity.registerForActivityResult(RequestCode.REQUEST_CODE_OPEN_FILE)
        requestPermissionLauncher = activity.registerForRequestPermission(RequestCode.REQUEST_PERMISSION)
    }

    override fun execute(activity: Activity?, data: ActionParams) {
        when (data) {
            is OpenMarketParams -> openMarket(activity, data)
            is SendEmailParams -> sendEmail(activity, data)
            is CreateFileParams -> createFile(data)
            is OpenFileParams -> openFile(data)
            is OpenSystemSettings -> openSystemSettings(activity, data)
            is ShareFileParams -> shareFile(activity, data)
            is RequestPermissionParams -> requestPermission(data)
            is OpenLinkParams -> openLink(activity, data)
        }
    }

    private fun openMarket(activity: Activity?, params: OpenMarketParams) {
        val uri = (MARKET_INTENT + params.packageName).toUri()
        val intent = Intent(Intent.ACTION_VIEW, uri)
        intent.setPackage(MARKET_PACKAGE)
        intent.addFlags(Intent.FLAG_ACTIVITY_NO_HISTORY)

        try {
            activity?.startActivity(intent)
        } catch (_: ActivityNotFoundException) {
            Intent(
                Intent.ACTION_VIEW,
                (MARKET_LINK + params.packageName).toUri(),
            ).apply {
                intent.setPackage(MARKET_PACKAGE)
            }.let {
                activity?.startActivity(it)
            }
        }
    }

    private fun openLink(activity: Activity?, params: OpenLinkParams) {
        activity?.startActivity(
            Intent(
                Intent.ACTION_VIEW,
                params.link.toUri(),
            ),
        )
    }

    private fun sendEmail(activity: Activity?, params: SendEmailParams) {
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = EMAIL_URI.toUri()
            params.email?.let { putExtra(Intent.EXTRA_EMAIL, arrayOf(it)) }
            params.subject?.let { putExtra(Intent.EXTRA_SUBJECT, it) }
            params.body?.let { putExtra(Intent.EXTRA_TEXT, it) }
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }

        try {
            activity?.startActivity(Intent.createChooser(intent, params.chooserTitle))
        } catch (_: ActivityNotFoundException) {
            params.notHandledCallback?.invoke()
        }
    }

    private fun openFile(data: OpenFileParams) {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            .addCategory(Intent.CATEGORY_OPENABLE)
            .setType(data.type)

        runCatching {
            openFileResultLauncher?.launch(intent)
        }.onFailure {
            Timber.e(it)
            data.notHandledCallback()
        }
    }

    private fun createFile(data: CreateFileParams) {
        val intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
            .addCategory(Intent.CATEGORY_OPENABLE)
            .setType(data.type)
            .putExtra(Intent.EXTRA_TITLE, data.fileName)

        runCatching {
            createFileResultLauncher?.launch(intent)
        }.onFailure {
            Timber.e(it)
            data.notHandledCallback()
        }
    }

    private fun openSystemSettings(activity: Activity?, data: OpenSystemSettings) {
        val packageName by lazy { applicationDataProvider.getPackageName() }
        val intent = Intent()

        when (data) {
            is OpenSystemSettings.ExactAlarms -> runCatching {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    intent.action = Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM
                    intent.data = "package:$packageName".toUri()
                }
            }

            is OpenSystemSettings.Notifications -> runCatching {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    intent.action = Settings.ACTION_APP_NOTIFICATION_SETTINGS
                    intent.putExtra(Settings.EXTRA_APP_PACKAGE, packageName)
                } else {
                    intent.action = Settings.ACTION_APPLICATION_DETAILS_SETTINGS
                    intent.data = "package:$packageName".toUri()
                }
            }
        }

        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        runCatching { activity?.startActivity(intent) }
    }

    private fun shareFile(activity: Activity?, data: ShareFileParams) {
        try {
            val uri = data.uriString.toUri()
            val type = allowDiskRead { data.type ?: activity?.contentResolver?.getType(uri) }
            val intent = Intent(Intent.ACTION_SEND).apply {
                setDataAndType(uri, type)
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            activity?.startActivity(Intent.createChooser(intent, null))
        } catch (_: ActivityNotFoundException) {
            data.notHandledCallback.invoke()
        }
    }

    private fun requestPermission(data: RequestPermissionParams) {
        requestPermissionLauncher?.launch(data.permissionId)
    }

    private fun ComponentActivity.registerForActivityResult(key: String): ActivityResultLauncher<Intent> {
        return registerForActivityResult(StartActivityForResult()) { result ->
            val intent = result.data
            val uri = intent?.data?.toString().takeIf { result.resultCode == Activity.RESULT_OK }

            resultContainer.sendResult(key, uri)
        }
    }

    private fun ComponentActivity.registerForRequestPermission(key: String): ActivityResultLauncher<String> {
        return registerForActivityResult(RequestPermission()) { result ->
            resultContainer.sendResult(key, result)
        }
    }

    companion object {
        private const val MARKET_INTENT = "market://details?id="
        private const val MARKET_LINK = "http://play.google.com/store/apps/details?id="
        private const val MARKET_PACKAGE = "com.android.vending"
        private const val EMAIL_URI = "mailto:"
    }
}